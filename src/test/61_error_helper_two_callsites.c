/* The single error sits in a helper called from two guarded sites, each with
 * its own guard. Two witnesses, distinguished by call site and guard. */
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
    if (a) {                 // B1
        err();               // C1
    }
    if (b) {                 // B2
        err();               // C2
    }
    return 0;
}
