"""CPU-only tests of the labeling pipeline with a stub model: prompt building, truncation, dedup and mapping back,
shard write / resume after a killed job, metadata check, time budget, JSON schema, merge coverage and reports.
Run from the repo root or this folder: `python -m pytest -q labeling`."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import label_tasks as lt  # noqa: E402
import merge_labels as ml  # noqa: E402
import taxonomy  # noqa: E402

BENCH = "llmrouterbench"


class StubLabeler:
    """Canned JSON by keyword; optionally raises after `fail_after` batches to simulate a killed job."""

    def __init__(self, fail_after=None, answer=None):
        self.batches = 0
        self.prompts: list[list[dict]] = []
        self.fail_after = fail_after
        self.answer = answer

    def label(self, messages_list):
        self.batches += 1
        if self.fail_after is not None and self.batches > self.fail_after:
            raise RuntimeError("simulated kill")
        out = []
        for msgs in messages_list:
            self.prompts.append(msgs)
            user = msgs[1]["content"]
            if self.answer is not None:
                out.append(self.answer(user))
            elif "SELECT" in user:
                out.append(json.dumps({"level1": "code", "level2": "sql_databases", "level3": "sql join query"}))
            else:
                out.append(json.dumps({"level1": "math", "level2": "algebra_precalculus", "level3": "Solve Equation"}))
        return out


def fake_queries(n=25, n_dups=3) -> pd.DataFrame:
    rows = []
    for i in range(n):
        q = f"Solve for x: {i}x + {i + 1} = {2 * i}" if i % 4 else f"SELECT * FROM t{i} JOIN u ON t{i}.id = u.id"
        rows.append((f"q/{i:03d}", "mmlupro" if i % 2 else "arenahard", "math" if i % 2 else "coding", q))
    df = pd.DataFrame(rows, columns=["query_id", "theme", "subtask", "query"])
    # the last n_dups rows repeat the text of row 1 (same theme) -> must be labeled once and mapped back
    df.loc[df.index[-n_dups:], "query"] = df.loc[1, "query"]
    return df


@pytest.fixture
def data_root(tmp_path):
    root = tmp_path / "data"
    (root / BENCH).mkdir(parents=True)
    df = fake_queries()
    df["prompt"] = df["query"]
    df["n_chars"] = df["query"].str.len()
    df.to_parquet(root / BENCH / "queries.parquet", index=False)
    return root


def meta(**kw):
    base = dict(model="/nonexistent/model", dtype="bfloat16", max_query_chars=3000, shard_size=10, max_tokens=64, max_model_len=4096)
    base.update(kw)
    return lt.build_metadata(**base)


# ------------------------------------------------------------------------------------------------------ taxonomy

def test_taxonomy_lists():
    assert len(taxonomy.LEVEL1) <= 12
    assert len(taxonomy.LEVEL2_ALL) == len(set(taxonomy.LEVEL2_ALL))
    for d, subs in taxonomy.DOMAINS.items():
        assert 3 <= len(subs) <= 10, d
        assert subs[-1].startswith("other"), d
        for s in subs:
            assert taxonomy.level1_of(s) == d
            assert taxonomy.is_consistent(d, s)
    assert not taxonomy.is_consistent("math", "sql_databases")
    assert taxonomy.level1_of("nope") is None


def test_json_schema_valid_and_enforces_enums():
    schema = taxonomy.json_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    v = jsonschema.Draft202012Validator(schema)
    v.validate({"level1": "math", "level2": "number_theory", "level3": "modular arithmetic"})
    assert list(v.iter_errors({"level1": "math", "level2": "not_a_subdomain", "level3": "x"}))
    assert list(v.iter_errors({"level1": "math", "level2": "number_theory", "level3": "x", "extra": 1}))
    assert list(v.iter_errors({"level1": "math", "level2": "number_theory"}))
    assert list(v.iter_errors({"level1": "math", "level2": "number_theory", "level3": "y" * 61}))


# -------------------------------------------------------------------------------------------------- prompt pieces

def test_truncate_middle():
    assert lt.truncate_middle("short", 100) == ("short", False)
    text = "H" * 500 + "M" * 1000 + "T" * 500
    out, tr = lt.truncate_middle(text, 300)
    assert tr
    assert out.startswith("H" * 180) and out.endswith("T" * 120)
    assert "characters omitted" in out and "M" not in out
    assert len(out) <= 300 + len(lt.TRUNCATION_MARKER) + 10
    assert lt.truncate_middle(text, 0) == (text, False)


def test_build_messages_and_prompt_hash():
    msgs, tr = lt.build_messages("What is 2+2?", "gsm", "arith", 3000)
    assert not tr and msgs[0]["role"] == "system" and msgs[1]["role"] == "user"
    assert msgs[0]["content"] == lt.SYSTEM_PROMPT
    assert 'dataset "gsm"' in msgs[1]["content"] and 'subcategory "arith"' in msgs[1]["content"]
    assert "What is 2+2?" in msgs[1]["content"]
    for name in taxonomy.LEVEL1 + taxonomy.LEVEL2_ALL:
        assert name in lt.SYSTEM_PROMPT
    h = lt.prompt_hash()
    assert len(h) == 16 and h == lt.prompt_hash()
    long_msgs, tr = lt.build_messages("x" * 10000, "t", "s", 3000)
    assert tr and len(long_msgs[1]["content"]) < 3600


def test_parse_output():
    ok = lt.parse_output('{"level1": "math", "level2": "algebra_precalculus", "level3": "  Solve   Quadratic "}')
    assert (ok.level1, ok.level2, ok.level3, ok.consistent) == ("math", "algebra_precalculus", "solve quadratic", True)
    bad_pair = lt.parse_output('{"level1": "math", "level2": "sql_databases", "level3": "x"}')
    assert bad_pair.consistent is False and bad_pair.level1 == "math" and bad_pair.level2 == "sql_databases"
    unknown = lt.parse_output('{"level1": "cooking", "level2": "baking", "level3": "x"}')
    assert (unknown.level1, unknown.level2, unknown.consistent) == ("other", "other", True)
    garbage = lt.parse_output("not json at all")
    assert garbage.level3 == lt.PARSE_ERROR and not garbage.consistent and garbage.raw_output == "not json at all"
    fenced = lt.parse_output('```json\n{"level1": "code", "level2": "web_frontend", "level3": "css layout"}\n```')
    assert fenced.level2 == "web_frontend" and fenced.consistent
    assert lt.parse_output(None).level3 == lt.PARSE_ERROR


# ------------------------------------------------------------------------------------------ dedup, shards, resume

def test_dedup_and_mapping_back(tmp_path):
    df = lt.select_rows(fake_queries(), None)
    stub = StubLabeler()
    stats = lt.run_benchmark(df, tmp_path / BENCH, stub, meta(shard_size=100), shard_size=100, max_query_chars=3000)
    assert stats["shards_done"] == 1 and stats["model_calls"] == df["query"].nunique() == len(stub.prompts)
    out = pd.read_parquet(lt.shard_path(tmp_path / BENCH, 0))
    assert list(out.columns) == lt.OUTPUT_COLUMNS and len(out) == len(df)
    assert set(out.query_id) == set(df.query_id)
    dup_text = df.loc[df.query_id == "q/001", "query"].item()
    dup_rows = out[out.query_id.isin(df[df["query"] == dup_text].query_id)]
    assert len(dup_rows) == 4 and dup_rows.level2.nunique() == 1 and dup_rows.raw_output.nunique() == 1
    assert out.consistent.all() and (out.level3 != lt.PARSE_ERROR).all()
    sql = out[out.query_id.isin(df[df["query"].str.startswith("SELECT")].query_id)]
    assert (sql.level2 == "sql_databases").all()


def test_shard_write_resume_after_kill(tmp_path):
    df = lt.select_rows(fake_queries(), None)
    bench_dir = tmp_path / BENCH
    killed = StubLabeler(fail_after=2)
    with pytest.raises(RuntimeError, match="simulated kill"):
        lt.run_benchmark(df, bench_dir, killed, meta(), shard_size=10, max_query_chars=3000)
    done = lt.existing_shards(bench_dir)
    assert [p.name for p in done] == ["shard_00000.parquet", "shard_00001.parquet"]
    assert not list(bench_dir.glob("*.tmp"))
    assert (bench_dir / "metadata.json").exists()

    fresh = StubLabeler()
    stats = lt.run_benchmark(df, bench_dir, fresh, meta(), shard_size=10, max_query_chars=3000)
    assert stats["shards_skipped"] == 2 and stats["shards_done"] == 1 and stats["shards_left"] == 0
    assert fresh.batches == 1
    # the duplicate texts in the last shard were already labeled in shard 0 -> reused from disk, not re-sent
    last = df.iloc[20:]
    new_texts = set(last["query"]) - set(df.iloc[:20]["query"])
    assert len(fresh.prompts) == len(new_texts)
    merged = pd.concat([pd.read_parquet(p) for p in lt.existing_shards(bench_dir)])
    assert len(merged) == len(df) and merged.query_id.is_unique
    # a third run does nothing
    idle = StubLabeler()
    stats = lt.run_benchmark(df, bench_dir, idle, meta(), shard_size=10, max_query_chars=3000)
    assert stats["shards_skipped"] == 3 and idle.batches == 0


def test_metadata_refuses_resume_on_mismatch(tmp_path):
    bench_dir = tmp_path / BENCH
    lt.write_or_check_metadata(bench_dir, meta())
    lt.write_or_check_metadata(bench_dir, meta())  # identical: fine
    m2 = meta()
    m2["vllm_version"] = "other"  # only warns
    lt.write_or_check_metadata(bench_dir, m2)
    for key, value in [("prompt_hash", "deadbeef"), ("taxonomy_version", "9.9.9"), ("max_query_chars", 1000), ("model", "/x")]:
        m3 = meta()
        m3[key] = value
        with pytest.raises(SystemExit, match="metadata differs"):
            lt.write_or_check_metadata(bench_dir, m3)


def test_time_budget_stops_before_new_shard(tmp_path):
    df = lt.select_rows(fake_queries(), None)
    tight = lt.TimeBudget(end_time=time.time() + 100, min_remaining=300)
    assert tight.exhausted()
    stub = StubLabeler()
    stats = lt.run_benchmark(df, tmp_path / BENCH, stub, meta(), shard_size=10, max_query_chars=3000, budget=tight)
    assert stats["shards_done"] == 0 and stats["shards_left"] == 3 and stub.batches == 0
    roomy = lt.TimeBudget(end_time=time.time() + 10_000, min_remaining=300)
    stats = lt.run_benchmark(df, tmp_path / BENCH, stub, meta(), shard_size=10, max_query_chars=3000, budget=roomy)
    assert stats["shards_done"] == 3 and stats["shards_left"] == 0
    assert lt.TimeBudget(None).remaining() is None and not lt.TimeBudget(None).exhausted()


def test_time_budget_from_env(monkeypatch):
    monkeypatch.setenv("SLURM_JOB_END_TIME", str(int(time.time()) + 50))
    assert lt.TimeBudget.from_env(300).exhausted()
    monkeypatch.delenv("SLURM_JOB_END_TIME")
    assert not lt.TimeBudget.from_env(300).exhausted()


def test_select_rows_and_shards():
    df = fake_queries(n=23)
    full = lt.select_rows(df, None)
    assert full.query_id.tolist() == sorted(df.query_id)
    sub = lt.select_rows(df, 5, seed=1)
    assert len(sub) == 5 and sub.query_id.tolist() == sorted(sub.query_id)
    shards = lt.plan_shards(full, 10)
    assert [len(s) for _, s in shards] == [10, 10, 3] and [i for i, _ in shards] == [0, 1, 2]
    with pytest.raises(ValueError):
        lt.plan_shards(full, 0)


def test_truncated_flag_recorded(tmp_path):
    df = lt.select_rows(fake_queries(n=6, n_dups=0), None)
    df.loc[0, "query"] = "L" * 5000
    stub = StubLabeler()
    lt.run_benchmark(df, tmp_path / BENCH, stub, meta(max_query_chars=1000), shard_size=100, max_query_chars=1000)
    out = pd.read_parquet(lt.shard_path(tmp_path / BENCH, 0)).set_index("query_id")
    assert out.truncated.sum() == 1 and bool(out.loc[df.loc[0, "query_id"], "truncated"])
    sent = [m[1]["content"] for m in stub.prompts if "characters omitted" in m[1]["content"]]
    assert len(sent) == 1 and len(sent[0]) < 1600


# ---------------------------------------------------------------------------------------------------------- merge

def run_full(data_root, out_dir, answer=None):
    df = lt.select_rows(lt.load_queries(BENCH, data_root), None)
    stub = StubLabeler(answer=answer)
    lt.run_benchmark(df, out_dir / BENCH, stub, meta(), shard_size=10, max_query_chars=3000)
    return df


def test_merge_outputs(data_root, tmp_path):
    out_dir = tmp_path / "out"
    reports = tmp_path / "reports"

    def answer(user):  # three domains so the report and the stratified sample have several classes
        if "SELECT" in user:
            return json.dumps({"level1": "code", "level2": "sql_databases", "level3": "sql join"})
        if "x + " in user and int(user.split("Solve for x: ")[1].split("x")[0]) % 3 == 0:
            return json.dumps({"level1": "math", "level2": "sql_databases", "level3": "oops"})  # inconsistent
        return "garbage" if "17x" in user else json.dumps({"level1": "math", "level2": "algebra_precalculus", "level3": "solve equation"})

    df = run_full(data_root, out_dir, answer)
    res = ml.merge_benchmark(BENCH, out_dir, data_root, None, reports, n_examples=3, n_handcheck=12)
    labels = pd.read_parquet(data_root / BENCH / "task_labels.parquet")
    assert list(labels.columns) == ml.LABEL_COLUMNS and labels.query_id.tolist() == pd.read_parquet(data_root / BENCH / "queries.parquet").query_id.tolist()
    assert res["inconsistent"] > 0 and res["parse_errors"] == 1
    full = pd.read_parquet(out_dir / BENCH / "labels_full.parquet")
    assert "raw_output" in full.columns and "query" not in full.columns
    report = (reports / f"{BENCH}_labels_report.md").read_text()
    for section in ("## Level 1", "## Level 2", "## Theme x level 1", "random examples per level 1", "### math", "### code", "Inconsistent pairs"):
        assert section in report
    sample = pd.read_csv(reports / f"{BENCH}_handcheck_sample.csv", keep_default_na=False)
    assert len(sample) == 12 and sample.columns.tolist()[-1] == "correct" and (sample.correct == "").all()
    assert set(sample.level1) == {"math", "code", "other"} and sample.query_id.is_unique  # "other" = the parse-error row


def test_merge_coverage_errors(data_root, tmp_path):
    out_dir = tmp_path / "out"
    run_full(data_root, out_dir)
    shards = lt.existing_shards(out_dir / BENCH)
    extra = pd.read_parquet(shards[0]).iloc[:1].assign(query_id="q/999")
    extra.to_parquet(out_dir / BENCH / "shard_00099.parquet", index=False)
    with pytest.raises(ml.CoverageError, match="unknown"):
        ml.merge_benchmark(BENCH, out_dir, data_root, None, tmp_path / "r")
    (out_dir / BENCH / "shard_00099.parquet").unlink()
    shards[-1].unlink()
    with pytest.raises(ml.CoverageError, match="missing"):
        ml.merge_benchmark(BENCH, out_dir, data_root, None, tmp_path / "r")
    dup = pd.read_parquet(shards[0])
    dup.to_parquet(out_dir / BENCH / "shard_00098.parquet", index=False)
    with pytest.raises(ml.CoverageError, match="duplicated"):
        ml.merge_benchmark(BENCH, out_dir, data_root, None, tmp_path / "r")
    with pytest.raises(ml.CoverageError, match="no shards"):
        ml.merge_benchmark(BENCH, tmp_path / "empty", data_root, None, tmp_path / "r")


def test_handcheck_stratified():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"query_id": [f"q{i}" for i in range(1000)], "theme": "t", "subtask": "s", "query": "q",
                       "level1": rng.choice(["math", "code", "other"], size=1000, p=[0.9, 0.09, 0.01]),
                       "level2": "x", "level3": "y", "consistent": True})
    s = ml.handcheck_sample(df, 200, seed=0, min_per_class=5)
    assert len(s) == 200 and s.query_id.is_unique
    counts = s.level1.value_counts()
    assert counts["other"] >= 5 and counts["code"] >= 5 and counts["math"] > 150


# -------------------------------------------------------------------------------------------------------- dry run

def test_token_stats():
    st = lt.token_stats(np.array([10, 20, 30, 4000]), limit=1000)
    assert st["n"] == 4 and st["max"] == 4000 and st["over_limit"] == 1 and st["median"] == 25
    assert lt.token_stats(np.array([])) == {"n": 0}


def test_dry_run_with_fallback_tokenizer(data_root, capsys):
    args = SimpleNamespace(tokenizer="/nonexistent/tokenizer", model="/nonexistent/model", data_root=str(data_root),
                           limit=None, seed=0, max_query_chars=3000, max_model_len=4096, max_tokens=64)
    res = lt.dry_run([BENCH], args)
    out = capsys.readouterr().out
    assert res[BENCH]["rows"] == 25 and res[BENCH]["unique_texts"] == 22 and res[BENCH]["over_limit"] == 0
    assert out.count("--- example prompt") == 3 and "tokenizer: tiktoken" in out and "per theme" in out
