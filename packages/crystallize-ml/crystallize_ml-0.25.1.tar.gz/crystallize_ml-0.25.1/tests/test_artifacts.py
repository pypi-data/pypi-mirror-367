from pathlib import Path

import numpy as np
import pytest
import pickle

from crystallize.utils.cache import compute_hash
from crystallize.utils.context import FrozenContext
from crystallize.datasources.datasource import DataSource
from crystallize.experiments.experiment import Experiment
from crystallize.pipelines.pipeline import Pipeline
from crystallize.pipelines.pipeline_step import PipelineStep
from crystallize import pipeline_step
from crystallize.plugins.plugins import ArtifactPlugin
from crystallize.experiments.experiment_graph import ExperimentGraph
from crystallize.datasources import Artifact, ArtifactLog
from crystallize.utils.context import ContextMutationError


class DummySource(DataSource):
    def fetch(self, ctx: FrozenContext):
        return 0


class LogStep(PipelineStep):
    def __call__(self, data, ctx):
        ctx.artifacts.add("out.txt", b"hello")
        return {"result": data}

    @property
    def params(self):
        return {}


class CheckStep(PipelineStep):
    def __init__(self, log_counts):
        self.log_counts = log_counts

    def __call__(self, data, ctx):
        self.log_counts.append(len(ctx.artifacts))
        return {"result": data}

    @property
    def params(self):
        return {}


def test_artifacts_saved_and_cleared(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logs = []
    pipeline = Pipeline([LogStep(), CheckStep(logs)])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp.validate()
    exp.run()

    exp_id = compute_hash(pipeline.signature())
    expected = (
        tmp_path
        / "arts"
        / exp_id
        / "v0"
        / "replicate_0"
        / "baseline"
        / "LogStep"
        / "out.txt"
    )
    assert expected.read_text() == "hello"
    assert logs == [0]


def test_artifacts_respect_experiment_name(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin], name="my_exp")
    exp.validate()
    exp.run()

    expected = (
        tmp_path
        / "arts"
        / "my_exp"
        / "v0"
        / "replicate_0"
        / "baseline"
        / "LogStep"
        / "out.txt"
    )
    assert expected.read_text() == "hello"


def test_artifact_datasource_before_run(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    run_plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp_run = Experiment(
        datasource=DummySource(), pipeline=pipeline, plugins=[run_plugin]
    )
    exp_run.validate()
    exp_run.run(replicates=2)

    fresh_exp = Experiment(
        datasource=DummySource(),
        pipeline=pipeline,
        plugins=[ArtifactPlugin(root_dir=str(tmp_path / "arts"))],
    )
    fresh_exp.validate()
    ds = fresh_exp.artifact_datasource(step="LogStep", name="out.txt")
    assert ds.replicates == 2
    assert ds.fetch(FrozenContext({"replicate": 1})).read_text() == "hello"


def test_artifact_versioning(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"), versioned=True)
    exp = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp.validate()
    exp.run()
    exp.run()

    exp_id = compute_hash(pipeline.signature())
    path0 = (
        tmp_path
        / "arts"
        / exp_id
        / "v0"
        / "replicate_0"
        / "baseline"
        / "LogStep"
        / "out.txt"
    )
    path1 = (
        tmp_path
        / "arts"
        / exp_id
        / "v1"
        / "replicate_0"
        / "baseline"
        / "LogStep"
        / "out.txt"
    )
    assert path0.exists() and path1.exists()


def test_metadata_written_and_chained(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp1 = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp1.validate()
    exp1.run(replicates=2)

    meta_path = Path(plugin.root_dir) / exp1.id / f"v{plugin.version}" / "metadata.json"
    assert meta_path.exists()

    ds2 = exp1.artifact_datasource(step="LogStep", name="out.txt")
    pipeline2 = Pipeline([CheckStep([])])
    exp2 = Experiment(datasource=ds2, pipeline=pipeline2)
    exp2.validate()
    first_path = ds2.fetch(FrozenContext({"replicate": 0}))
    assert isinstance(first_path, Path)
    assert first_path.exists()
    exp2.run()
    assert ds2.replicates == 2


def test_artifact_datasource_replicate_mismatch(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp1 = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp1.validate()
    exp1.run(replicates=2)

    ds2 = exp1.artifact_datasource(step="LogStep", name="out.txt")
    pipeline2 = Pipeline([CheckStep([])])
    exp2 = Experiment(datasource=ds2, pipeline=pipeline2)
    exp2.validate()

    # Should run with replicates % datasource_reps
    exp2.run(replicates=3)  # Will run with 3 % 2 = 1 replicate
    exp2.run(replicates=4)  # Will run with 4 % 2 = 0 replicate (maps to 0)
    exp2.run(replicates=5)  # Will run with 5 % 2 = 1 replicate


def test_artifact_datasource_missing_file(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp1 = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp1.validate()
    exp1.run()

    ds2 = exp1.artifact_datasource(step="LogStep", name="missing.txt")
    with pytest.raises(FileNotFoundError):
        ds2.fetch(FrozenContext({"replicate": 0}))


def test_artifact_datasource_require_metadata(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline = Pipeline([LogStep()])
    ds = DummySource()
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp1 = Experiment(datasource=ds, pipeline=pipeline, plugins=[plugin])
    exp1.validate()
    exp1.run()

    meta = Path(plugin.root_dir) / exp1.id / f"v{plugin.version}" / "metadata.json"
    meta.unlink()

    with pytest.raises(FileNotFoundError):
        exp1.artifact_datasource(step="LogStep", name="out.txt", require_metadata=True)


def test_output_write_and_injection(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class WriteStep(PipelineStep):
        def __init__(self, out: Artifact) -> None:
            self.out = out

        def __call__(self, data, ctx):
            self.out.write(b"data")
            return data

        @property
        def params(self):
            return {}

    out = Artifact("x.txt")
    pipeline = Pipeline([WriteStep(out)])
    exp = Experiment(
        datasource=DummySource(),
        pipeline=pipeline,
        plugins=[ArtifactPlugin(root_dir=str(tmp_path / "arts"))],
        outputs=[out],
    )
    exp.validate()
    exp.run()
    path = tmp_path / "arts" / exp.id / "v0" / "baseline" / "results.json"
    assert path.exists()


def test_artifact_log_write_once():
    log = ArtifactLog()
    log.add("a.txt", b"1")
    with pytest.raises(ContextMutationError):
        log.add("a.txt", b"2")


def test_artifact_plugin_unwritable_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def deny_open(*args, **kwargs):
        raise PermissionError("no write")

    monkeypatch.setattr("builtins.open", deny_open)

    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))

    exp = Experiment(
        datasource=DummySource(),
        pipeline=Pipeline([LogStep()]),
        plugins=[plugin],
    )
    exp.validate()
    with pytest.raises(PermissionError):
        exp.run()


class FlakyStep(PipelineStep):
    def __init__(self, artifact: Artifact) -> None:
        self.artifact = artifact

    def __call__(self, data, ctx):
        # do not write artifact
        ctx.metrics.add("val", data)
        return data

    @property
    def params(self):
        return {}


class DummyPass(PipelineStep):
    def __call__(self, data, ctx):
        return data

    @property
    def params(self):
        return {}


def test_missing_upstream_artifact(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    out = Artifact("x.txt")
    step_a = FlakyStep(out)
    exp_a = Experiment(
        datasource=DummySource(),
        pipeline=Pipeline([step_a]),
        plugins=[plugin],
        name="A",
        outputs=[out],
    )
    ds_b = exp_a.artifact_datasource(step="FlakyStep", name="x.txt")
    exp_b = Experiment(
        datasource=ds_b,
        pipeline=Pipeline([DummyPass()]),
        plugins=[plugin],
        name="B",
    )
    for e in (exp_a, exp_b):
        e.validate()
    graph = ExperimentGraph()
    graph.add_experiment(exp_a)
    graph.add_experiment(exp_b)
    graph.add_dependency(exp_b, exp_a)
    res = graph.run()
    assert any(isinstance(e, FileNotFoundError) for e in res["B"].errors.values())


def test_np_generic_serialization(tmp_path):
    class DummyStep(PipelineStep):
        def __call__(self, data, ctx):
            ctx.metrics.add("score", np.float64(3.14))  # This will hit `np.generic`
            return data

        @property
        def params(self):
            return {}

    class DummySource(DataSource):
        def fetch(self, ctx: FrozenContext):
            return 0

    plugin = ArtifactPlugin(root_dir=str(tmp_path / "arts"))
    exp = Experiment(
        datasource=DummySource(),
        pipeline=Pipeline([DummyStep()]),
        plugins=[plugin],
        name="test_generic",
    )
    exp.validate()
    exp.run()

    results_file = (
        tmp_path / "arts" / "test_generic" / "v0" / "baseline" / "results.json"
    )
    assert results_file.exists()
    content = results_file.read_text()
    assert "3.14" in content


@pipeline_step()
def write_simple(data, ctx, dest: Artifact):
    dest.write(b"data")
    ctx.metrics.add("val", data)
    return data


def test_lambda_loader_pickleable(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello")
    loader_art = Artifact("x.txt", loader=lambda p: p.read_text())
    dumped = pickle.dumps(loader_art)
    clone = pickle.loads(dumped)
    assert clone.loader(path) == "hello"


def test_default_writer(tmp_path):
    from crystallize.datasources.artifacts import default_writer

    assert default_writer(b"x") == b"x"
    assert default_writer("x") == b"x"
    with pytest.raises(TypeError):
        default_writer(1)  # type: ignore[arg-type]
