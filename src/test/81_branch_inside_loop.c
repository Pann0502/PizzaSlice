/* Draft case 6 - "try on different kinds of loops" and "ignore this if, bc
 * it's in a loop". The error is inside the loop body behind a branch. Pinning
 * that branch would tie the witness to a specific iteration, which the no-unroll
 * rule forbids. Design choice: leave the in-loop branch free. See README q3. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int n = __VERIFIER_nondet_int();
    for (int i = 0; i < n; i++) {
        int a = __VERIFIER_nondet_int();
        if (a) {                 // B1 - inside the loop
            reach_error();       // T
        }
    }
    return 0;
}
