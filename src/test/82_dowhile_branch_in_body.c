/* do-while variant. The body runs at least once, unlike for/while which may
 * run zero times. The branch is still inside a loop, so the same no-unroll
 * rule applies. Included to check the tool recognises do-while as a loop. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int n = __VERIFIER_nondet_int();
    int i = 0;
    do {
        int a = __VERIFIER_nondet_int();
        if (a) {                 // B1 - inside the loop
            reach_error();       // T
        }
        i++;
    } while (i < n);
    return 0;
}
