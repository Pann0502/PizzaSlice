extern void reach_error(void);
extern int __VERIFIER_nondet_int(void);
int main() {

  int x = __VERIFIER_nondet_int();
  int y;

  if (x > 10) {
    y = x - 10;
  } else {
    y = 10 - x;
  }

  if (y == 0) {
    reach_error();
  }

  return 0;
}