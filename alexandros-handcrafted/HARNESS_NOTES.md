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

## For Arman (what my code assumes about `load_data`)

See the checklist in `README.md`, "Open assumptions about the data". The short version: `load_data(benchmark,
split_seed=0) -> router.Data` with `theme` filled (one task-type label per query), unique query texts, `models`
in release order (or a `release_order` / `release_date` attribute), and either one `cost` vector or a
`cost_by_epoch` matrix of shape (n_epochs, n_models).
