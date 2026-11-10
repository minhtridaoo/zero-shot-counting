# CS331 workspace — hướng dẫn cho assistant

When starting or resuming work in this checkout:

1. Read `BAT_DAU_SESSION_MOI.md` (current state + next actions), then the latest entry of `WORKLOG.md` (newest at top) and `roadmap/KE_HOACH_HOAN_THANH_20261110.md` (plan to 02/12). `README.md` maps the folders. Check actual Git status (remote `github.com/minhtridaoo/zero-shot-counting`) and artifacts before reporting progress.
2. Continue the first unfinished action in `BAT_DAU_SESSION_MOI.md`. Plans and existing code are not evidence that a run succeeded.
3. CountGD++ is the counting model; CLIP is only an auxiliary crop/exemplar scorer. The main improvement is branch P (CLIP-verified pseudo-exemplars) plus variant T; branch R is a fallback. Decisions D1–D10 (`reports/KE_HOACH_TIEP_THEO_20261105.md`) are fixed; the final configuration is chosen on dev by rule D9, and the test set is run once.
4. Ask Trí before running evaluator/self-test/inference/training or other experiments. Reading files, preparing code/plans and updating documentation can proceed.
5. Do not modify locked data, the freeze, original predictions, or `.py` files whose hashes are recorded in audits; add new scripts instead. Do not sign or mark human approvals on someone else's behalf.
6. After each work session, add a WORKLOG entry (top) and update `BAT_DAU_SESSION_MOI.md`. Old documents live in `quá khứ/`; do not edit them as if current.
7. Preserve unrelated local changes; snapshot before pulling overlapping edits; never reapply the old recovery stash.

Communicate in simple Vietnamese with concrete next steps.
