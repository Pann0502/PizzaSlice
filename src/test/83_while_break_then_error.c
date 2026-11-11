/* An infinite loop with a conditional break, then the error after the loop.
 * Reaching the error requires leaving the loop, i.e. taking the break. The
 * break is a branch inside a loop that gates post-loop code. This is the least
 * obvious loop case - see README q4. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    while (1) {
        int a = __VERIFIER_nondet_int();
        if (a) {                 // B1 - break gates loop exit
            break;
        }
    }
    reach_error();               // T - only reached after the break
    return 0;
}
