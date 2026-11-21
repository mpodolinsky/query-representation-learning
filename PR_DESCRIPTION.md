Adds the proposal's handcrafted, frozen, concatenated and learned query representations to the existing kNN routing harness. Learned representations use profile regression or contrastive training on permitted training-model scores, with early stopping inside the training split.

The complete original grid covers both benchmarks, every unseen release, three splits and training/probe seeds: 25,056 main evaluations and 300,672 sensitivity evaluations. Reviewable protocols, coverage manifests, metrics, summaries, probes-to-target, figures and compressed sensitivity rows are committed in `results_summary/`.

Review fixes:
- Preserve the unweighted `combined` baseline and report `combined_balanced` separately, with a training-only scalar that equalizes average squared block norms. Its matching full grid adds 4,176 main and 50,112 sensitivity evaluations. Final-pool mean A (unweighted → balanced): LLMRouterBench 0.7385 → 0.7372; RouterBench 0.7731 → 0.7746. Neither is claimed to be the best concatenation.
- Name `michal-harness/router.py` as the reference. Real-data integration tests compare neighbor/probe predictions, A, gain and paired-bootstrap intervals in seen, unseen and single-incumbent settings.
- State fixed k=10 for single-incumbent unseen pools beside the unseen results.

Validation: `python -m pytest -q preproc michal-harness learned` — 91 passed, 1 skipped (external raw-data rebuild inputs unavailable). Bundle tests verify file hashes, exact coverage and regenerated summaries/probes-to-target. No files in `michal-harness/` or `preproc/` changed.
