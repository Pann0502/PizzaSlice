/* The error sits behind a constant-false guard: it is unreachable.
 * A splitter that only looks at syntax might emit a witness; it must not.
 * The complete set is empty. */
/* SV-COMP preamble, inlined. */
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *)
    __attribute__((__nothrow__, __leaf__)) __attribute__((__noreturn__));
void reach_error(void) { __assert_fail("0", __FILE__, __LINE__, "reach_error"); }

int main(void) {
    if (0) {             // B1 - constant, never taken
        reach_error();   // T - dead code
    }
    return 0;
}
