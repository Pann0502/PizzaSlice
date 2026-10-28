extern void reach_error(void);

int main() {
    int x = 0;

    if (x == 0) {
        reach_error();
    }

    return 0;
}