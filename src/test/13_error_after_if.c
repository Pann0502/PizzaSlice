/* The "..." placeholder resolved to: error AFTER the if, at the merge point.
 * Both branches reach the target, so the branch does not gate it.
 * Design choice: leave B1 free (one witness, no branching waypoint) rather
 * than emit one witness per outcome. See README open question 1. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int a = __VERIFIER_nondet_int();
    if (a) {             // B1 - does not gate the error
        /* ... */
    }
    reach_error();       // T - reached on both edges of B1
    return 0;
}
