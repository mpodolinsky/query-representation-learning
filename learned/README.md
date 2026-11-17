# Learned query representations

Implements the proposal's learned embedding and evaluates it using the existing kNN harness.
The sentence encoder is frozen; only the MLP and (for regression) its prediction head are trained.
No LLM responses or API calls are needed: supervision comes from the committed score tables.

## Setup

From the repository root, with Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r learned/requirements.txt
```

The first run downloads `sentence-transformers/all-MiniLM-L6-v2`. Subsequent runs reuse
the encoder and sentence-vector cache in `results/learned/cache/`.

## First milestone: seen-model regression

```bash
python -m learned.experiments
```

Defaults: LLMRouterBench, split 0, training seed 0, frozen baseline and learned regression,
up to 50 epochs, early-stopping patience 5, validation-tuned k, 500 log-spaced cost weights
plus zero, and 1,000 bootstrap resamples. The harness reports the single-best and oracle
alongside each representation. Results are saved under `results/learned/runs/<timestamp>/`.

## Compare both objectives and the proposal baselines

```bash
python -m learned.experiments \
  --representations task_type handcrafted frozen combined regression contrastive \
  --instances 11 --probe-seeds 0 1 2
```

This runs the final-pool seen comparison, then the matched seen/unseen comparison for
LLMRouterBench instance 11 (GLM-4.6). Default probe budgets: 1, 5, 10, 20, 50, 100, 500.
Use `--probe-budgets` to change them (positive integers no larger than the training split).

For all release instances on both benchmarks, all three splits and multiple seeds:

```bash
python -m learned.experiments \
  --benchmarks llmrouterbench routerbench --splits 0 1 2 \
  --training-seeds 0 1 2 --probe-seeds 0 1 2 \
  --representations task_type handcrafted frozen combined regression contrastive \
  --all-instances
```

This is the full experiment grid and can take substantially longer. Start with the first milestone.
Individual instance numbers differ across benchmarks; use `--all-instances` for the combined run.

## Training

- Input: L2-normalized frozen sentence embeddings, with queries truncated at 256 encoder tokens.
- Architecture: input → Linear(128) → ReLU → Linear(64) → L2 normalization.
- **Regression:** a sigmoid linear head predicts scores across the allowed models; minimize MSE.
  Only the normalized embedding is passed to kNN, not the predicted scores.
- **Contrastive:** a pair is positive if its mean squared quality-profile difference is <= 0.1.
  Minimize squared embedding distance for positives and `max(0, 1-distance)^2` for negatives.
  Average positive and negative terms separately. Pairs are formed inside minibatches;
  self-pairs are excluded. Threshold and margin are configurable.
- Adam, learning rate 0.001, batch size 128. Training seed controls initialization, shuffling
  and the internal early-stopping split. Default execution is CPU with four PyTorch threads.
- Ten percent of `data.train` is held out for early stopping on the training objective.
  Neither `data.val` nor `data.test` supplies training or early-stopping labels.
- In unseen runs, the new model's scores are excluded from all embedding supervision.
  Its probe scores are used only by the existing kNN estimator. One checkpoint is reused
  across probe budgets and probe seeds. Seen and unseen models are trained separately.
- The existing harness tunes k on `data.val`. With a single incumbent it cannot tune k
  by routing performance, so the unseen run uses fixed k=10 (configurable with `--k`).
- The default text is the bare query, following preprocessing. Theme-based baselines use
  benchmark-provided labels, so their lookup accepts only benchmark queries; the learned
  embedding and frozen sentence encoder can embed arbitrary new text.

Handcrafted features are one-hot theme, character count, lexical token count and line count,
standardized using training queries. `combined` concatenates them with frozen sentence vectors.
Task-type-only uses the one-hot theme. These are the proposal's non-learned baselines.

## Outputs and metrics

- `metrics.csv`: each run's A, A_single_best, gain, gain_abs, same-probe gain, bootstrap interval,
  selected k, model/setting, split/training/probe seeds, and task-type recovery where available.
- `probes_to_target.csv`: smallest **tested** budget with `A_unseen(n) >= 0.9 * A_seen`.
  Calculated separately per representation, release instance, split, training seed and probe seed.
  The status is `not reached` if no tested budget meets the target. This follows the proposal's
  A-based definition, not the harness's gain-based `recovery`.
- `task_type_recovery`: `A_task / A_learned` for matched seen or unseen runs. Include `task_type`
  alongside learned representations to calculate it; otherwise it is left blank.
- `summary.csv`: mean and standard deviation across the requested seeds, as descriptive spread.
  Per-run bootstrap intervals remain in `metrics.csv`; they measure test-query sampling noise.
- Under each benchmark/split/instance/training-seed folder: the harness's saved curves, quality
  estimates, probes and metadata, plus cost-quality and A-versus-probes plots.
- The cache contains sentence/baseline/learned embeddings and each checkpoint's `model.pt`
  and `training.json` (configuration, allowed models, training/early-stopping indices and loss history).

`instance=-1` in the tables denotes the final-pool seen comparison. Each release instance gets
its own seen reference with exactly the same candidate pool. Dotted plot lines show that reference.
Gains and areas should be compared within matching benchmark/pool settings.

All generated files live under the existing gitignored `results/` directory.

## Python interface

```python
from preproc.data import load_data
from learned.features import SentenceFeatures
from learned.train import TrainConfig, make_fit

data = load_data("llmrouterbench", instance=11)
features = SentenceFeatures(data.queries, "results/learned/cache")
fit = make_fit(data, features, TrainConfig(objective="regression"),
               "results/learned/cache/checkpoints")
# Pass fit to router.evaluate or router.Results.run as in michal-harness/README.md.
# The harness supplies train_models with the held-out model removed.
```

Tests run offline without downloading an encoder:

```bash
python -m pytest -q preproc michal-harness learned
```
