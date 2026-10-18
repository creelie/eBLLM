/* Largest sublattice (family closed under union and intersection) of 2^[n] inside a given set of
 * points, by depth-first search over the points in increasing order with forced exclusions.
 * Usage: maxsub n            prints the number of nonempty sublattices of 2^[n] (n <= 5)
 *        maxsub n dump s       prints, in hex, every sublattice with at least s members
 *        maxsub n brute      prints f(n) = min over 2-colourings of the largest monochromatic
 *                            sublattice, by exhausting all 2^(2^n) colourings (n <= 4). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int N, P;              /* P = 2^n points */
static int inc[64], exc[64];  /* inclusion flags during the search */
static int allow[64];
static long long count;
static int best;
static int dump_min = -1;

/* adding point p to the current family: every union and intersection with an included point must
 * be allowed and not already excluded; points are decided in increasing order, so a union or
 * intersection that is below p and undecided cannot occur. */
static int ok_add(int p, int *forced, int *nf) {
    *nf = 0;
    for (int q = 0; q < P; q++) if (inc[q]) {
        int u = p | q, v = p & q;
        int t[2] = {u, v};
        for (int k = 0; k < 2; k++) {
            int x = t[k];
            if (x == p || inc[x]) continue;
            if (!allow[x] || exc[x] || x < p) return 0;
            /* x > p: must be included later */
            int seen = 0;
            for (int i = 0; i < *nf; i++) if (forced[i] == x) seen = 1;
            if (!seen) forced[(*nf)++] = x;
        }
    }
    return 1;
}

static int must[64];   /* points that must still be included */

static void dfs(int p, int size, int remaining_allowed, int mode) {
    if (mode == 1 && size + remaining_allowed <= best) return;
    if (p == P) {
        for (int x = 0; x < P; x++) if (must[x] && !inc[x]) return;
        if (size == 0) return;
        if (mode == 0) {
            count++;
            if (dump_min >= 0 && size >= dump_min) {
                unsigned long long m = 0;
                for (int x = 0; x < P; x++) if (inc[x]) m |= 1ULL << x;
                printf("%llx\n", m);
            }
        }
        else if (size > best) best = size;
        return;
    }
    int ra = remaining_allowed - (allow[p] ? 1 : 0);
    /* include p */
    if (allow[p]) {
        int forced[64], nf;
        if (ok_add(p, forced, &nf)) {
            int saved[64]; memcpy(saved, must, sizeof must);
            for (int i = 0; i < nf; i++) must[forced[i]] = 1;
            inc[p] = 1;
            dfs(p + 1, size + 1, ra, mode);
            inc[p] = 0;
            memcpy(must, saved, sizeof must);
        }
    }
    /* exclude p */
    if (!must[p]) {
        exc[p] = 1;
        dfs(p + 1, size, ra, mode);
        exc[p] = 0;
    }
}

int largest_in(uint64_t mask) {
    int na = 0;
    for (int x = 0; x < P; x++) { allow[x] = (mask >> x) & 1; na += allow[x]; }
    memset(inc, 0, sizeof inc); memset(exc, 0, sizeof exc); memset(must, 0, sizeof must);
    best = 0;
    dfs(0, 0, na, 1);
    return best;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]); P = 1 << N;
    if (argc == 4 && !strcmp(argv[2], "dump")) {
        dump_min = atoi(argv[3]);
        for (int x = 0; x < P; x++) allow[x] = 1;
        dfs(0, 0, P, 0);
        return 0;
    }
    if (argc == 2) {
        for (int x = 0; x < P; x++) allow[x] = 1;
        count = 0; dfs(0, 0, P, 0);
        printf("n=%d nonempty_sublattices=%lld\n", N, count);
        return 0;
    }
    uint64_t full = (P == 64) ? ~0ULL : ((1ULL << P) - 1);
    int f = 1 << 30; uint64_t arg = 0;
    /* colour of point 0 fixed to red by symmetry */
    for (uint64_t r = 0; r < (1ULL << (P - 1)); r++) {
        uint64_t red = (r << 1) | 1ULL;
        int a = largest_in(red);
        if (a >= f) continue;
        int b = largest_in(full & ~red);
        int m = a > b ? a : b;
        if (m < f) { f = m; arg = red; }
    }
    printf("n=%d f=%d witness_red_mask=0x%llx\n", N, f, (unsigned long long)arg);
    return 0;
}
