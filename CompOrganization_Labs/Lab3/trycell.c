#include <stdio.h>
extern void *returnsp();

int trycell(int *x, int pos)
{
    int row = pos / 9;
    int col = pos % 9;
    int i, j, used = 0;
    unsigned long sp;
    
    sp = (unsigned long) returnsp();
    printf("Returning from trycell, Stack pointer register  sp: %#8x\n", sp);
    
    sp = (unsigned long) returnsp();
    printf("Returning from trycell, Stack pointer register  sp: %#8x\n", sp);

    if (pos == 81) return 1;
    if (x[pos]) return trycell(x, pos + 1);

    for (i = 0; i < 9; i++)
        used |= 1 << (x[i * 9 + col] - 1);

    for (j = 0; j < 9; j++)
        used |= 1 << (x[row * 9 + j] - 1);

    row = row / 3 * 3;
    col = col / 3 * 3;
    for (i = row; i < row + 3; i++)
        for (j = col; j < col + 3; j++)
            used |= 1 << (x[i * 9 + j] - 1);

    for (x[pos] = 1; x[pos] <= 9; x[pos]++, used >>= 1)
        if (!(used & 1) && trycell(x, pos + 1)) return 1;

    x[pos] = 0;
    sp = (unsigned long) returnsp();
    printf("Returning from trycell, Stack pointer register  sp: %#8x\n", sp);
    return 0;
}
