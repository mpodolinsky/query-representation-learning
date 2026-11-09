"""End-to-end plumbing tests for the handcrafted representation, on fake data only (no benchmark data, no network
beyond tiktoken's cached BPE table; the whitespace tokenizer is used where the count matters).
Run from this folder:  python -m pytest -q"""
import csv
import dataclasses
import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "michal-harness"))
sys.path.insert(0, str(HERE))

from router import Data, Results, evaluate  # noqa: E402
from test_router import make_data  # noqa: E402
import task_taxonomy  # noqa: E402
from handcrafted import (FEATURE_NAMES, FEATURES, VARIANTS, HandcraftedEmbedding, MissingLevels, fit_concat,  # noqa: E402
                         fit_concat_factory, fit_handcrafted, fit_stats_only, fit_task_type_only, get_tokenizer,
                         level_labels, query_stats)


@dataclasses.dataclass
class HierData(Data):
    """The harness `Data` plus the finer task-type columns Arman's loader (or my offline classifier) will add."""
    task_level2: np.ndarray | None = None
    task_level3: np.ndarray | None = None


# raw label (dataset name, as the loader will give it) -> level-2 subdomain -> query templates
DATASETS = {
    "GSM8K": ("arithmetic", ["Solve for x: {a}x + {b} = {c}.", "Compute {a} * {b} - {c} and explain each step."]),
    "MATH500": ("algebra", ["What is the integral of x^{a} from 0 to {b}?", "Prove that the sum of the first {a} odd numbers is a square."]),
    "mbpp": ("python", ["Write a Python function:\n```python\ndef f(xs):\n    return sum(xs) / {a}\n```\nFix the bug for empty lists.",
                        "Convert this SQL to pandas: SELECT name FROM users WHERE age > {a};"]),
    "HumanEval": ("python", ["Why does `for (int i = 0; i < {a}; i++) {{ total += arr[i]; }}` segfault?"]),
    "mmlu-high_school_biology.val.3": ("biology", ["Describe how mitochondria produce ATP in eukaryotic cells.",
                                                   "What role does mRNA play in protein synthesis? Give {a} examples."]),
    "mmlu_pro_physics": ("physics", ["A ball is dropped from {a} m. How long until it hits the ground?"]),
    "ARC Challenge": ("earth_science", ["Why does the Moon show phases? Answer in {a} sentences."]),
    "hellaswag.dev.v0": ("sentence_completion", ["The chef put the tray in the oven and then..."]),
    "MT-Bench": ("open_chat", ["WHY DID THE ROMAN REPUBLIC COLLAPSE? Answer briefly.", "Who was the ruler of France in {a}?"]),
}


def make_text_data(Q=800, M=4, seed=0, split_seed=0, with_levels=True):
    """Tiny fake dataset with real-looking text, a raw dataset-name label per query (data.theme), optional level-2
    and level-3 columns, and scores that depend on the level-2 subdomain. Built from the harness's own `Data`."""
    rng = np.random.default_rng(seed)
    names = list(DATASETS)
    ds = rng.integers(len(names), size=Q)
    sub = np.array([DATASETS[names[d]][0] for d in ds], dtype=object)
    subs = sorted(set(sub.tolist()))
    queries = [rng.choice(DATASETS[names[d]][1]).format(a=rng.integers(2, 99), b=rng.integers(2, 99), c=rng.integers(2, 999))
               + f" (query {i})" for i, d in enumerate(ds)]  # unique texts, like real benchmark queries
    quality = np.clip(np.linspace(0.3, 0.7, M)[:, None] + rng.uniform(-0.3, 0.3, (M, len(subs))), 0, 1)
    sub_id = np.array([subs.index(s) for s in sub])
    S = (rng.random((Q, M)) < quality[:, sub_id].T).astype(float)
    order = np.random.default_rng(100 + split_seed).permutation(Q)
    a, b = int(0.6 * Q), int(0.7 * Q)
    kw = dict(task_level2=sub, task_level3=np.array([f"{s}/task{i % 2}" for i, s in enumerate(sub)], dtype=object)) if with_levels else {}
    return HierData(queries, [f"model{m}" for m in range(M)], S, np.geomspace(1, 20, M), train=order[:a], val=order[a:b],
                    test=order[b:], theme=np.array(names, dtype=object)[ds], split_seed=split_seed, **kw)


def load_fake_data(benchmark, split_seed=0):
    """Stands in for Arman's `load_data(benchmark, split_seed)` so run_handcrafted.py can be exercised.
    Benchmark 'fakebench_l1only' has no finer columns (the Level-1-only situation)."""
    return make_text_data(seed=hash(benchmark) % 1000, split_seed=split_seed, with_levels="l1only" not in benchmark)


@pytest.fixture(scope="module")
def text():
    return make_text_data()


@pytest.fixture(scope="module")
def l1only():
    return make_text_data(with_levels=False)


WS = dict(tokenizer="whitespace")


# ---------------------------------------------------------------- statistics

def test_query_stats_hand_checked_values():
    X = query_stats(["Is it? Really?\nYes.", "def f(x):\n    return {x}", "12 + 34 = 46", ""], get_tokenizer("whitespace")[1])
    f = {name: X[:, j] for j, name in enumerate(FEATURE_NAMES)}
    assert X.shape == (4, len(FEATURES)) and np.isfinite(X).all()
    assert list(f["n_question_marks"]) == [2, 0, 0, 0]
    assert list(f["n_lines"]) == [2, 2, 1, 0]
    assert list(f["n_sentences"]) == [3, 1, 1, 0]
    assert list(f["has_code"]) == [0, 1, 0, 0] and f["n_code_markers"][1] >= 3
    assert f["digit_density"][2] == pytest.approx(6 / 12) and f["math_symbol_density"][2] == pytest.approx(2 / 12)
    assert f["n_tokens"][0] == 4 and f["n_words"][0] == 4 and f["avg_word_length"][0] == pytest.approx(16 / 4)
    assert f["frac_uppercase"][0] == pytest.approx(3 / 13)


def test_tokenizer_falls_back_to_whitespace_with_a_warning():
    with pytest.warns(UserWarning, match="unavailable"):
        name, count = get_tokenizer("tiktoken:no_such_encoding")
    assert name == "whitespace" and count("a b  c") == 3
    with pytest.raises(ValueError):
        get_tokenizer("bogus:thing")


def test_tiktoken_counts_when_available():
    pytest.importorskip("tiktoken")
    name, count = get_tokenizer("tiktoken:cl100k_base")
    if name.startswith("tiktoken"):
        assert count("hello world") == 2 and count("<|endoftext|>") >= 1  # special tokens are plain text here


# ---------------------------------------------------------------- taxonomy

def test_taxonomy_resolves_spellings_subjects_and_unknowns():
    cases = {"GSM8K": "math", "gsm8k": "math", "MATH500": "math", "aime24": "math", "HumanEval": "code", "mbpp": "code",
             "SWE-Bench-Verified": "code", "BBH": "logic", "Knights & Knaves": "logic", "knights_and_knaves": "logic",
             "MMLU-Pro": "knowledge", "mmlu_pro_physics": "science", "mmlu_pro_law": "law", "GPQA": "science",
             "FinQA": "finance", "MedQA": "medicine", "HLE": "knowledge", "SimpleQA": "knowledge", "EmoryNLP": "affective",
             "MELD": "affective", "ArenaHard": "instruction_following", "τ²-Bench": "tool_use", "tau2bench": "tool_use",
             "hellaswag.dev.v0": "commonsense", "Winogrande": "commonsense", "ARC Challenge": "science",
             "mmlu-astronomy.val.5": "science", "mmlu-professional_law.val.1": "law", "mmlu-miscellaneous": "knowledge",
             "mmlu": "knowledge", "MT-Bench": "conversation", "rag": "rag", "biology": "science", "code": "code",
             "no_such_dataset": "other"}
    wrong = {k: (task_taxonomy.level1_of(k), v) for k, v in cases.items() if task_taxonomy.level1_of(k) != v}
    assert not wrong, wrong
    assert set(task_taxonomy.level1_of(k) for k in task_taxonomy.TAXONOMY) <= set(task_taxonomy.DOMAINS)
    with pytest.warns(UserWarning, match="not in the taxonomy"):
        mapped = task_taxonomy.map_labels(["GSM8K", "zzz", "zzz"])
    assert mapped == ["math", "other", "other"]
    assert "UNKNOWN" in task_taxonomy.report(["GSM8K", "zzz"]) and len(task_taxonomy.todos()) >= 5


def test_every_llmrouterbench_and_routerbench_dataset_has_an_entry():
    llmrb = ["AIME", "MATH500", "MATHBench", "LiveMathBench", "HumanEval", "MBPP", "LiveCodeBench", "SWE-Bench", "BBH", "KORBench",
             "Knights & Knaves", "MMLU-Pro", "GPQA", "FinQA", "MedQA", "HLE", "SimpleQA", "EmoryNLP", "MELD", "ArenaHard", "τ²-Bench"]
    rb = ["HellaSwag", "Winogrande", "ARC Challenge", "MMLU", "MT-Bench", "GSM8K", "MBPP", "RAG"]
    assert len(set(llmrb)) == 21 and len(set(rb)) == 8
    assert all(task_taxonomy.lookup(d)[0] is not None for d in llmrb + rb)


# ---------------------------------------------------------------- level sources

def test_level_labels_come_from_columns_then_taxonomy_then_nothing(text, l1only):
    assert list(level_labels(text, 0)[:3]) == list(text.theme[:3])                      # raw label
    assert list(level_labels(text, 1)[:3]) == task_taxonomy.map_labels(text.theme[:3])  # taxonomy on the raw label
    assert np.array_equal(level_labels(text, 2), text.task_level2)                      # the data column
    assert level_labels(l1only, 2) is None and level_labels(l1only, 3) is None          # nothing to read
    explicit = np.array(["x"] * len(text.queries), dtype=object)
    assert (level_labels(text, 2, labels={2: explicit}) == "x").all()                    # explicit beats the column
    l1 = dataclasses.replace(text, theme=None)
    l1.task_level1 = np.array(["dom"] * len(text.queries), dtype=object)                 # a loader-provided level-1 column bypasses the taxonomy
    assert (level_labels(l1, 1) == "dom").all() and level_labels(l1, 0) is None


# ---------------------------------------------------------------- standardization, one-hot blocks, whitening

def test_stats_are_standardized_on_train_only(text):
    emb = HandcraftedEmbedding(text, use_task_type=False, **WS)
    E = emb(text.queries)
    assert E.shape == (len(text.queries), len(FEATURES))
    tr = E[text.train]
    varying = tr.std(0) > 1e-9
    assert np.allclose(tr.mean(0), 0, atol=1e-9) and np.allclose(tr.std(0)[varying], 1, atol=1e-6)
    assert np.abs(E).max() <= emb.clip
    other = dataclasses.replace(text, test=text.test[:10])  # the test split does not influence the scaler
    assert np.allclose(HandcraftedEmbedding(other, use_task_type=False, **WS).mean_, emb.mean_)


def test_whitened_stats_block_has_identity_covariance_on_train(text):
    emb = HandcraftedEmbedding(text, use_task_type=False, whiten=True, **WS)
    W = emb(text.queries)[text.train]
    assert W.shape[1] <= len(FEATURES) and emb.n_stats_dims == W.shape[1]
    assert np.allclose(np.cov(W, rowvar=False), np.eye(W.shape[1]), atol=1e-6)
    assert emb.feature_names[-1] == f"stats_pc{W.shape[1]}" and "whitened" in emb.describe()


def test_hierarchical_block_has_one_one_hot_per_level(text):
    emb = fit_task_type_only(text, levels=(1, 2, 3))(text.models)
    assert emb.available_levels == [1, 2, 3]
    n1, n2, n3 = (len(emb.level_categories[l]) for l in (1, 2, 3))
    assert (n1, n2, n3) == (len(set(task_taxonomy.map_labels(text.theme))), len(set(text.task_level2)), len(set(text.task_level3)))
    E = emb(text.queries)
    assert E.shape == (len(text.queries), n1 + n2 + n3)
    assert (E[:, :n1].sum(1) == 1).all() and (E[:, n1:n1 + n2].sum(1) == 1).all() and (E[:, n1 + n2:].sum(1) == 1).all()
    assert emb.feature_names[0].startswith("L1=") and emb.feature_names[n1].startswith("L2=") and emb.feature_names[-1].startswith("L3=")
    assert [emb.level_categories[1][j] for j in E[:, :n1].argmax(1)] == task_taxonomy.map_labels(text.theme)
    assert [emb.level_categories[2][j] for j in E[:, n1:n1 + n2].argmax(1)] == list(text.task_level2)


def test_level_weights_scale_each_level_block(text):
    emb = HandcraftedEmbedding(text, use_stats=False, levels=(1, 2), level_weights={1: 2.0, 2: 0.5}, **WS)
    E = emb(text.queries)
    n1 = len(emb.level_categories[1])
    assert set(np.unique(E[:, :n1])) == {0.0, 2.0} and set(np.unique(E[:, n1:])) == {0.0, 0.5}
    assert emb.onehot_scale == 1.0  # "balanced" with no stats block means 1


def test_unseen_category_at_test_time_is_an_all_zero_block(text):
    lvl2 = np.array(text.task_level2, dtype=object)
    lvl2[text.test[:5]] = "brand_new_subdomain"                     # only in the test split
    data = dataclasses.replace(text, task_level2=lvl2)
    emb = fit_task_type_only(data, levels=(1, 2))(None)
    n1 = len(emb.level_categories[1])
    assert "brand_new_subdomain" not in emb.level_categories[2]      # categories come from the training split
    E = emb(data.queries)
    assert (E[data.test[:5], n1:] == 0).all() and (E[data.test[:5], :n1].sum(1) == 1).all()  # L1 still set, L2 zero


def test_level_1_only_data_skips_the_missing_levels(l1only):
    with pytest.warns(UserWarning, match="skipped"):
        emb = fit_handcrafted(l1only, **WS)(None)                    # default levels (1, 2, 3): 2 and 3 are missing
    assert emb.available_levels == [1] and emb.dim == len(emb.level_categories[1]) + len(FEATURES)
    with pytest.raises(MissingLevels):
        fit_task_type_only(l1only, levels=(2,))
    with pytest.raises(MissingLevels):
        fit_task_type_only(l1only, levels=(2, 3))
    no_theme = dataclasses.replace(l1only, theme=None)
    with pytest.raises(MissingLevels):
        fit_task_type_only(no_theme, levels=(1,))
    fit_stats_only(no_theme, **WS)                                   # fine without labels


def test_raw_label_level_zero_is_the_dataset_name(text):
    emb = fit_task_type_only(text, levels=(0,))(None)
    assert emb.level_categories[0] == sorted(set(text.theme[text.train].tolist()), key=str)


def test_duplicated_texts_with_different_labels_warn_and_keep_the_first(text):
    queries = list(text.queries)
    queries[text.train[1]] = queries[text.train[0]]
    lvl2 = np.array(text.task_level2, dtype=object)
    lvl2[text.train[1]] = "other_sub"
    dup = dataclasses.replace(text, queries=queries, task_level2=lvl2)
    with pytest.warns(UserWarning, match="duplicated query texts"):
        E = fit_task_type_only(dup, levels=(2,))(None)(queries)
    assert np.array_equal(E[text.train[0]], E[text.train[1]])


def test_balanced_weight_equalizes_the_blocks_and_float_weight_is_used_as_is(text):
    emb = HandcraftedEmbedding(text, **WS)
    E = emb(text.queries)[text.train]
    C = emb.n_task_dims
    assert emb.dim == C + len(FEATURES)
    assert E[:, :C].var(0).sum() == pytest.approx(E[:, C:].var(0).sum())
    fixed = HandcraftedEmbedding(text, onehot_weight=3.0, stats_weight=0.5, **WS)
    E = fixed(text.queries)
    assert set(np.unique(E[:, :C])) == {0.0, 3.0} and np.abs(E[:, C:]).max() <= 0.5 * fixed.clip
    assert "d = " in emb.describe()


def test_unseen_query_texts_are_embedded_on_the_fly(text):
    emb = HandcraftedEmbedding(text, **WS)
    with pytest.warns(UserWarning, match="no task-type label"):
        E = emb(["A brand new query that is not in the data?", text.queries[0]])
    assert E.shape == (2, emb.dim) and (E[0, :emb.n_task_dims] == 0).all() and np.allclose(E[1], emb(text.queries)[0])


# ---------------------------------------------------------------- the fit contract, through the harness

@pytest.mark.parametrize("name", list(VARIANTS))
def test_every_variant_runs_through_evaluate(text, name):
    fit = VARIANTS[name](text, **WS)
    embed = fit(text.models[:-1])  # the pool is ignored (frozen)
    assert np.array_equal(embed(text.queries), fit(text.models)(text.queries))
    res = evaluate(text, fit, tune_k=True, k_grid=(5, 20, 50), n_boot=0, n_lambdas=50)
    assert np.isfinite(res["gain"]) and 0 < res["A"] <= 1 and res["k"] in (5, 20, 50)
    unseen = evaluate(text, fit, new_model="model2", n_probes=10, seed=1, n_boot=0, n_lambdas=50)
    assert len(unseen["probes"]) == 10 and np.isfinite(unseen["gain_same_probes"])


def test_level_2_beats_single_best_when_quality_depends_on_the_subdomain(text):
    kw = dict(tune_k=True, k_grid=(20, 50, 100), n_boot=0, n_lambdas=100)
    assert evaluate(text, fit_task_type_only(text, levels=(2,)), **kw)["gain"] > 0
    assert evaluate(text, fit_task_type_only(text, levels=(1, 2)), **kw)["gain"] > 0


def test_task_type_only_matches_the_cluster_embedding_on_the_harness_synthetic_data():
    data, fit = make_data()  # clusters are the themes (ints 0..5, unknown to the taxonomy): use the raw label, level 0
    kw = dict(tune_k=True, k_grid=(50, 100, 200), n_boot=0, n_lambdas=100)
    ours, theirs = evaluate(data, fit_task_type_only(data, levels=(0,)), **kw)["gain"], evaluate(data, fit, **kw)["gain"]
    assert ours > 0.05 and abs(ours - theirs) < 0.03


def test_fit_concat_appends_the_handcrafted_block(text):
    rng = np.random.default_rng(0)
    table = {q: v for q, v in zip(text.queries, rng.normal(size=(len(text.queries), 6)))}
    other = lambda queries: np.array([table[q] / np.linalg.norm(table[q]) for q in queries])  # L2-normalized
    fit = fit_concat(other, text, **WS)
    E = fit(text.models)(text.queries)
    hand = HandcraftedEmbedding(text, **WS)
    assert E.shape == (len(text.queries), 6 + hand.dim) and np.allclose(E[:, :6], other(text.queries))
    tr = E[text.train]
    assert tr[:, :6].var(0).sum() == pytest.approx(tr[:, 6:].var(0).sum())  # balanced
    E2 = fit_concat(other, text, features_weight=2.0, **WS)(None)(text.queries)
    assert np.allclose(E2[:, 6:], 2.0 * hand(text.queries))
    calls = []
    factory = lambda pool: calls.append(pool) or other
    assert fit_concat_factory(factory, text, **WS)(["model0"])(text.queries[:3]).shape == (3, 6 + hand.dim)
    assert calls == [["model0"]]
    assert np.isfinite(evaluate(text, fit, n_boot=0, n_lambdas=50)["gain"])


def test_results_pipeline_mirrors_the_run_loop(text, tmp_path):
    out = Results(text, "fake", root=tmp_path)
    fit = fit_handcrafted(text, **WS)
    out.run("handcrafted", fit, tune_k=True, k_grid=(10, 20), n_boot=0, n_lambdas=50)
    for n in (2, 20):
        out.run("handcrafted", fit, new_model="model3", n_probes=n, seed=0, n_boot=0, n_lambdas=50)
    rows = list(csv.DictReader(open(out.dir / "results.csv")))
    assert [r["embedding"] for r in rows] == ["handcrafted"] * 3 and rows[2]["recovery"] != ""


# ---------------------------------------------------------------- the scripts, on the fake loader

def test_run_and_analyze_scripts_end_to_end(tmp_path, capsys):
    import run_handcrafted
    import analyze_handcrafted
    loader = f"{HERE / 'test_handcrafted.py'}:load_fake_data"
    common = ["--loader", loader, "--tokenizer", "whitespace", "--k-grid", "10", "20", "--n-lambdas", "50", "--n-boot", "0",
              "--n-boot-unseen", "0", "--n-grid", "2", "20", "--probe-seeds", "2"]
    base = common + ["--benchmarks", "fakebench", "--split-seeds", "0", "1", "--results-root", str(tmp_path / "results")]
    run_handcrafted.main(base + ["--dry-run"])
    printed = capsys.readouterr().out
    assert "unseen runs" in printed and "taxonomy coverage" in printed and "level 2: " in printed
    assert not (tmp_path / "results").exists()
    variants = ["task_type_L1", "task_type_L2", "task_type_L12", "handcrafted"]
    run_handcrafted.main(base + ["--new-models", "model2", "model3", "--variants", *variants])
    folders = sorted((tmp_path / "results").glob("*_split*"))
    assert [f.name[-6:] for f in folders] == ["split0", "split1"]
    rows = list(csv.DictReader(open(folders[0] / "results.csv")))
    assert len(rows) == 4 + 2 * 4 * 2 * 2  # 4 seen + (2 new models x 4 variants x 2 budgets x 2 seeds)
    assert {r["embedding"] for r in rows} == set(variants)

    analyze_handcrafted.main(["--results-root", str(tmp_path / "results"), "--out", str(tmp_path / "analysis"),
                              "--diagnostics", "--loader", loader, "--benchmark", "fakebench", "--tokenizer", "whitespace"])
    out = tmp_path / "analysis"
    assert {p.name for p in out.iterdir()} >= {"seen_table.csv", "seen_table.md", "unseen_table.csv", "A_unseen_curves.csv",
                                             "rq1a_ratio.csv", "probes_to_target.csv", "figures",
                                             "stats_correlation_fakebench.csv", "stats_correlation_fakebench.png",
                                             "stats_explained_variance_fakebench.png"}
    assert len(list((out / "figures").glob("*.png"))) >= 4 + 8 + 1  # curves, gain vs probes, A_unseen
    ratio = list(csv.DictReader(open(out / "rq1a_ratio.csv")))
    assert {r["task_variant"] for r in ratio} == {"task_type_L1", "task_type_L2", "task_type_L12"}
    assert {r["other"] for r in ratio} == {"handcrafted"}
    printed = capsys.readouterr().out
    assert "Seen-model setting" in printed and "RQ1a ratio" in printed and "Probes to target" in printed and "whitened block" in printed

    # Level 1 only: the level-2 variants are skipped, the others run
    run_handcrafted.main(common + ["--benchmarks", "fakebench_l1only", "--split-seeds", "0", "--new-models", "model3",
                                   "--variants", "task_type_L1", "task_type_L2", "handcrafted", "--results-root", str(tmp_path / "l1")])
    rows = list(csv.DictReader(open(next((tmp_path / "l1").glob("*_split0")) / "results.csv")))
    assert {r["embedding"] for r in rows} == {"task_type_L1", "handcrafted"}
    assert "task_type_L2: skipped" in capsys.readouterr().out

    # finer labels from a CSV (the offline classifier's output) when the data has none
    labels_csv = tmp_path / "levels.csv"
    data = load_fake_data("fakebench_l1only")
    with open(labels_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["query", "task_level2"])
        for q, t in zip(data.queries[:-10], data.theme[:-10]):  # the last 10 queries stay unlabeled
            w.writerow([q, f"sub_{t}"])
    run_handcrafted.main(common + ["--benchmarks", "fakebench_l1only", "--split-seeds", "0", "--skip-unseen",
                                   "--variants", "task_type_L2", "--level-labels", str(labels_csv), "--results-root", str(tmp_path / "csv")])
    printed = capsys.readouterr().out
    assert "L2: " in printed and "10 of" in printed and "unlabeled" in printed

    # replay mode: one results folder per release event, with an epoch.json
    run_handcrafted.main(common + ["--benchmarks", "fakebench", "--split-seeds", "0", "--timeline", "replay", "--variants", "task_type_L1",
                                   "--results-root", str(tmp_path / "replay")])
    folders = sorted((tmp_path / "replay").glob("*_split0"))
    assert len(folders) == 2 and all((f / "epoch.json").exists() for f in folders)  # events 2, 3 (0 and 1 have no pool to route among)


def test_run_script_explains_a_missing_loader():
    import run_handcrafted
    with pytest.raises(SystemExit, match="loader was not found"):
        run_handcrafted.find_load_data("no_such_module_xyz:load_data")
