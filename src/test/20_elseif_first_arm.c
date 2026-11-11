/* Draft case 3, error in the first arm. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int a = __VERIFIER_nondet_int();
    int b = __VERIFIER_nondet_int();
    if (a) {                 // B1
        reach_error();       // T
    } else if (b) {          // B2
        /* ... */
    } else {
        /* ... */
    }
    return 0;
}
