import random
import time
import threading
from typing import Any, List
from pathlib import Path

import numpy as np
import pytest
from crystallize.plugins.plugins import ArtifactPlugin, BasePlugin
from crystallize.experiments.result import Result

import asyncio
from crystallize.plugins.execution import ParallelExecution
from crystallize.plugins.plugins import SeedPlugin
from crystallize.utils.cache import compute_hash
from crystallize.utils.context import FrozenContext
from crystallize.datasources.datasource import DataSource
from crystallize.experiments.experiment import Experiment
from crystallize.datasources import Artifact
from crystallize.experiments.hypothesis import Hypothesis
from crystallize.pipelines.pipeline import Pipeline
from crystallize.pipelines.pipeline_step import PipelineStep
from crystallize.experiments.optimizers import BaseOptimizer, Objective
from crystallize.experiments.treatment import Treatment
from crystallize import (
    pipeline_step,
    data_source,
    verifier,
    hypothesis,
    treatment,
    AsyncExecution,
)


class DummyDataSource(DataSource):
    def fetch(self, ctx: FrozenContext):
        # return replicate id plus any increment in ctx
        return ctx["replicate"] + ctx.as_dict().get("increment", 0)


class PassStep(PipelineStep):
    cacheable = True

    def __call__(self, data, ctx):
        ctx.metrics.add("metric", data)
        return {"metric": data}

    @property
    def params(self):
        return {}


def always_significant(baseline, treatment):
    return {"p_value": 0.01, "significant": True, "accepted": True}


def test_experiment_run_basic():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )
    treatment = Treatment("treat", {"increment": 1})

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run(
        treatments=[treatment], hypotheses=[hypothesis], replicates=2
    )
    assert result.metrics.baseline.metrics["metric"] == [0, 1]
    assert result.metrics.treatments["treat"].metrics["metric"] == [1, 2]
    hyp_res = result.get_hypothesis(hypothesis.name)
    assert hyp_res is not None and hyp_res.results["treat"]["accepted"] is True
    assert hyp_res.ranking["best"] == "treat"
    assert result.errors == {}


def test_experiment_run_multiple_treatments():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )
    treatment1 = Treatment("treat1", {"increment": 1})
    treatment2 = Treatment("treat2", {"increment": 2})
    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run(
        treatments=[treatment1, treatment2], hypotheses=[hypothesis], replicates=2
    )
    assert result.metrics.baseline.metrics["metric"] == [0, 1]
    assert result.metrics.treatments["treat1"].metrics["metric"] == [1, 2]
    assert result.metrics.treatments["treat2"].metrics["metric"] == [2, 3]
    hyp_res = result.get_hypothesis(hypothesis.name)
    assert hyp_res is not None and hyp_res.results["treat1"]["accepted"] is True
    assert hyp_res.results["treat2"]["accepted"] is True
    ranked = hyp_res.ranking["ranked"]
    assert ranked[0][0] == "treat1"


def test_experiment_run_baseline_only():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run()
    assert result.metrics.baseline.metrics["metric"] == [0]
    assert result.metrics.hypotheses == []


def test_experiment_run_treatments_no_hypotheses():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    treatment = Treatment("treat", {"increment": 1})

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run(treatments=[treatment])
    assert result.metrics.treatments["treat"].metrics["metric"] == [1]


def test_treatment_named_baseline_updates_baseline():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    baseline_t = Treatment("baseline", {"increment": 2})

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run(treatments=[baseline_t])
    assert result.metrics.baseline.metrics["metric"] == [2]
    assert "baseline" not in result.metrics.treatments


def test_experiment_run_hypothesis_without_treatments_raises():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    with pytest.raises(ValueError):
        experiment.run(hypotheses=[hypothesis])


class IdentityStep(PipelineStep):
    def __call__(self, data, ctx):
        return data

    @property
    def params(self):
        return {}


def test_experiment_apply_runs_pipeline():
    pipeline = Pipeline([IdentityStep(), PassStep()])
    datasource = DummyDataSource()
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    experiment.validate()
    output = experiment.apply(data=5)
    assert output == {"metric": 5}


def test_experiment_requires_validation():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    # run() and apply() should auto-validate
    result = experiment.run()
    assert result.metrics.baseline.metrics["metric"] == [0]
    output = experiment.apply(data=1)
    assert output == {"metric": 1}


def test_experiment_builder_chaining():
    experiment = (
        Experiment.builder()
        .datasource(DummyDataSource())
        .add_step(PassStep())
        .treatments([Treatment("t", {"increment": 1})])
        .hypotheses(
            [
                Hypothesis(
                    verifier=always_significant,
                    metrics="metric",
                    ranker=lambda r: r["p_value"],
                    name="hypothesis",
                )
            ]
        )
        .replicates(2)
        .build()
    )
    experiment.validate()
    result = experiment.run()
    assert result.metrics.treatments["t"].metrics["metric"] == [1, 2]
    hyp_res = result.get_hypothesis("hypothesis")
    assert hyp_res is not None and hyp_res.ranking["best"] == "t"


def test_run_zero_replicates():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    experiment.validate()
    result = experiment.run(replicates=0)
    assert len(result.metrics.baseline.metrics["metric"]) == 1


def test_validate_partial_config():
    with pytest.raises(TypeError):
        Experiment(pipeline=Pipeline([PassStep()]))


def test_apply_without_designated_exit():
    pipeline = Pipeline([IdentityStep(), PassStep()])
    datasource = DummyDataSource()
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    experiment.validate()
    output = experiment.apply(data=7)
    assert output == {"metric": 7}


class TrackStep(PipelineStep):
    def __init__(self):
        self.called = False

    def __call__(self, data, ctx):
        self.called = True
        return data

    @property
    def params(self):
        return {}


def test_apply_multiple_steps():
    step1 = TrackStep()
    step2 = TrackStep()
    pipeline = Pipeline([step1, step2, PassStep()])
    datasource = DummyDataSource()
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    experiment.validate()
    output = experiment.apply(data=3)
    assert output == {"metric": 3}
    assert step1.called is True
    assert step2.called is True


class StringMetricsStep(PipelineStep):
    cacheable = True

    def __call__(self, data, ctx):
        ctx.metrics.add("metric", "a")
        return {"metric": "a"}

    @property
    def params(self):
        return {}


def test_run_with_non_numeric_metrics_raises():
    pipeline = Pipeline([StringMetricsStep()])
    datasource = DummyDataSource()
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )
    treatment = Treatment("t", {"increment": 0})
    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    experiment.run(treatments=[treatment], hypotheses=[hypothesis])


def test_cache_provenance_reused_between_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    step = PassStep()
    pipeline1 = Pipeline([step])
    ds = DummyDataSource()
    exp1 = Experiment(datasource=ds, pipeline=pipeline1)
    exp1.validate()
    exp1.run()

    pipeline2 = Pipeline([PassStep()])
    exp2 = Experiment(datasource=ds, pipeline=pipeline2)
    exp2.validate()
    exp2.run()
    assert pipeline2.get_provenance()[0]["cache_hit"] is True


def test_experiment_id_set_after_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp.validate()
    exp.run()
    assert exp.id == compute_hash(pipeline.signature())


def test_experiment_reusable_multiple_runs():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    exp = Experiment(datasource=ds, pipeline=pipeline)
    exp.validate()
    res1 = exp.run()
    res2 = exp.run(treatments=[Treatment("t", {"increment": 1})], replicates=2)
    assert len(res1.metrics.baseline.metrics["metric"]) == 1
    assert len(res2.metrics.treatments["t"].metrics["metric"]) == 2


def test_parallel_execution_matches_serial():
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )
    treatment = Treatment("t", {"increment": 1})

    serial_exp = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    serial_exp.validate()
    serial_result = serial_exp.run(
        treatments=[treatment], hypotheses=[hypothesis], replicates=2
    )

    parallel_exp = Experiment(
        datasource=datasource,
        pipeline=pipeline,
        plugins=[ParallelExecution()],
    )
    parallel_exp.validate()
    parallel_result = parallel_exp.run(
        treatments=[treatment], hypotheses=[hypothesis], replicates=2
    )

    assert parallel_result.metrics == serial_result.metrics


class FailingStep(PipelineStep):
    def __call__(self, data, ctx):
        if ctx["replicate"] == 1:
            raise RuntimeError("boom")
        ctx.metrics.add("metric", data)
        return {"metric": data}

    @property
    def params(self):
        return {}


def test_parallel_execution_handles_errors():
    pipeline = Pipeline([FailingStep()])
    datasource = DummyDataSource()
    treatment = Treatment("t", {"increment": 1})

    serial = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    serial.validate()
    serial_res = serial.run(treatments=[treatment], replicates=2)

    parallel = Experiment(
        datasource=datasource,
        pipeline=pipeline,
        plugins=[ParallelExecution()],
    )
    parallel.validate()
    parallel_res = parallel.run(treatments=[treatment], replicates=2)

    assert parallel_res.metrics == serial_res.metrics
    assert parallel_res.errors.keys() == serial_res.errors.keys()


class SleepStep(PipelineStep):
    cacheable = False

    def __call__(self, data, ctx):
        time.sleep(0.1)
        ctx.metrics.add("metric", data)
        return {"metric": data}

    @property
    def params(self):
        return {}


def test_parallel_is_faster_for_sleep_step():
    pipeline = Pipeline([SleepStep()])
    ds = DummyDataSource()
    exp_serial = Experiment(datasource=ds, pipeline=pipeline)
    exp_serial.validate()
    start = time.time()
    exp_serial.run(replicates=5)
    serial_time = time.time() - start

    exp_parallel = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution()],
    )
    exp_parallel.validate()
    start = time.time()
    exp_parallel.run(replicates=5)
    parallel_time = time.time() - start

    assert serial_time > parallel_time


def test_parallel_high_replicate_count():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution()],
    )
    exp.validate()
    result = exp.run(replicates=10)
    assert len(result.metrics.baseline.metrics["metric"]) == 10


class FibStep(PipelineStep):
    cacheable = False

    def __init__(self, n: int = 32) -> None:
        self.n = n

    def __call__(self, data, ctx):
        def fib(k: int) -> int:
            return k if k < 2 else fib(k - 1) + fib(k - 2)

        fib(self.n)
        ctx.metrics.add("metric", data)
        return {"metric": data}

    @property
    def params(self):
        return {"n": self.n}


def test_process_executor_faster_for_cpu_bound_step():
    pipeline = Pipeline([FibStep(35)])
    ds = DummyDataSource()

    exp_thread = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution(executor_type="thread")],
    )
    exp_thread.validate()
    start = time.time()
    exp_thread.run(replicates=4)
    thread_time = time.time() - start

    exp_process = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution(executor_type="process")],
    )
    exp_process.validate()
    start = time.time()
    exp_process.run(replicates=4)
    process_time = time.time() - start

    assert process_time < thread_time


def test_invalid_executor_type_raises():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution(executor_type="bogus")],
    )
    exp.validate()
    with pytest.raises(ValueError):
        exp.run()


@pytest.mark.parametrize("replicates", [1, 5, 10])
def test_full_experiment_replicate_counts(replicates):
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    treatment = Treatment("t", {"increment": 1})
    hypothesis = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )

    experiment = Experiment(
        datasource=datasource,
        pipeline=pipeline,
    )
    experiment.validate()
    result = experiment.run(
        treatments=[treatment], hypotheses=[hypothesis], replicates=replicates
    )
    assert len(result.metrics.baseline.metrics["metric"]) == replicates
    assert len(result.metrics.treatments["t"].metrics["metric"]) == replicates
    hyp_res = result.get_hypothesis(hypothesis.name)
    assert hyp_res is not None and hyp_res.ranking["best"] == "t"


def test_apply_with_treatment_and_exit():
    pipeline = Pipeline([IdentityStep(), PassStep()])
    datasource = DummyDataSource()
    treatment = Treatment("inc", {"increment": 2})
    experiment = Experiment(datasource=datasource, pipeline=pipeline)
    experiment.validate()
    output = experiment.apply(treatment=treatment, data=5)
    assert output == {"metric": 5}


def test_provenance_signature_and_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    step = PassStep()
    pipeline = Pipeline([step])
    ds = DummyDataSource()
    exp1 = Experiment(datasource=ds, pipeline=pipeline)
    exp1.validate()
    res1 = exp1.run()
    assert res1.provenance["pipeline_signature"] == pipeline.signature()
    assert res1.provenance["replicates"] == 1

    pipeline2 = Pipeline([PassStep()])
    exp2 = Experiment(datasource=ds, pipeline=pipeline2)
    exp2.validate()
    exp2.run()
    assert pipeline2.get_provenance()[0]["cache_hit"] is True


def test_multiple_hypotheses_partial_failure():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    good = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
        name="good",
    )
    bad = Hypothesis(
        verifier=always_significant,
        metrics="missing",
        ranker=lambda r: r["p_value"],
        name="bad",
    )
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
    )
    exp.validate()
    with pytest.raises(Exception):
        exp.run(treatments=[Treatment("t", {"increment": 1})], hypotheses=[good, bad])


def test_process_pool_respects_max_workers(monkeypatch):
    recorded = {}

    class DummyExecutor:
        def __init__(self, max_workers=None):
            recorded["max"] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(self, fn, rep):
            class F:
                def __init__(self_inner) -> None:
                    self_inner._condition = threading.Condition()
                    self_inner._state = "FINISHED"
                    self_inner._waiters = []

                def result(self_inner):
                    return fn(rep)

                def done(self_inner):  # pragma: no cover - minimal future API
                    return True

            return F()

    from crystallize.plugins import execution

    monkeypatch.setattr(execution, "ProcessPoolExecutor", DummyExecutor)
    monkeypatch.setattr(execution.os, "cpu_count", lambda: 4)
    from crystallize.experiments.run_results import ReplicateResult

    def dummy_remote(args):
        # args now include baseline_treatment as last element
        return ReplicateResult(None, None, {}, {}, {}, {})

    monkeypatch.setattr(
        "crystallize.experiments.experiment._run_replicate_remote",
        dummy_remote,
    )

    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution(executor_type="process", max_workers=2)],
    )
    exp.validate()
    exp.run(replicates=5)

    assert recorded["max"] == 2


@pytest.mark.parametrize("parallel", [False, True])
def test_ctx_mutation_error_parallel_and_serial(parallel):
    class MutateStep(PipelineStep):
        def __call__(self, data, ctx):
            ctx["condition"] = "oops"

        @property
        def params(self):
            return {}

    pipeline = Pipeline([MutateStep()])
    ds = DummyDataSource()
    plugins = [ParallelExecution()] if parallel else []
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=plugins,
    )
    exp.validate()
    result = exp.run(replicates=2)
    assert result.metrics.baseline.metrics == {}
    assert "baseline_rep_0" in result.errors and "baseline_rep_1" in result.errors


class FailingSource(DataSource):
    def fetch(self, ctx: FrozenContext):
        raise RuntimeError("source fail")


def test_datasource_failure_recorded():
    pipeline = Pipeline([PassStep()])
    ds = FailingSource()
    exp = Experiment(datasource=ds, pipeline=pipeline)
    exp.validate()
    result = exp.run(replicates=2)
    assert "baseline_rep_0" in result.errors
    assert "baseline_rep_1" in result.errors


def test_treatment_failure_recorded():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    failing = Treatment("boom", lambda ctx: (_ for _ in ()).throw(RuntimeError("bad")))
    exp = Experiment(datasource=ds, pipeline=pipeline)
    exp.validate()
    result = exp.run(treatments=[failing], replicates=2)
    assert "boom_rep_0" in result.errors
    assert "boom_rep_1" in result.errors


def test_ranker_error_bubbles():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()

    def bad_ranker(res):
        return 1 / 0

    hyp = Hypothesis(verifier=always_significant, metrics="metric", ranker=bad_ranker)
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
    )
    exp.validate()
    with pytest.raises(ZeroDivisionError):
        exp.run(treatments=[Treatment("t", {"increment": 1})], hypotheses=[hyp])


def test_invalid_replicates_type():
    with pytest.raises(TypeError):
        Experiment(
            datasource=DummyDataSource(),
            pipeline=Pipeline([PassStep()]),
            replicates="three",
        )


def test_zero_negative_replicates_clamped():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    for reps in [0, -5]:
        exp = Experiment(datasource=ds, pipeline=pipeline)
        exp.validate()
        result = exp.run(replicates=reps)
        assert len(result.metrics.baseline.metrics["metric"]) == 1


# Slow
def test_high_replicates_parallel_no_issues():
    pipeline = Pipeline([PassStep()])
    ds = DummyDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[ParallelExecution(executor_type="thread")],
    )
    exp.validate()
    result = exp.run(replicates=50)
    assert len(result.metrics.baseline.metrics["metric"]) == 50


class RandomDataSource(DataSource):
    def fetch(self, ctx: FrozenContext):
        return np.random.random()


class RandomStep(PipelineStep):
    cacheable = False

    def __call__(self, data, ctx):
        val = data + random.random()
        ctx.metrics.add("rand", val)
        return {"rand": val}

    @property
    def params(self):
        return {}


# TODO: Resolve this bug
@pytest.mark.xfail(reason="Seed plugin does not yet work correctly across executors")
def test_auto_seed_reproducible_serial_vs_parallel():
    pipeline = Pipeline([RandomStep()])
    ds = RandomDataSource()

    def numpy_seed_fn(seed: int) -> None:
        random.seed(seed)
        np.random.seed(seed % (2**32 - 1))

    serial = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[SeedPlugin(seed=123, auto_seed=True, seed_fn=numpy_seed_fn)],
    )
    serial.validate()
    res_serial = serial.run(replicates=3)

    parallel = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[
            SeedPlugin(seed=123, auto_seed=True, seed_fn=numpy_seed_fn),
            ParallelExecution(),
        ],
    )
    parallel.validate()
    res_parallel = parallel.run(replicates=3)

    assert res_serial.metrics == res_parallel.metrics
    assert res_serial.provenance["seeds"] == res_parallel.provenance["seeds"]
    expected = [hash(123 + rep) for rep in range(3)]
    assert res_serial.provenance["seeds"]["baseline"] == expected


def test_custom_seed_function_called():
    called: List[int] = []

    def record_seed(val: int) -> None:
        called.append(val)

    pipeline = Pipeline([RandomStep()])
    ds = RandomDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[SeedPlugin(seed=7, seed_fn=record_seed, auto_seed=True)],
    )
    exp.validate()
    exp.run(replicates=1)
    assert called == [hash(7)]


def test_apply_seed_function_called():
    called: List[int] = []

    def record_seed(val: int) -> None:
        called.append(val)

    pipeline = Pipeline([IdentityStep()])
    ds = DummyDataSource()
    exp = Experiment(
        datasource=ds,
        pipeline=pipeline,
        plugins=[SeedPlugin(seed_fn=record_seed)],
    )
    exp.validate()
    exp.apply(data=1, seed=5)
    assert called == [5]


class CountingOptimizer(BaseOptimizer):
    def __init__(self) -> None:
        super().__init__(Objective(metric="metric", direction="minimize"))
        self.ask_called = 0
        self.tell_called = 0

    def ask(self) -> list[Treatment]:
        self.ask_called += 1
        return [Treatment("opt", {"increment": 1})]

    def tell(self, objective_values: dict[str, float]) -> None:
        self.tell_called += 1

    def get_best_treatment(self) -> Treatment:
        return Treatment("best", {"increment": 0})


def test_run_with_arguments() -> None:
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    exp = Experiment(datasource=datasource, pipeline=pipeline)
    exp.validate()
    treatment = Treatment("inc", {"increment": 2})
    hyp = Hypothesis(
        verifier=always_significant,
        metrics="metric",
        ranker=lambda r: r["p_value"],
    )
    result = exp.run(treatments=[treatment], hypotheses=[hyp], replicates=2)
    assert result.metrics.treatments["inc"].metrics["metric"] == [2, 3]


class IncrementStep(PipelineStep):
    cacheable = False

    def __call__(self, data, ctx):
        return data + ctx.get("increment", 0)

    @property
    def params(self):
        return {}


def test_apply_with_treatment_object() -> None:
    pipeline = Pipeline([IncrementStep()])
    datasource = DummyDataSource()
    exp = Experiment(datasource=datasource, pipeline=pipeline)
    exp.validate()
    treatment = Treatment("inc", {"increment": 2})
    output = exp.apply(treatment=treatment, data=1)
    assert output == 3


def test_optimize_method_calls_optimizer_correctly() -> None:
    pipeline = Pipeline([PassStep()])
    datasource = DummyDataSource()
    exp = Experiment(datasource=datasource, pipeline=pipeline)
    exp.validate()
    opt = CountingOptimizer()
    best = exp.optimize(opt, num_trials=5, replicates_per_trial=1)
    assert opt.ask_called == 5
    assert opt.tell_called == 5
    assert best.name == "best"


class FailSetupStep(PipelineStep):
    def __init__(self) -> None:
        self.teardown_called = False

    def __call__(self, data, ctx):
        return data

    def setup(self, ctx):
        raise RuntimeError("setup fail")

    def teardown(self, ctx):
        self.teardown_called = True

    @property
    def params(self):
        return {}


class FailTeardownStep(PipelineStep):
    def __call__(self, data, ctx):
        return data

    def teardown(self, ctx):
        raise RuntimeError("teardown fail")

    @property
    def params(self):
        return {}


class BadPlugin(BasePlugin):
    def before_run(self, experiment):
        raise RuntimeError("plugin fail")


def test_step_setup_failure_calls_teardown():
    step = FailSetupStep()
    exp = Experiment(datasource=DummyDataSource(), pipeline=Pipeline([step]))
    exp.validate()
    with pytest.raises(RuntimeError):
        exp.run()
    assert step.teardown_called is True


def test_step_teardown_failure_raises():
    step = FailTeardownStep()
    exp = Experiment(datasource=DummyDataSource(), pipeline=Pipeline([step]))
    exp.validate()
    with pytest.raises(RuntimeError):
        exp.run()


def test_before_run_plugin_failure():
    plugin = BadPlugin()
    exp = Experiment(
        datasource=DummyDataSource(), pipeline=Pipeline([PassStep()]), plugins=[plugin]
    )
    exp.validate()
    with pytest.raises(RuntimeError):
        exp.run()


class RecordingPlugin(BasePlugin):
    def __init__(self) -> None:
        self.calls: list[str] = []

    def before_run(self, experiment: Experiment) -> None:
        self.calls.append("before_run")

    def before_replicate(self, experiment: Experiment, ctx: FrozenContext) -> None:
        self.calls.append("before_replicate")

    def after_step(
        self,
        experiment: Experiment,
        step: PipelineStep,
        data: Any,
        ctx: FrozenContext,
    ) -> None:
        self.calls.append(f"after_step_{step.__class__.__name__}")

    def after_run(self, experiment: Experiment, result: Result) -> None:
        self.calls.append("after_run")


class SetupTeardownStep(PipelineStep):
    def __init__(self) -> None:
        self.setup_called = False
        self.teardown_called = False

    def __call__(self, data, ctx):
        return data

    def setup(self, ctx):
        self.setup_called = True

    def teardown(self, ctx):
        self.teardown_called = True

    @property
    def params(self):
        return {}


def test_apply_runs_full_lifecycle():
    step = SetupTeardownStep()
    plugin = RecordingPlugin()
    exp = Experiment(
        datasource=DummyDataSource(), pipeline=Pipeline([step]), plugins=[plugin]
    )
    exp.validate()
    output = exp.apply(data=1)
    assert output == 1
    assert step.setup_called is True and step.teardown_called is True
    assert plugin.calls == [
        "before_run",
        "before_replicate",
        f"after_step_{step.__class__.__name__}",
        "after_run",
    ]


def test_apply_seed_plugin_autoseed():
    called: list[int] = []

    def record_seed(val: int) -> None:
        called.append(val)

    step = IdentityStep()
    ds = DummyDataSource()
    plugin = SeedPlugin(seed=7, seed_fn=record_seed)
    exp = Experiment(datasource=ds, pipeline=Pipeline([step]), plugins=[plugin])
    exp.validate()
    exp.apply(data=1)
    assert called == [hash(7)]


def test_experiment_resume_skips(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class CountStep(PipelineStep):
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, data, ctx):
            self.calls += 1
            ctx.metrics.add("metric", data)
            return {"metric": data}

        @property
        def params(self):
            return {}

    step = CountStep()
    pipeline = Pipeline([step])
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp = Experiment(
        datasource=DummyDataSource(),
        pipeline=pipeline,
        plugins=[plugin],
        outputs=[Artifact("x.txt")],
    )
    exp.validate()
    exp.run()
    assert step.calls == 1

    step2 = CountStep()
    exp2 = Experiment(
        datasource=DummyDataSource(),
        pipeline=Pipeline([step2]),
        plugins=[plugin],
        outputs=[Artifact("x.txt")],
    )
    exp2.validate()
    exp2.run(strategy="resume")
    assert step2.calls == 0


class FailingAfterTwo(DataSource):
    def fetch(self, ctx: FrozenContext):
        rep = ctx.get("replicate", 0)
        if rep > 2:
            raise ValueError("DataSource failed")
        return rep


def test_run_datasource_partial_failures():
    pipeline = Pipeline([PassStep()])
    ds = FailingAfterTwo()
    exp = Experiment(datasource=ds, pipeline=pipeline)
    exp.validate()
    res = exp.run(replicates=5)
    assert res.metrics.baseline.metrics["metric"] == [0, 1, 2]
    assert isinstance(res.errors.get("baseline_rep_3"), ValueError)
    assert isinstance(res.errors.get("baseline_rep_4"), ValueError)


def test_experiment_description_attribute():
    exp = Experiment(
        datasource=DummyDataSource(),
        pipeline=Pipeline([PassStep()]),
        description="my experiment",
    )
    assert exp.description == "my experiment"


@pipeline_step()
async def async_increment(data, ctx):
    await asyncio.sleep(0)
    inc = ctx.as_dict().get("inc", 0)
    return data + inc


@pipeline_step()
def record(data, ctx):
    ctx.metrics.add("metric", data)
    return {"metric": data}


@data_source
def constant(ctx, value=0):
    return value


@verifier
def dummy_verifier(baseline, treatment, *, alpha=0.05):
    return {"p_value": 0.01, "significant": True, "accepted": True}


@hypothesis(verifier=dummy_verifier(), metrics="metric")
def dummy_ranker(result):
    return result["p_value"]


@treatment("inc_async")
def inc_async(ctx):
    ctx.add("inc", 1)


def test_async_execution_with_hypothesis_and_verifier():
    ds = constant(value=2)
    pipe = Pipeline([async_increment(), record()])
    exp = Experiment(
        datasource=ds,
        pipeline=pipe,
        plugins=[AsyncExecution()],
    )
    exp.validate()
    result = exp.run(treatments=[inc_async()], hypotheses=[dummy_ranker], replicates=2)
    assert result.metrics.baseline.metrics["metric"] == [2, 2]
    assert result.metrics.treatments["inc_async"].metrics["metric"] == [3, 3]


def test_experiment_requires_datasource_and_pipeline():
    with pytest.raises(TypeError) as excinfo:
        Experiment()
    assert "datasource" in str(excinfo.value)
    assert "pipeline" in str(excinfo.value)


def test_validation_error_prints_message(capsys):
    exp = Experiment(
        datasource=DummyDataSource(),
        pipeline=Pipeline([PassStep()]),
    )
    exp._validated = False

    with pytest.raises(ValueError, match="boom"):
        exp.validate = lambda: (_ for _ in ()).throw(ValueError("boom"))
        exp.run()

    captured = capsys.readouterr()
    assert "Experiment validation failed: boom" in captured.out


def test_validation_error_prints_message_in_apply(capsys):
    exp = Experiment(
        datasource=DummyDataSource(),
        pipeline=Pipeline([PassStep()]),
    )
    exp._validated = False

    with pytest.raises(ValueError, match="boom"):
        exp.validate = lambda: (_ for _ in ()).throw(ValueError("boom"))
        exp.apply()

    captured = capsys.readouterr()
    assert "Experiment validation failed: boom" in captured.out
