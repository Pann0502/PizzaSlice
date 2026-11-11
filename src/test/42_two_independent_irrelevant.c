/* Two non-gating branches, error after both merges. Neither gates T.
 * Guards against a 4-way cross-product. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int a = __VERIFIER_nondet_int();
    int c = __VERIFIER_nondet_int();
    if (a) {                 // B1 - does not gate
        /* ... */
    }
    if (c) {                 // B2 - does not gate
        /* ... */
    }
    reach_error();           // T
    return 0;
}
