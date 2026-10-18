/* gridwit: witnesses for the grid colourings of gridsearch.c, for a SAT search with lazy clauses.
 *
 * Reads one line of BITS per query on stdin (the colours of the grid points, as for gridsearch check)
 * and prints either "none" (no monochromatic sublattice with s members), or "c x_1 x_2 ..." (a
 * monochromatic sublattice of colour c with at least s members, given by the distinct grid points
 * of its members), or "undecided" (the search budget ran out at some base and nothing was found).
 * The search is the one of gridsearch.c; only the budget is no longer read as success.
 *
 *   gridwit k d_1 .. d_k s [budget]
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

static long budget, budget0 = 20000000;
static int exhausted, nwit;
static DS wit[MAXD];

static int dfs(DS *downs, int n, int last_rank, int last_key) {
    if (n >= s) { memcpy(wit, downs, n * sizeof(DS)); nwit = n; return 1; }
    if (--budget < 0) { exhausted = 1; return 0; }
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
    budget = budget0;
    return dfs(start, 1, 0, -1);
}

/* first (colour, base) pair from which s members are reachable, with its witness in wit */
static int find(int *tb) {
    exhausted = 0;
    for (cls = 0; cls < 2; cls++)
        for (int x = 0; x < npts; x++) {
            int y = x;
            for (int i = k - 1; i >= 0; i--) { tb[i] = y % (dims[i] + 1); y /= dims[i] + 1; }
            if (reachable(tb)) return 1;
        }
    return 0;
}

static void setup(void) {
    npts = 1;
    for (int i = k - 1; i >= 0; i--) { stride[i] = npts; npts *= dims[i] + 1; }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: see the header\n"); return 2; }
    int a = 1;
    k = atoi(argv[a++]);
    for (int i = 0; i < k; i++) dims[i] = atoi(argv[a++]);
    s = atoi(argv[a++]);
    if (a < argc) budget0 = atol(argv[a++]);
    setup();
    static char line[MAXG + 16];
    while (fgets(line, sizeof line, stdin)) {
        if ((int)strcspn(line, "\r\n") != npts) { printf("error need %d bits\n", npts); fflush(stdout); continue; }
        for (int x = 0; x < npts; x++) col[x] = line[x] - '0';
        int t[K];
        if (find(t)) {
            static unsigned char seen[MAXG];
            memset(seen, 0, sizeof seen);
            printf("%d", cls);
            for (int q = 0; q < nwit; q++) {
                int v[K];
                for (int i = 0; i < k; i++) v[i] = t[i] + wit[q].r[i];
                int x = idx(v);
                if (!seen[x]) { seen[x] = 1; printf(" %d", x); }
            }
            printf("\n");
        } else printf(exhausted ? "undecided\n" : "none\n");
        fflush(stdout);
    }
    return 0;
}
