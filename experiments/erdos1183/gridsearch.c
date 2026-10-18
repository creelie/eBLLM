/* gridsearch: grid colourings of 2^[n] with no monochromatic sublattice of s members.
 *
 * A grid colouring fixes a partition [n] = X_1 u ... u X_k with |X_i| = d_i and colours S by the
 * vector v(S) = (|S n X_1|, ..., |S n X_k|).  By the weighted-poset lemma of gridmono.py, a
 * monochromatic sublattice of colour c with N members exists iff there are a poset P, weights
 * w: P -> N^k \ {0} and a base t with every t + w(I) (I a down-set) of colour c, and |J(P)| = N.
 * This is the search of gridmono.py in C (same order of elements, same pruning), so the two agree.
 *
 *   gridsearch check k d_1 .. d_k s BITS        BITS: colours of the grid points in lexicographic
 *                                               order of v; prints the number of (colour, base)
 *                                               pairs from which s members are reachable (0 = none)
 *   gridsearch anneal k d_1 .. d_k s LEVELWORD seed steps
 *                                               starts from the level colouring S -> LEVELWORD[|S|]
 *                                               and flips grid points, minimising that number;
 *                                               prints BITS of every colouring reaching 0.
 *                                               LEVELWORD may also be the full grid BITS.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define K 4
#define MAXG 4096
#define MAXD 64

static int k, dims[K], s, npts, stride[K];
static unsigned char col[MAXG];
static int W[MAXG][K], wsum[MAXG], nw;
static int room[K], base[K], cls;

typedef struct { uint64_t m; int r[K]; } DS;

static int idx(const int *v) { int x = 0; for (int i = 0; i < k; i++) x += v[i] * stride[i]; return x; }

static int ok_point(const int *r) {
    int v[K];
    for (int i = 0; i < k; i++) { v[i] = base[i] + r[i]; if (r[i] > room[i]) return 0; }
    return col[idx(v)] == cls;
}

static long budget;

static int dfs(DS *downs, int n, int last_rank, int last_key) {
    if (n >= s) return 1;
    if (--budget < 0) return 1;           /* treat an exhausted budget as reachable (pessimistic) */
    uint64_t all = 0;
    for (int i = 0; i < n; i++) all |= downs[i].m;
    uint64_t j = all ? (1ULL << (64 - __builtin_clzll(all))) : 1ULL;
    DS next[MAXD];
    for (int di = 0; di < n; di++) {
        uint64_t D = downs[di].m;
        int rD = 0;
        for (int i = 0; i < k; i++) rD += downs[di].r[i];
        int sup[MAXD], ns = 0;
        for (int i = 0; i < n; i++) if ((downs[i].m & D) == D) sup[ns++] = i;
        for (int a = 0; a < nw; a++) {
            int rp = rD + wsum[a];
            if (rp < last_rank || (rp == last_rank && di < last_key)) continue;
            int good = 1;
            for (int q = 0; q < ns && good; q++) {
                int r[K];
                for (int i = 0; i < k; i++) r[i] = downs[sup[q]].r[i] + W[a][i];
                good = ok_point(r);
            }
            if (!good) continue;
            if (n + ns > MAXD) continue;
            memcpy(next, downs, n * sizeof(DS));
            for (int q = 0; q < ns; q++) {
                next[n + q].m = downs[sup[q]].m | j;
                for (int i = 0; i < k; i++) next[n + q].r[i] = downs[sup[q]].r[i] + W[a][i];
            }
            if (dfs(next, n + ns, rp, di)) return 1;
        }
    }
    return 0;
}

static int reachable(const int *t) {
    if (col[idx(t)] != cls) return 0;
    nw = 0;
    for (int i = 0; i < k; i++) { room[i] = dims[i] - t[i]; base[i] = t[i]; }
    /* all nonzero w in prod [0, room_i], sorted by sum (stable on lexicographic order, as in Python) */
    int tot = 1;
    for (int i = 0; i < k; i++) tot *= room[i] + 1;
    for (int sum = 1; sum <= 64; sum++)
        for (int x = 0; x < tot; x++) {
            int v[K], y = x, sm = 0;
            for (int i = k - 1; i >= 0; i--) { v[i] = y % (room[i] + 1); y /= room[i] + 1; sm += v[i]; }
            if (sm == sum) { memcpy(W[nw], v, sizeof v); wsum[nw++] = sm; }
        }
    DS start[1];
    start[0].m = 0;
    memset(start[0].r, 0, sizeof start[0].r);
    budget = 2000000;
    return dfs(start, 1, 0, -1);
}

/* number of (colour, base) pairs from which s members are reachable; stops at cap */
static int score(int cap) {
    int c = 0;
    for (cls = 0; cls < 2; cls++)
        for (int x = 0; x < npts; x++) {
            int t[K], y = x;
            for (int i = k - 1; i >= 0; i--) { t[i] = y % (dims[i] + 1); y /= dims[i] + 1; }
            if (reachable(t) && ++c >= cap) return c;
        }
    return c;
}

static void setup(void) {
    npts = 1;
    for (int i = k - 1; i >= 0; i--) { stride[i] = npts; npts *= dims[i] + 1; }
}

static void print_bits(void) { for (int x = 0; x < npts; x++) putchar('0' + col[x]); putchar('\n'); }

static uint64_t rng = 88172645463325252ULL;
static uint64_t rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: see the header\n"); return 2; }
    int a = 2;
    k = atoi(argv[a++]);
    for (int i = 0; i < k; i++) dims[i] = atoi(argv[a++]);
    s = atoi(argv[a++]);
    setup();
    if (!strcmp(argv[1], "check")) {
        const char *b = argv[a];
        if ((int)strlen(b) != npts) { fprintf(stderr, "need %d bits\n", npts); return 2; }
        for (int x = 0; x < npts; x++) col[x] = b[x] - '0';
        printf("%d\n", score(1 << 30));
        return 0;
    }
    const char *lw = argv[a++];
    rng ^= (uint64_t)atoll(argv[a++]) * 0x9E3779B97F4A7C15ULL;
    long steps = atol(argv[a++]);
    for (int x = 0; x < npts; x++) {
        int y = x, sm = 0;
        for (int i = k - 1; i >= 0; i--) { sm += y % (dims[i] + 1); y /= dims[i] + 1; }
        col[x] = ((int)strlen(lw) == npts ? lw[x] : lw[sm]) - '0';   /* LEVELWORD may be full grid BITS */
    }
    int cur = score(1 << 30), best = cur;
    printf("start %d\n", cur);
    fflush(stdout);
    for (long st = 0; st < steps && cur > 0; st++) {
        int x = rnd() % npts, y = rnd() % npts;
        int two = rnd() % 3 == 0;
        col[x] ^= 1;
        if (two) col[y] ^= 1;
        int sc = score(cur + 2);
        double T = 0.6 * (1.0 - (double)st / steps) + 0.05;
        if (sc <= cur || (double)(rnd() % 100000) / 100000.0 < __builtin_exp((cur - sc) / T)) {
            cur = sc;
            if (cur < best) { best = cur; printf("step %ld score %d bits ", st, cur); print_bits(); fflush(stdout); }
        } else {
            col[x] ^= 1;
            if (two) col[y] ^= 1;
        }
    }
    printf("best %d\n", best);
    if (cur == 0) { printf("FOUND "); print_bits(); }
    return 0;
}
