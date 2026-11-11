/* Switch: the error lives in exactly one case. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int x = __VERIFIER_nondet_int();
    switch (x) {             // B1
        case 1:
            reach_error();   // T
            break;
        case 2:
            break;
        default:
            break;
    }
    return 0;
}
