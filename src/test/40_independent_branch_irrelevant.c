/* Two sequential, independent branches. Only the second gates the error.
 * The tool must not take the cross-product: B1 is irrelevant. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int a = __VERIFIER_nondet_int();
    int b = __VERIFIER_nondet_int();
    if (a) {                 // B1 - does not gate the error
        /* ... */
    }
    if (b) {                 // B2 - gates the error
        reach_error();       // T
    }
    return 0;
}
