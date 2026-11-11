/* Stretch case: mutual recursion (plain calls, no function pointers). The error
 * is in is_even's base case, reached when the original argument is even.
 * Depth is dynamic and not unrolled. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern unsigned int __VERIFIER_nondet_uint(void);

static int is_even(unsigned int n);

static int is_odd(unsigned int n) {
    if (n == 0u) {               // B_odd
        return 0;
    }
    return is_even(n - 1u);      // C_oe
}

static int is_even(unsigned int n) {
    if (n == 0u) {               // B_even
        reach_error();           // T
        return 1;
    }
    return is_odd(n - 1u);       // C_eo
}

int main(void) {
    unsigned int n = __VERIFIER_nondet_uint();
    is_even(n);                  // C1
    return 0;
}
