# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import functools
import hashlib
import json
import logging
import uuid
from collections import Counter
from collections.abc import Generator, Iterator
from typing import Any, cast

import attrs
import cloudpickle
import lance
import pyarrow as pa
import ray.actor
import ray.exceptions
import ray.util.queue
from ray import ObjectRef
from tqdm.std import tqdm as TqdmType  # noqa: N812

from geneva.apply import (
    CheckpointingApplier,
    plan_copy,
    plan_read,
)
from geneva.apply.applier import BatchApplier
from geneva.apply.multiprocess import MultiProcessBatchApplier
from geneva.apply.simple import SimpleApplier
from geneva.apply.task import BackfillUDFTask, CopyTableTask, MapTask, ReadTask
from geneva.checkpoint import CheckpointStore
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.job.config import JobConfig
from geneva.packager import UDFPackager
from geneva.query import (
    MATVIEW_META_BASE_DBURI,
    MATVIEW_META_BASE_TABLE,
    MATVIEW_META_BASE_VERSION,
    MATVIEW_META_QUERY,
    GenevaQuery,
    GenevaQueryBuilder,
)
from geneva.runners.ray.actor_pool import ActorPool
from geneva.runners.ray.kuberay import _ray_job_status
from geneva.runners.ray.raycluster import CPU_ONLY_NODE, ProgressTracker, ray_tqdm
from geneva.runners.ray.writer import FragmentWriter
from geneva.table import JobFuture, Table, TableReference
from geneva.tqdm import tqdm
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


@ray.remote
@attrs.define
class ApplierActor:
    applier: CheckpointingApplier

    def __ray_ready__(self) -> None:
        pass

    def run(self, task) -> tuple[ReadTask, str]:
        return task, self.applier.run(task)


ApplierActor: ray.actor.ActorClass = cast("ray.actor.ActorClass", ApplierActor)


def _get_fragment_dedupe_key(uri: str, frag_id: int, map_task: MapTask) -> str:
    key = f"{uri}:{frag_id}:{map_task.checkpoint_key()}"
    return hashlib.sha256(key.encode()).hexdigest()


def _run_column_adding_pipeline(
    map_task: MapTask,
    checkpoint_store: CheckpointStore,
    config: JobConfig,
    dst: TableReference,
    input_plan: Iterator[ReadTask],
    job_id: str | None,
    applier_concurrency: int = 8,
    *,
    intra_applier_concurrency: int = 1,
    batch_applier: BatchApplier | None = None,
    use_cpu_only_pool: bool = False,
    fragment_tracker=None,
    writer_tracker=None,
    worker_tracker=None,
    where=None,
) -> None:
    """
    Run the column adding pipeline.

    Args:
    * use_cpu_only_pool: If True will force schedule cpu-only actors on cpu-only nodes.

    """
    job_id = job_id or uuid.uuid4().hex
    job = ColumnAddPipelineJob(
        map_task=map_task,
        checkpoint_store=checkpoint_store,
        config=config,
        dst=dst,
        input_plan=input_plan,
        job_id=job_id,
        applier_concurrency=applier_concurrency,
        intra_applier_concurrency=intra_applier_concurrency,
        use_cpu_only_pool=use_cpu_only_pool,
        fragment_tracker=fragment_tracker,
        writer_tracker=writer_tracker,
        worker_tracker=worker_tracker,
        where=where,
    )
    job.run()


@attrs.define
class ColumnAddPipelineJob:
    """ColumnAddPipeline drives batches of rows to commits in the dataset.

    ReadTasks are defined wrapped for tracking, and then dispatched for udf exeuction
    in the ActorPool.  The results are sent to the FragmentWriterManager which
    manages fragment checkpoints and incremental commits.
    """

    map_task: MapTask
    checkpoint_store: CheckpointStore
    config: JobConfig
    dst: TableReference
    input_plan: Iterator[ReadTask]
    job_id: str
    applier_concurrency: int = 8
    intra_applier_concurrency: int = 1
    use_cpu_only_pool: bool = False
    fragment_tracker: ObjectRef | None = None
    writer_tracker: ObjectRef | None = None
    worker_tracker: ObjectRef | None = None
    where: str | None = None

    def setup_inputplans(self) -> (Iterator[ReadTask], int):
        all_tasks = list(self.input_plan)
        self.fragment_tracker = self.fragment_tracker or ProgressTracker.remote()
        plan_len = len(all_tasks)
        self.fragment_tracker.set_total.remote(plan_len)
        # TODO read prefix f"[{dst.table_name} - {map_task.name()}]"

        # this reports # of batches started, not completed.
        tasks_by_frag = Counter(t.dest_frag_id() for t in all_tasks)
        return ray_tqdm(all_tasks, self.fragment_tracker), tasks_by_frag, plan_len

    def setup_actor(self) -> None:
        actor = ApplierActor

        # actor.options can only be called once, we must pass all override args
        # in one shot
        args = {
            "num_cpus": self.map_task.num_cpus() * self.intra_applier_concurrency,
        }
        if self.map_task.is_cuda():
            args["num_gpus"] = 1
        elif self.use_cpu_only_pool:
            _LOG.info("Using CPU only pool for applier, setting %s to 1", CPU_ONLY_NODE)
            args["resources"] = {CPU_ONLY_NODE: 1}
        if self.map_task.memory():
            args["memory"] = self.map_task.memory() * self.intra_applier_concurrency
        actor = actor.options(**args)
        return actor

    def setup_batchapplier(self) -> BatchApplier:
        if self.intra_applier_concurrency > 1:
            return MultiProcessBatchApplier(
                num_processes=self.intra_applier_concurrency
            )
        else:
            return SimpleApplier()

    def setup_actorpool(self) -> ActorPool:
        batch_applier = self.setup_batchapplier()

        applier = CheckpointingApplier(
            map_task=self.map_task,
            batch_applier=batch_applier,
            checkpoint_store=self.checkpoint_store,
            error_logger=CheckpointStoreErrorLogger(self.job_id, self.checkpoint_store),
        )

        actor = self.setup_actor()
        self.worker_tracker = self.worker_tracker or ProgressTracker.remote()
        self.worker_tracker.set_total.remote(self.applier_concurrency)

        pool = ActorPool(
            functools.partial(actor.remote, applier=applier),
            self.applier_concurrency,
            worker_tracker=self.worker_tracker,
        )
        return pool

    def setup_writertracker(self) -> (lance.LanceDataset, int):
        ds = self.dst.open().to_lance()
        fragments = ds.get_fragments()
        len_frags = len(fragments)
        self.writer_tracker = self.writer_tracker or ProgressTracker.remote()
        self.writer_tracker.set_total.remote(len_frags)
        ray_tqdm(fragments, self.writer_tracker)  # values update explicitly
        # TODO descriptions f"{pbar_prefix} Writing Fragments"
        return ds, len_frags

    def run(self) -> None:
        plans, tasks_by_frag, cnt_batches = self.setup_inputplans()
        pool = self.setup_actorpool()
        ds, cnt_fragments = self.setup_writertracker()

        _LOG.info(
            f"Pipeline executing on {cnt_batches} batches over "
            f"{cnt_fragments} table fragments"
        )

        # kick off the applier actors
        # TODO description f"{pbar_prefix} Applying UDFs"
        applier_iter = pool.map_unordered(
            lambda actor, value: actor.run.remote(value),
            # the API says list, but iterables are fine
            plans,
        )

        fwm = FragmentWriterManager(
            ds.version,
            ds_uri=ds.uri,
            map_task=self.map_task,
            checkpoint_store=self.checkpoint_store,
            where=self.where,
            writer_tracker=self.writer_tracker,
            commit_granularity=self.config.commit_granularity,
            expected_tasks=dict(tasks_by_frag),
        )

        for task, result in applier_iter:
            fwm.ingest(result, task)

        pool.shutdown()
        fwm.cleanup()


@attrs.define
class FragmentWriterSession:
    """This tracks all the batch tasks for a single fragment.

    It is responsible for managing the fragment writer's life cycle and does the
    bookkeeping of inflight tasks, completed tasks, and the queue of tasks to write.
    These are locally tracked and accounted for before the fragment is considered
    complete and ready to be commited to the dataset.

    It expects to be initialized and then fed with `ingest_task` calls. After all tasks
    have been added, it is `seal`ed meaning no more input tasks are expected.  Then it
    can be `drain`ed to yield all completed tasks.
    """

    frag_id: int
    ds_uri: str
    output_columns: list[str]
    checkpoint_store: CheckpointStore
    where: str | None

    # runtime state.  This is single-threaded and is not thread-safe.
    queue: ray.util.queue.Queue = attrs.field(factory=ray.util.queue.Queue, init=False)
    actor: ray.actor.ActorHandle = attrs.field(init=False)
    cached_tasks: list[tuple[int, Any]] = attrs.field(factory=list, init=False)
    inflight: dict[ray.ObjectRef, int] = attrs.field(factory=dict, init=False)
    _shutdown: bool = attrs.field(default=False, init=False)

    sealed: bool = attrs.field(default=False, init=False)  # no more tasks will be added
    enqueued: int = attrs.field(default=0, init=False)  # total expected tasks
    completed: int = attrs.field(default=0, init=False)  # total compelted tasks

    def __attrs_post_init__(self) -> None:
        self._start_writer()

    def _start_writer(self) -> None:
        self.actor = FragmentWriter.remote(
            self.ds_uri,
            self.output_columns,
            self.checkpoint_store,
            self.frag_id,
            self.queue,
            where=self.where,
        )
        # prime one future so we can detect when it finishes
        fut = self.actor.write.remote()
        self.inflight[fut] = self.frag_id

    def shutdown(self) -> None:
        len_inflight = len(self.inflight)
        if len_inflight > 0:
            try:
                is_empty = self.queue.empty()
            except (ray.exceptions.RayError, Exception):
                # queue actor died or unavailble.  assume empty
                is_empty = True
                # queue should be empty and inflight should be 0.
                _LOG.warning(
                    "Shutting down frag %s - queue empty %s, inflight: %d",
                    self.frag_id,
                    is_empty,
                    len_inflight,
                )

        if self._shutdown:
            return  # idempotent
        self.queue.shutdown()
        ray.kill(self.actor)
        self._shutdown = True

    def _restart(self) -> None:
        self.shutdown()

        self.queue = ray.util.queue.Queue()
        self.inflight.clear()
        self.cached_tasks, old_tasks = [], self.cached_tasks
        self.__attrs_post_init__()  # recreates writer & first future

        # replay tasks
        for off, res in old_tasks:
            self.queue.put((off, res))

    def ingest_task(self, offset: int, result: Any) -> None:
        """Called by manager when a new (offset, result) arrives."""
        self.cached_tasks.append((offset, result))
        self.enqueued += 1
        try:
            self.queue.put((offset, result))
        except (ray.exceptions.ActorDiedError, ray.exceptions.ActorUnavailableError):
            _LOG.warning("Writer actor for frag %s died – restarting", self.frag_id)
            self._restart()

    def poll_ready(self) -> list[tuple[int, Any]]:
        """Non‑blocking check for any finished futures.
        Returns list of (frag_id, new_file) that completed."""
        ready, _ = ray.wait(list(self.inflight.keys()), timeout=0.0)
        completed: list[tuple[int, Any]] = []

        for fut in ready:
            try:
                fid, new_file = ray.get(fut)
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                _LOG.warning(
                    "Writer actor for frag %s unavailable – restarting", self.frag_id
                )
                self._restart()
                return []  # will show up next poll
            assert fid == self.frag_id
            completed.append((fid, new_file))
            self.completed += 1
            self.inflight.pop(fut)
            # fire off a new “write” future to keep going
            new_fut = self.actor.write.remote()
            self.inflight[new_fut] = fid

        return completed

    def seal(self) -> None:
        self.sealed = True

    def drain(self) -> Generator[tuple[int, Any], None, None]:
        """Yield all (frag_id,new_file) as futures complete."""
        while self.inflight:
            ready, _ = ray.wait(list(self.inflight.keys()), timeout=5.0)
            if not ready:
                continue

            for fut in ready:
                try:
                    fid, new_file = ray.get(fut)
                    self.completed += 1
                except (
                    ray.exceptions.ActorDiedError,
                    ray.exceptions.ActorUnavailableError,
                ):
                    _LOG.warning(
                        "Writer actor for frag %s died during drain—restarting",
                        self.frag_id,
                    )
                    # clear out any old futures, spin up a fresh actor & queue
                    self._restart()
                    # break out to re-enter the while loop with a clean slate
                    break
                # sucessful write
                self.inflight.pop(fut)
                yield fid, new_file


@attrs.define
class FragmentWriterManager:
    """FragmentWriterManager is responsible for writing out fragments
    from the ReadTasks to the destination dataset.

    There is one instance so that we can track pending completed fragments and do
    partial commits.
    """

    dst_read_version: int
    ds_uri: str
    map_task: MapTask
    checkpoint_store: CheckpointStore
    where: str | None
    writer_tracker: ProgressTracker
    commit_granularity: int
    expected_tasks: dict[int, int]  # frag_id, # batches

    # internal state
    sessions: dict[int, FragmentWriterSession] = attrs.field(factory=dict, init=False)
    remaining_tasks: dict[int, int] = attrs.field(init=False)
    processed_writes: dict[int, int] = attrs.field(factory=dict, init=False)
    output_columns: list[str] = attrs.field(init=False)
    to_commit: list[tuple[int, lance.fragment.DataFile]] = attrs.field(
        factory=list, init=False
    )

    def __attrs_post_init__(self) -> None:
        # all output cols except for _rowaddr because it is implicit since the
        # lancedatafile is writing out in sequential order
        self.output_columns = [
            f.name for f in self.map_task.output_schema() if f.name != "_rowaddr"
        ]
        self.remaining_tasks = dict(self.expected_tasks)

    def ingest(self, result, task) -> None:
        frag_id = task.dest_frag_id()

        sess = self.sessions.get(frag_id)
        if sess is None:
            _LOG.debug("Creating writer for fragment %d", frag_id)
            sess = FragmentWriterSession(
                frag_id=frag_id,
                ds_uri=self.ds_uri,
                output_columns=self.output_columns,
                checkpoint_store=self.checkpoint_store,
                where=self.where,
            )
            self.sessions[frag_id] = sess

        sess.ingest_task(task.dest_offset(), result)
        self.remaining_tasks[frag_id] -= 1
        if self.remaining_tasks[frag_id] <= 0:
            sess.seal()

        # TODO check if previously checkpointed fragment exists

        # collect and completed fragments
        for fid, new_file in sess.poll_ready():
            self._record_fragment(fid, new_file, self.commit_granularity)

    def _record_fragment(self, frag_id: int, new_file, commit_granularity: int) -> None:
        self.to_commit.append((frag_id, new_file))
        self._commit_if_n_fragments(commit_granularity)

        dedupe_key = _get_fragment_dedupe_key(self.ds_uri, frag_id, self.map_task)
        # store file name in case of a failure or delete and recalc reuse.
        self.checkpoint_store[dedupe_key] = pa.RecordBatch.from_pydict(
            {"file": new_file.path}
        )
        if self.writer_tracker:
            self.writer_tracker.increment.remote(1)

        # Track processed writes and hybrid-shutdown
        done = self.processed_writes.get(frag_id, 0) + 1
        self.processed_writes[frag_id] = done
        expected = self.expected_tasks.get(frag_id, 0)
        sess = self.sessions.get(frag_id)
        if sess.sealed and done == expected and not sess.inflight:
            # flush any pending commit for this fragment
            self._commit_if_n_fragments(1)
            sess.shutdown()
            self.sessions.pop(frag_id)

    # aka _try_commit
    def _commit_if_n_fragments(self, commit_granularity: int) -> None:
        if len(self.to_commit) < commit_granularity:
            return

        to_commit = self.to_commit
        self.to_commit = []
        version = self.dst_read_version
        self.dst_read_version += 1

        operation = lance.LanceOperation.DataReplacement(
            replacements=[
                lance.LanceOperation.DataReplacementGroup(
                    fragment_id=frag_id,
                    new_file=new_file,
                )
                for frag_id, new_file in to_commit
            ]
        )
        lance.LanceDataset.commit(self.ds_uri, operation, read_version=version)

    def cleanup(self) -> None:
        _LOG.debug("draining & shutting down any leftover sessions")

        # 1) Commit any top‑of‑buffer fragments
        self._commit_if_n_fragments(1)

        # 2) Drain & shutdown whatever sessions remain
        for _frag_id, sess in list(self.sessions.items()):
            for fid, new_file in sess.drain():
                # this may in turn pop more sessions via _record_fragment
                self._record_fragment(fid, new_file, self.commit_granularity)
            sess.shutdown()

        # 3) Clear out any sessions that finished in the loop above
        self.sessions.clear()

        # 4) Final safety commit of anything left
        self._commit_if_n_fragments(1)


def run_ray_copy_table(
    dst: TableReference,
    packager: UDFPackager,
    checkpoint_store: CheckpointStore | None = None,
    *,
    job_id: str | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    **kwargs,
) -> None:
    # prepare job parameters
    config = JobConfig.get().with_overrides(
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
    )

    checkpoint_store = checkpoint_store or config.make_checkpoint_store()

    dst_schema = dst.open().schema
    if dst_schema.metadata is None:
        raise Exception("Destination dataset must have view metadata.")
    src_dburi = dst_schema.metadata[MATVIEW_META_BASE_DBURI.encode("utf-8")].decode(
        "utf-8"
    )
    src_name = dst_schema.metadata[MATVIEW_META_BASE_TABLE.encode("utf-8")].decode(
        "utf-8"
    )
    src_version = int(
        dst_schema.metadata[MATVIEW_META_BASE_VERSION.encode("utf-8")].decode("utf-8")
    )
    src = TableReference(db_uri=src_dburi, table_name=src_name, version=src_version)
    query_json = dst_schema.metadata[MATVIEW_META_QUERY.encode("utf-8")]
    query = GenevaQuery.model_validate_json(query_json)

    src_table = src.open()
    schema = GenevaQueryBuilder.from_query_object(src_table, query).schema

    job_id = job_id or uuid.uuid4().hex

    column_udfs = query.extract_column_udfs(packager)

    # take all cols (excluding some internal columns) since contents are needed to feed
    # udfs or copy src table data
    input_cols = [
        n for n in src_table.schema.names if n not in ["__is_set", "__source_row_id"]
    ]

    plan = plan_copy(
        src,
        dst,
        input_cols,
        batch_size=config.batch_size,
        task_shuffle_diversity=config.task_shuffle_diversity,
    )

    map_task = CopyTableTask(
        column_udfs=column_udfs, view_name=dst.table_name, schema=schema
    )

    _run_column_adding_pipeline(
        map_task,
        checkpoint_store,
        config,
        dst,
        plan,
        job_id,
        concurrency,
        **kwargs,
    )


def dispatch_run_ray_add_column(
    table_ref: TableReference,
    col_name: str,
    *,
    read_version: int | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    where: str | None = None,
    **kwargs,
) -> JobFuture:
    """
    Dispatch the Ray add column operation to a remote function.
    This is a convenience function to allow calling the remote function directly.
    """

    db = table_ref.open_db()
    hist = db._history
    job = hist.launch(table_ref.table_name, col_name, where=where, **kwargs)

    fragment_tracker = ProgressTracker.remote()
    writer_tracker = ProgressTracker.remote()
    worker_tracker = ProgressTracker.remote()

    obj_ref = run_ray_add_column_remote.remote(
        table_ref,
        col_name,
        read_version=read_version,
        job_id=job.job_id,
        concurrency=concurrency,
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
        where=where,
        fragment_tracker=fragment_tracker,
        writer_tracker=writer_tracker,
        worker_tracker=worker_tracker,
        **kwargs,
    )
    # object ref is only available here
    hist.set_object_ref(job.job_id, cloudpickle.dumps(obj_ref))
    return RayJobFuture(
        job_id=job.job_id,
        ray_obj_ref=obj_ref,
        fragment_tracker=fragment_tracker,
        writer_tracker=writer_tracker,
        worker_tracker=worker_tracker,
    )


def validate_backfill_args(
    tbl: Table,
    col_name: str,
    udf: UDF | None = None,
    input_columns: list[str] | None = None,
) -> None:
    """
    Validate the arguments for the backfill operation.
    This is a placeholder function to ensure that the arguments are valid.
    """
    if col_name not in tbl._ltbl.schema.names:
        raise ValueError(
            f"Column {col_name} is not defined this table.  "
            "Use add_columns to register it first"
        )

    if udf is None:
        from geneva.runners.ray.__main__ import fetch_udf

        udf_spec = fetch_udf(tbl, col_name)
        udf = tbl._conn._packager.unmarshal(udf_spec)

    if input_columns is None:
        field = tbl._ltbl.schema.field(col_name)
        input_columns = json.loads(
            field.metadata.get(b"virtual_column.udf_inputs", "null")
        )
    else:
        udf._input_columns_validator(None, input_columns)


@ray.remote
def run_ray_add_column_remote(
    table_ref: TableReference,
    col_name: str,
    *,
    job_id: str | None = None,
    input_columns: list[str] | None = None,
    udf: UDF | None = None,
    where: str | None = None,
    fragment_tracker,
    writer_tracker,
    worker_tracker,
    **kwargs,
) -> None:
    """
    Remote function to run the Ray add column operation.
    This is a wrapper around `run_ray_add_column` to allow it to be called as a Ray
    task.
    """
    import geneva  # noqa: F401  Force so that we have the same env in next level down

    tbl = table_ref.open()
    hist = tbl._conn._history
    hist.set_running(job_id)
    try:
        validate_backfill_args(tbl, col_name, udf, input_columns)
        if udf is None:
            from geneva.runners.ray.__main__ import fetch_udf

            udf_spec = fetch_udf(tbl, col_name)
            udf = tbl._conn._packager.unmarshal(udf_spec)

        if input_columns is None:
            field = tbl._ltbl.schema.field(col_name)
            input_columns = json.loads(
                field.metadata.get(b"virtual_column.udf_inputs", "null")
            )

        from geneva.runners.ray.pipeline import run_ray_add_column

        checkpoint_store = tbl._conn._checkpoint_store
        run_ray_add_column(
            table_ref,
            input_columns,
            {col_name: udf},
            checkpoint_store=checkpoint_store,
            where=where,
            fragment_tracker=fragment_tracker,
            writer_tracker=writer_tracker,
            worker_tracker=worker_tracker,
            **kwargs,
        )
        hist.set_completed(job_id)
    except Exception as e:
        _LOG.exception("Error running Ray add column operation")
        hist.set_failed(job_id, str(e))
        raise e


def run_ray_add_column(
    table_ref: TableReference,
    columns: list[str] | None,
    transforms: dict[str, UDF],
    checkpoint_store: CheckpointStore | None = None,
    *,
    read_version: int | None = None,
    job_id: str | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    where: str | None = None,
    writer_tracker=None,
    fragment_tracker=None,
    worker_tracker=None,
    **kwargs,
) -> None:
    # prepare job parameters
    config = JobConfig.get().with_overrides(
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
    )

    checkpoint_store = checkpoint_store or config.make_checkpoint_store()

    table = table_ref.open()
    uri = table.to_lance().uri

    # add pre-existing col if carrying previous values forward
    carry_forward_cols = list(set(transforms.keys()) & set(table.schema.names))
    _LOG.debug(f"carry_forward_cols {carry_forward_cols}")
    # this copy is necessary because the array extending updates inplace and this
    # columns array is directly referenced by the udf instance earlier
    cols = table.schema.names.copy() if columns is None else columns.copy()
    for cfcol in carry_forward_cols:
        # only append if cf col is not in col list already
        if cfcol not in cols:
            cols.append(cfcol)

    worker_tracker = worker_tracker or ProgressTracker.remote()
    rjs = _ray_job_status()
    worker_tracker.set.remote(rjs.get("ray_actors", 0))

    plan, pipeline_args = plan_read(
        uri,
        cols,
        batch_size=config.batch_size,
        read_version=read_version,
        task_shuffle_diversity=config.task_shuffle_diversity,
        where=where,
        **kwargs,
    )

    map_task = BackfillUDFTask(udfs=transforms, where=where)

    _LOG.info(
        f"starting backfill pipeline for {transforms} where='{where}'"
        f" with carry_forward_cols={carry_forward_cols}"
    )
    _run_column_adding_pipeline(
        map_task,
        checkpoint_store,
        config,
        table_ref,
        plan,
        job_id,
        concurrency,
        where=where,
        fragment_tracker=fragment_tracker,
        writer_tracker=writer_tracker,
        worker_tracker=worker_tracker,
        **pipeline_args,
    )


@attrs.define
class RayJobFuture(JobFuture):
    ray_obj_ref: ObjectRef = attrs.field()
    worker_tracker: ObjectRef | None = attrs.field(default=None)
    worker_pbar: TqdmType | None = attrs.field(default=None)
    fragment_tracker: ObjectRef | None = attrs.field(default=None)
    fragment_pbar: TqdmType | None = attrs.field(default=None)
    writer_tracker: ObjectRef | None = attrs.field(default=None)
    writer_pbar: TqdmType | None = attrs.field(default=None)

    def done(self, timeout: float = 0.0) -> bool:
        self.status()
        ready, _ = ray.wait([self.ray_obj_ref], timeout=timeout)
        done = bool(ready)
        if done:
            self.status()
        return done

    def result(self, timeout: float | None = None) -> Any:
        # TODO this can throw a ray.exceptions.GetTimeoutError if the task
        # does not complete in time, we should create a new exception type to
        # encapsulate Ray specifics
        self.status()
        return ray.get(self.ray_obj_ref, timeout=timeout)

    def status(self) -> None:
        if self.worker_tracker is not None:
            prog = ray.get(self.worker_tracker.get_progress.remote())
            n, total, done = prog["n"], prog["total"], prog["done"]
            if self.worker_pbar is None:
                _LOG.debug("starting worker tracker...")
                self.worker_pbar = tqdm(total=total, desc="Workers started")
            # sync the bar's count
            self.worker_pbar.total = total
            self.worker_pbar.n = n
            self.worker_pbar.refresh()
            if done:
                self.worker_pbar.close()

        if self.fragment_tracker is not None:
            prog = ray.get(self.fragment_tracker.get_progress.remote())
            n, total, done = prog["n"], prog["total"], prog["done"]
            if self.fragment_pbar is None:
                _LOG.debug("starting batchtracker...")
                self.fragment_pbar = tqdm(total=total, desc="Batches checkpointed")
            # sync the bar's count
            self.fragment_pbar.total = total
            self.fragment_pbar.n = n
            self.fragment_pbar.refresh()
            if done:
                self.fragment_pbar.close()

        if self.writer_tracker is not None:
            prog = ray.get(self.writer_tracker.get_progress.remote())
            n, total, done = prog["n"], prog["total"], prog["done"]
            if self.writer_pbar is None:
                _LOG.debug("starting fragment tracker...")
                self.writer_pbar = tqdm(total=total, desc="Fragments written")
            # sync the bar's count
            self.writer_pbar.total = total
            self.writer_pbar.n = n
            self.writer_pbar.refresh()
            if done:
                self.writer_pbar.close()
