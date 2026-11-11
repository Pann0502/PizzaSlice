/* Draft case 11. Recursion with no error inside; the single error is in main,
 * unconditionally, after the call and after an irrelevant branch. Here foo()
 * does return (base case a=false is empty), so main continues. */
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
    }
    /* base case a=false: return */
}

int main(void) {
    foo();                   // C1
    int b = __VERIFIER_nondet_int();
    if (b) {                 // B2 - does not gate the error
        /* ... */
    }
    reach_error();           // T - unconditional
    return 0;
}
