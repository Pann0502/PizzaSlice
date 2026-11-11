/* Draft case 5. A loop runs, then a branch gates the error AFTER the loop.
 * The loop itself is not a splitting point. Only the post-loop branch is. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int n = __VERIFIER_nondet_int();
    for (int i = 0; i < n; i++) {   /* loop: left be, not a branch */
        /* ... */
    }
    int a = __VERIFIER_nondet_int();
    if (a) {                         // B1
        reach_error();               // T
    }
    return 0;
}
