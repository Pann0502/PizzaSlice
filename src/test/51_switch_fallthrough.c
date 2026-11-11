/* Fall-through: case 1 has no break and falls into case 2, which holds the
 * error. So BOTH x==1 and x==2 reach the target. Two witnesses. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int x = __VERIFIER_nondet_int();
    switch (x) {             // B1
        case 1:
            /* no break - falls through into case 2 */
        case 2:
            reach_error();   // T - reached by x==1 and x==2
            break;
        default:
            break;
    }
    return 0;
}
