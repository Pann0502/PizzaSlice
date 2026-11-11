/* Draft case 10. Recursion whose base case holds the error. The recursive call
 * count is dynamic - treated like a loop, not unrolled.
 *
 * Note: foo() never returns normally. It either recurses (a true) or errors
 * (a false, which aborts in reach_error). So main's if(b) after the call is
 * UNREACHABLE. The draft comment "we can still put wps for this one" does not
 * hold here - flagged in the sidecar. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

static void foo(void) {
    int a = __VERIFIER_nondet_int();
    if (a) {                 // B1
        foo();               /* recursive call: dynamic depth, left be */
    } else {
        reach_error();       // T
    }
}

int main(void) {
    foo();                   // C1
    int b = __VERIFIER_nondet_int();
    if (b) {                 // B2 - unreachable: foo() never returns
        /* ... */
    }
    return 0;
}
