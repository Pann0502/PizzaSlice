/* Draft case 9. A guard in main gates a call; the callee has its own guarded
 * error. Both branches must be pinned, across the call boundary. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

static void foo(void) {
    int b = __VERIFIER_nondet_int();
    if (b) {                 // B2
        reach_error();       // T
    }
}

int main(void) {
    int a = __VERIFIER_nondet_int();
    if (a) {                 // B1
        foo();               // C1
    }
    return 0;
}
