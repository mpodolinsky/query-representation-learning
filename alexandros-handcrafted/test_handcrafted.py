"""End-to-end plumbing tests for the handcrafted representation, on fake data only (no benchmark data, no network
beyond tiktoken's cached BPE table; the whitespace tokenizer is used where the count matters).
Run from this folder:  python -m pytest -q"""
import csv
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
from handcrafted import (FEATURE_NAMES, FEATURES, HandcraftedEmbedding, fit_concat, fit_concat_factory,  # noqa: E402
                         fit_handcrafted, fit_stats_only, fit_task_type_only, get_tokenizer, query_stats)

THEMES = {
    "math": ["Solve for x: {a}x + {b} = {c}.", "What is the integral of x^{a} from 0 to {b}?",
             "Compute {a} * {b} - {c} and explain each step.", "Prove that the sum of the first {a} odd numbers is a square."],
    "code": ["Write a Python function:\n```python\ndef f(xs):\n    return sum(xs) / {a}\n```\nFix the bug for empty lists.",
             "Why does `for (int i = 0; i < {a}; i++) {{ total += arr[i]; }}` segfault?",
             "Convert this SQL to pandas: SELECT name FROM users WHERE age > {a};"],
    "biology": ["Describe how mitochondria produce ATP in eukaryotic cells.",
                "What role does mRNA play in protein synthesis? Give {a} examples.",
                "Explain the difference between mitosis and meiosis."],
    "history": ["Who was the ruler of France in {a}? What happened to them?",
                "Summarize the causes of the First World War in a few sentences.",
                "WHY DID THE ROMAN REPUBLIC COLLAPSE? Answer briefly."],
}


def make_text_data(Q=600, M=4, seed=0, split_seed=0):
    """Tiny fake dataset with real-looking text, a task type per query and scores that depend on the task type,
    built from the harness's own `Data` so the plumbing is exercised exactly as it will be with Arman's data."""
    rng = np.random.default_rng(seed)
    names = list(THEMES)
    theme_id = rng.integers(len(names), size=Q)
    queries = [rng.choice(THEMES[names[t]]).format(a=rng.integers(2, 99), b=rng.integers(2, 99), c=rng.integers(2, 999))
               + f" (query {i})" for i, t in enumerate(theme_id)]  # unique texts, like real benchmark queries
    quality = np.clip(np.linspace(0.3, 0.7, M)[:, None] + rng.uniform(-0.3, 0.3, (M, len(names))), 0, 1)
    S = (rng.random((Q, M)) < quality[:, theme_id].T).astype(float)
    order = np.random.default_rng(100 + split_seed).permutation(Q)
    a, b = int(0.6 * Q), int(0.7 * Q)
    return Data(queries, [f"model{m}" for m in range(M)], S, np.geomspace(1, 20, M), train=order[:a], val=order[a:b],
                test=order[b:], theme=np.array(names)[theme_id], split_seed=split_seed)


def load_fake_data(benchmark, split_seed=0):
    """Stands in for Arman's `load_data(benchmark, split_seed)` so run_handcrafted.py can be exercised."""
    return make_text_data(seed=hash(benchmark) % 1000, split_seed=split_seed)


@pytest.fixture(scope="module")
def text():
    return make_text_data()


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


# ---------------------------------------------------------------- standardization and the one-hot block

def test_stats_are_standardized_on_train_only(text):
    emb = HandcraftedEmbedding(text, use_task_type=False, **WS)
    E = emb(text.queries)
    assert E.shape == (len(text.queries), len(FEATURES))
    tr = E[text.train]
    varying = tr.std(0) > 1e-9
    assert np.allclose(tr.mean(0), 0, atol=1e-9) and np.allclose(tr.std(0)[varying], 1, atol=1e-6)
    assert np.abs(E).max() <= emb.clip
    # the test split does not influence the scaler
    other = Data(text.queries[:], text.models, text.S, text.cost, text.train, text.val, text.test[:10], text.theme)
    assert np.allclose(HandcraftedEmbedding(other, use_task_type=False, **WS).mean_, emb.mean_)


def test_task_type_only_is_a_one_hot_over_training_categories(text):
    embed = fit_task_type_only(text)(text.models)
    E = embed(text.queries)
    assert E.shape == (len(text.queries), 4) and set(np.unique(E)) == {0.0, 1.0} and (E.sum(1) == 1).all()
    assert embed.feature_names == ["task=biology", "task=code", "task=history", "task=math"]
    assert [embed.categories[j] for j in E.argmax(1)] == list(text.theme)
    # a category absent from the training split gets an all-zero row (and no column)
    theme = np.array(text.theme, dtype=object)
    theme[text.test[:5]] = "unknown_type"
    E2 = fit_task_type_only(Data(text.queries, text.models, text.S, text.cost, text.train, text.val, text.test, theme))(None)(text.queries)
    assert E2.shape[1] == 4 and (E2[text.test[:5]] == 0).all()


def test_duplicated_texts_with_different_labels_warn_and_keep_the_first(text):
    queries = list(text.queries)
    queries[text.train[1]] = queries[text.train[0]]  # same text, (almost surely) another theme
    theme = np.array(text.theme, dtype=object)
    theme[text.train[1]] = "other"
    dup = Data(queries, text.models, text.S, text.cost, text.train, text.val, text.test, theme)
    with pytest.warns(UserWarning, match="duplicated query texts"):
        E = fit_task_type_only(dup)(None)(queries)
    assert np.array_equal(E[text.train[0]], E[text.train[1]])  # one text, one row: the label cannot be told apart


def test_theme_is_required_for_the_task_type_variants(text):
    no_theme = Data(text.queries, text.models, text.S, text.cost, text.train, text.val, text.test, theme=None)
    with pytest.raises(ValueError, match="theme"):
        fit_task_type_only(no_theme)
    fit_stats_only(no_theme, **WS)  # fine without labels


def test_balanced_weight_equalizes_the_blocks_and_float_weight_is_used_as_is(text):
    emb = HandcraftedEmbedding(text, **WS)
    E = emb(text.queries)[text.train]
    C = len(emb.categories)
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
    assert E.shape == (2, emb.dim) and (E[0, :4] == 0).all() and np.allclose(E[1], emb(text.queries)[0])


# ---------------------------------------------------------------- the fit contract, through the harness

@pytest.mark.parametrize("factory", [fit_task_type_only, fit_stats_only, fit_handcrafted])
def test_fit_contract_and_evaluate(text, factory):
    fit = factory(text, **WS) if factory is not fit_task_type_only else factory(text)
    embed = fit(text.models[:-1])  # the pool is ignored (frozen)
    assert np.array_equal(embed(text.queries), fit(text.models)(text.queries))
    res = evaluate(text, fit, tune_k=True, k_grid=(5, 20, 50), n_boot=0, n_lambdas=50)
    assert np.isfinite(res["gain"]) and 0 < res["A"] <= 1 and res["k"] in (5, 20, 50)
    unseen = evaluate(text, fit, new_model="model2", n_probes=10, seed=1, n_boot=0, n_lambdas=50)
    assert len(unseen["probes"]) == 10 and np.isfinite(unseen["gain_same_probes"])


def test_task_type_beats_single_best_when_quality_depends_on_task_type(text):
    res = evaluate(text, fit_task_type_only(text), tune_k=True, k_grid=(20, 50, 100), n_boot=0, n_lambdas=100)
    assert res["gain"] > 0


def test_task_type_only_matches_the_cluster_embedding_on_the_harness_synthetic_data():
    data, fit = make_data()  # clusters are the themes, so the one-hot theme carries the same routing information
    kw = dict(tune_k=True, k_grid=(50, 100, 200), n_boot=0, n_lambdas=100)
    ours, theirs = evaluate(data, fit_task_type_only(data), **kw)["gain"], evaluate(data, fit, **kw)["gain"]
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
    common = ["--benchmarks", "fakebench", "--loader", loader, "--tokenizer", "whitespace", "--k-grid", "10", "20",
              "--n-lambdas", "50", "--n-boot", "0", "--n-boot-unseen", "0", "--n-grid", "2", "20", "--probe-seeds", "2"]
    base = common + ["--split-seeds", "0", "1", "--results-root", str(tmp_path / "results")]
    run_handcrafted.main(base + ["--dry-run"])
    assert "unseen runs" in capsys.readouterr().out and not (tmp_path / "results").exists()
    run_handcrafted.main(base + ["--new-models", "model2", "model3", "--variants", "task_type", "handcrafted"])
    folders = sorted((tmp_path / "results").glob("*_split*"))
    assert [f.name[-6:] for f in folders] == ["split0", "split1"]
    rows = list(csv.DictReader(open(folders[0] / "results.csv")))
    assert len(rows) == 2 + 2 * 2 * 2 * 2  # 2 seen + (2 new models x 2 variants x 2 budgets x 2 seeds)

    analyze_handcrafted.main(["--results-root", str(tmp_path / "results"), "--out", str(tmp_path / "analysis")])
    out = tmp_path / "analysis"
    assert {p.name for p in out.iterdir()} >= {"seen_table.csv", "seen_table.md", "unseen_table.csv", "A_unseen_curves.csv",
                                             "rq1a_ratio.csv", "probes_to_target.csv", "figures"}
    assert len(list((out / "figures").glob("*.png"))) >= 1 + 2 + 1  # curves, gain vs probes, A_unseen
    printed = capsys.readouterr().out
    assert "Seen-model setting" in printed and "RQ1a ratio" in printed and "Probes to target" in printed

    # replay mode: one results folder per release event, with an epoch.json
    run_handcrafted.main(common + ["--split-seeds", "0", "--timeline", "replay", "--variants", "task_type",
                                   "--results-root", str(tmp_path / "replay")])
    folders = sorted((tmp_path / "replay").glob("*_split0"))
    assert len(folders) == 2 and all((f / "epoch.json").exists() for f in folders)  # events 2, 3 (0 and 1 have no pool to route among)


def test_run_script_explains_a_missing_loader():
    import run_handcrafted
    with pytest.raises(SystemExit, match="loader was not found"):
        run_handcrafted.find_load_data("no_such_module_xyz:load_data")
