/* Baseline: the error is reached on every path. No branching at all.
 * The complete set is a single witness with only a target waypoint. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }

int main(void) {
    reach_error();   // T
    return 0;
}
