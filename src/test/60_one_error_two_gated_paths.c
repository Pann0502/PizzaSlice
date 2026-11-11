/* The completeness star. A SINGLE reach_error(), factored into a helper, is
 * reached from two different branch combinations. The complete set needs two
 * witnesses. This is the case that makes "complete set of witnesses" non-trivial
 * and that plain program slicing handles poorly. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

static void err(void) {
    reach_error();           // T
}

int main(void) {
    int a = __VERIFIER_nondet_int();
    int b = __VERIFIER_nondet_int();
    int c = __VERIFIER_nondet_int();
    if (a) {                 // B1
        if (b) {             // B2
            err();           // C1
        }
    } else {
        if (c) {             // B3
            err();           // C2
        }
    }
    return 0;
}
