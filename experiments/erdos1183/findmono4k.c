/* findmono: reads lines "n s hexcolouring" (bit x of the colouring = colour of the point x of 2^[n],
 * n <= 10, written most significant digit first) and prints, for each line, either a monochromatic
 * sublattice with at least s members (its points in decimal, colour first) or "none".
 * Depth-first search over the points of one colour class in increasing order; including a point
 * forces every union and intersection with included points, which must lie in the class. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int P, S, allow[4096], inc[4096], exc[4096], must[4096], found, cls;
static int pts[4096], npts;

static int add(int p, int *forced, int *nf) {
    *nf = 0;
    for (int i = 0; i < npts; i++) {
        int q = pts[i];
        int t[2] = {p | q, p & q};
        for (int k = 0; k < 2; k++) {
            int x = t[k];
            if (x == p || inc[x]) continue;
            if (!allow[x] || exc[x] || x < p) return 0;
            int seen = 0;
            for (int j = 0; j < *nf; j++) if (forced[j] == x) seen = 1;
            if (!seen) forced[(*nf)++] = x;
        }
    }
    return 1;
}

static void dfs(int p, int remaining) {
    if (found) return;
    if (npts + remaining < S) return;
    if (npts >= S) {   /* the family is a sublattice once every forced point is included */
        int ok = 1;
        for (int x = 0; x < P && ok; x++) if (must[x] && !inc[x]) ok = 0;
        if (ok) {
            found = 1;
            printf("%d", cls);
            for (int i = 0; i < npts; i++) printf(" %d", pts[i]);
            printf("\n");
            return;
        }
    }
    if (p == P) return;
    int ra = remaining - (allow[p] ? 1 : 0);
    if (allow[p]) {
        int forced[4096], nf;
        if (add(p, forced, &nf)) {
            int saved[4096]; memcpy(saved, must, sizeof must);
            for (int i = 0; i < nf; i++) must[forced[i]] = 1;
            inc[p] = 1; pts[npts++] = p;
            dfs(p + 1, ra);
            npts--; inc[p] = 0;
            memcpy(must, saved, sizeof must);
        }
    }
    if (!must[p] && !found) {
        exc[p] = 1;
        dfs(p + 1, ra);
        exc[p] = 0;
    }
}

int main(void) {
    int n; char hex[1100];
    while (scanf("%d %d %1099s", &n, &S, hex) == 3) {
        P = 1 << n;
        int col[4096] = {0}, L = strlen(hex);
        for (int i = 0; i < L; i++) {
            char c = hex[L - 1 - i];
            int v = (c <= '9') ? c - '0' : (c | 32) - 'a' + 10;
            for (int b = 0; b < 4; b++) if (4 * i + b < P) col[4 * i + b] = (v >> b) & 1;
        }
        found = 0;
        for (cls = 1; cls >= 0 && !found; cls--) {
            int na = 0;
            for (int x = 0; x < P; x++) { allow[x] = (col[x] == cls); na += allow[x]; }
            memset(inc, 0, sizeof inc); memset(exc, 0, sizeof exc); memset(must, 0, sizeof must);
            npts = 0;
            dfs(0, na);
        }
        if (!found) printf("none\n");
        fflush(stdout);
    }
    return 0;
}
