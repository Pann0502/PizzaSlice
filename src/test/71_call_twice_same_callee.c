/* Draft case 8 - "important test, bc this is why it's nicer to split by
 * witnesses". The same callee holds the error and is called twice. The error
 * can be hit on either call. Two witnesses, differing only in the call site. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

static void foo(void) {
    int a = __VERIFIER_nondet_int();
    if (a) {                 // B1
        reach_error();       // T
    }
}

int main(void) {
    foo();                   // C1
    foo();                   // C2
    return 0;
}
