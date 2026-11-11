# Witness-splitting test suite

Test cases for a tool that splits a reachability verification task into a
**complete set of software violation witnesses**, using **branching** and
**target** waypoints. The tool does **not** unroll loops or recursion.

- Property: reachability of a single `reach_error()` call.
- Each path that reaches `reach_error()` must match at least one witness in
  the set (completeness). The set should also avoid splitting on branches that
  do not gate the error (no over-splitting).
- Loops and recursion are "left be": the tool does not enumerate iteration
  counts or recursion depths.

## Layout

- `tests/NN_name.c` — one small, self-contained C program per test. The
  SV-COMP preamble (`reach_error`, nondet declarations) is inlined at the top of
  each file, so a file can be fed to a verifier on its own.
- `tests/NN_name.witnesses.txt` — the expected complete witness set (sidecar),
  written in a format-agnostic notation so it does not bake in a serialization.

Each `.c` file marks the relevant program points with end-of-line comments:

- `// Bk` — a branch (if / else-if / switch) that may become a branching waypoint.
- `// Ck` — a call site, when the witness must say *which* call it means.
- `// T`  — the target (`reach_error()` site).

## Sidecar notation

```
count: N                      number of witnesses in the complete set
W1: <waypoint> -> ... -> target(T)
```

Waypoints:

- `branch(Bk=T)` / `branch(Bk=F)` — condition at `Bk` was true / false.
- `case(Bk=v)` — switch selector took case `v`, or `default`.
- `enter(f@Ck)` — entered function `f` at call site `Ck` (context).
- `target(T)` — the reach_error site.

`count: 0` means the complete set is empty (the error is unreachable).
A witness with only `target(T)` means "reaches the error on every path; no
branch needs pinning".

## Test index

| File | Exercises | #witnesses | Key point |
|------|-----------|-----------:|-----------|
| 01_unconditional_error | no branching | 1 | baseline: target only, no branch waypoint |
| 02_no_error | empty program | 0 | completeness of the empty set |
| 03_dead_branch_error | `if(0){error}` | 0 | unreachable target, constant condition |
| 04_first_statement_error | error is first stmt | 1 | target at entry |
| 10_if_then_error | error in `then` | 1 | `branch(B1=T)` |
| 11_if_else_error | error in `else` | 1 | `branch(B1=F)` |
| 12_if_then_error_with_else | `then` error, else present | 1 | else branch not in any witness |
| 13_error_after_if | error after the merge | 1 | **do not over-split**: branch left free |
| 20_elseif_first_arm | else-if chain, arm 1 | 1 | `branch(B1=T)` |
| 21_elseif_middle_arm | else-if chain, arm 2 | 1 | else-if desugars to nesting: `B1=F, B2=T` |
| 22_elseif_else_arm | else-if chain, else | 1 | `B1=F, B2=F` |
| 30_nested_both_gate | `if(a){if(b){error}}` | 1 | `B1=T, B2=T` |
| 31_nested_inner_else | error in inner else | 1 | `B1=T, B2=F` |
| 40_independent_branch_irrelevant | `if(a){} if(b){error}` | 1 | a does not gate the error |
| 41_data_gated_merge | branch value flows to a later guard | 1 | pin the controllable branch, not the derived one |
| 42_two_independent_irrelevant | two non-gating branches | 1 | no cross-product |
| 50_switch_one_case | error in one case | 1 | `case(B1=1)` |
| 51_switch_fallthrough | error reached by two cases | 2 | fall-through: two witnesses |
| 52_switch_default | error in default | 1 | `case(B1=default)` = complement |
| 60_one_error_two_gated_paths | one error, two gated paths | 2 | the completeness star |
| 61_error_helper_two_callsites | error helper, two call sites | 2 | call-site context in the witness |
| 70_call_error_in_callee | error inside a callee | 1 | `enter(foo), branch, target` |
| 71_call_twice_same_callee | `foo(); foo();` | 2 | why witnesses are nicer: call-site context |
| 72_guarded_call_branch_in_callee | guarded call, branch inside | 1 | caller + callee branches |
| 80_loop_then_gated_error | loop, then gated error | 1 | the loop is not a branch |
| 81_branch_inside_loop | branch inside the loop body | 1 | **design: no in-loop split** |
| 82_dowhile_branch_in_body | do-while body runs once | 1 | do-while variant |
| 83_while_break_then_error | `while(1){..break;}` then error | 1 | **break gates loop exit** |
| 90_recursion_error_in_base | recursion, error in base case | 1 | depth abstracted; see note |
| 91_recursion_error_after | recursion, error after the call | 1 | error unconditional; no branch |
| 92_mutual_recursion_error_in_base | mutual recursion | 1 | stretch; depth abstracted |

## Open design questions (assumptions baked into the sidecars)

These are the places where your draft left the answer open. I picked an answer
for each and marked it in the relevant sidecar. Flip any you disagree with and
the expected outputs change.

1. **Non-gating branches (13, 40, 42).** When a branch does not gate the error
   (both outcomes reach the target, or the error is after the merge), I leave
   it **free** — no branching waypoint, one witness. The alternative is to emit
   one witness per outcome (a cross-product). I chose minimal, free.
2. **Data-gated branches (41).** When a branch sets a value that a later guard
   tests, I pin the **controllable** branch (the `if(a)`), not the derived
   guard. A witness that pins only the derived guard is also sound.
3. **Branch inside a loop (81).** I treat the in-loop branch as **not a
   splitting point** (matches your "ignore this if, bc it's in a loop"). The
   witness has a target waypoint only. Alternative: keep a single branching
   waypoint that is not tied to an iteration count.
4. **Loop-exit / break (83).** A `break` gates whether post-loop code runs, so
   it gates the error, yet it lives in a loop. I treated it like (3): free. This
   is the least obvious call — you may want the break pinned.
5. **Recursion depth (90, 91, 92).** Witnesses abstract over depth: one
   representative branch decision, no per-level pinning. Matches "don't
   calculate, leave it be".
6. **Dead tail after non-returning recursion (90).** In your draft case the
   recursive `foo()` never returns (it recurses or errors), so `main`'s `if(b)`
   after the call is unreachable. The sidecar flags this — it may be a surprise.
7. **Switch default (52).** The default witness is pinned as "selector not in
   the listed cases" — a complement, not a concrete value.

## Not covered (by your choice)

Short-circuit `&&` / `||`, ternary `?:`, `goto`, and function pointers were
excluded. Each hides a branch (`&&`/`?:`) or a target/edge (`goto`, indirect
calls) that an if/switch-only splitter would miss, so they are natural
follow-ups if the scope grows.
