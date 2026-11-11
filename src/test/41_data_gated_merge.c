/* A branch writes a value; a later guard tests that value. The first branch
 * therefore DOES gate the error, but through data flow, not control nesting.
 * Reaching the error needs x == 1, which needs a true. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int a = __VERIFIER_nondet_int();
    int x;
    if (a) {                 // B1 - controls x
        x = 1;
    } else {
        x = 2;
    }
    if (x == 1) {            // B2 - derived from B1
        reach_error();       // T
    }
    return 0;
}
