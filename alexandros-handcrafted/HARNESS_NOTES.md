# Notes for Michal (harness) and Arman (data)

Things I ran into while plugging the handcrafted representation into `michal-harness/`. Nothing under
`michal-harness/` was changed; these are proposals to raise.

## For Michal

1. **The task-type label cannot travel with the query.** `evaluate` calls `fit(pool)(data.queries)` with a plain
   `list[str]`, so an embedding that needs a per-query label (`data.theme`) has to look queries up by their text.
   My factories take `data` and build a `text -> theme` dictionary from `data.theme`. This works but is fragile:
   two queries with the same text and different labels collapse to one row (I warn and keep the first label), and
   any query text not in `data.queries` gets an all-zero one-hot block.
   Proposal (small, backwards compatible): have `evaluate` pass the row indices too, e.g.
   `embed(queries, idx=None)` where `idx` are the positions in `data.queries`, or call `embed(data.queries)` and
   let the contract say "the full `data.queries` list, in order", so positional lookup is legal. Either is a
   two-line change in `evaluate`; my `HandcraftedEmbedding.__call__` would then index its precomputed matrix
   directly. Until then the dictionary lookup is correct as long as query texts are unique.

2. **`select_k` divides by zero when the pool has one model.** In a replayed timeline the second release event
   leaves a one-model pool for the unseen run (`pool = models released so far minus the new model`), and
   `lambda_grid` divides by `np.ptp(cost) == 0`. Nothing crashes (numpy warns), but the tuned `k` is meaningless.
   My run script skips release events whose pool minus the new model has fewer than two models. A guard in
   `select_k` (or `evaluate`) that raises a clear error, or skips tuning, would make this explicit.

3. **Task-type-only has few distinct points.** With the one-hot label alone, every query of a type sits at the
   same point, so the `k` nearest neighbors are an arbitrary subset (scikit-learn's tie order) of that type.
   The right estimator for this representation is the per-type mean, which is the `k -> infinity` limit within a
   type. The grid tops out at 200, so for RQ1a it may be worth extending `k_grid` (the harness already warns
   when the best `k` is at the grid edge; on the synthetic data it picks 200 for this variant). I did not change
   the default grid in my runs; `--k-grid` is a CLI argument of `run_handcrafted.py`.

4. **Results folders are named by the second.** In replay mode I create one `Results` per release event, and two
   events for the same split within one second collide (`mkdir` without `exist_ok`). I retry after a second;
   adding a counter or microseconds to the folder name would remove the need.

5. **Per-epoch pools and costs are not in `Data`.** For the replayed timeline I subset `Data` myself
   (`run_handcrafted.data_at_epoch`: models released up to the event, their columns of `S`, the epoch's cost) and
   write an `epoch.json` next to `results.csv`. If the harness grows a notion of epoch, I will switch to it.

6. **`select_k` is recomputed in every unseen run, though it only depends on the embedding, the pool and `data.val`,
   never on the probes.** With 8 budgets x 5 seeds per held-out model that is 40 identical tunings (9 kNN searches
   and a 200-resample bootstrap each). My run script calls `router.select_k` once per (variant, held-out model)
   and passes the result as `k=k, tune_k=False` to every budget x seed run; the numbers are identical (the test
   `test_k_tuned_once_per_held_out_model_matches_tune_k_inside_every_run` checks it), and `k_tuning.csv` next to
   `results.csv` records how each k was obtained. A cache keyed on (`new_model`, `k_grid`) inside `evaluate`, or a
   `k` returned by a first call that the caller can pass back, would make this unnecessary. Related: the
   `tune_k` column of `results.csv` is then `False` for those runs although the k was tuned.

7. **`select_k` only reports the edge case as a printed warning.** To record which runs hit the edge of the grid I
   capture stdout around the call and parse the message (`run_handcrafted.Tuning`). Returning the per-k validation
   areas (or the raw best k) alongside the chosen k would let callers record it properly.

8. **`meta.json`'s `-dirty` flag also fires on untracked files** (`git status --porcelain` lists them), so an
   untracked analysis folder or a stray log marks every run dirty. `--untracked-files=no` would make the flag mean
   "uncommitted changes to tracked files", which is what one wants to know when matching results to a commit.

## For Arman (what my code assumes about `load_data`)

See the checklist in `README.md`, "Open assumptions about the data". The short version: `load_data(benchmark,
split_seed=0) -> router.Data` with `theme` filled (one task-type label per query), unique query texts, `models`
in release order (or a `release_order` / `release_date` attribute), and either one `cost` vector or a
`cost_by_epoch` matrix of shape (n_epochs, n_models).
