#include <stdio.h>

extern int trycell(int*, int);

void show(int *x)
{
    int i, j;
    for (i = 0; i < 9; i++) {
        if (!(i % 3)) putchar('\n');
        for (j = 0; j < 9; j++)
            printf(j % 3 ? "%2d" : "%3d", *x++);
        putchar('\n');
    }
}

void solve(const char *s)
{
    int i, x[81];
    for (i = 0; i < 81; i++)
        x[i] = s[i] >= '1' && s[i] <= '9' ? s[i] - '0' : 0;

    puts("Puzzle to solve\n");
    show(x);
    if (trycell(x, 0)) {
        puts("\nSolution:\n");
        show(x);
    }
    else
        puts("No solution\n");
}

int main(void)
{
    solve(    "5...7...."
        "6..195..."
        ".98....6."
        "8...6...3"
        "4..8.3..1"
        "7...2...6"
        ".6....28."
        "...419..5"
        "....8..79"    );

    return 0;
}
