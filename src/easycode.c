extern void reach_error(void);
extern int __VERIFIER_nondet_int(void);

int main() {

  int x = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  int y;

  if (x > 10) {
    y = x - 10;
    if (x < 15) {
      y = x + 3;
      if (z > 0) {
        y = x + 3 - z;
      } else {
        y = x + 3 + z;
      }
    }
  } else if (x < 0) {
    y = 0 - x;
  } else {
    y = 10 - x;
  }

  if (y == 0) {
    reach_error();
  }

  return 0;
}