/* Independent check of the sand-tile findings, in exact integer arithmetic.
   1. Conservative two-site run (units 1/2: heights 2,2, theta 1, Delta 2, share 2): no
      stable configuration within 10^6 topplings (Proposition 10.2, Theorem 10.4).
   2. Dissipative two-site run (units 1/N: heights 2N,2N, theta N, Delta 2N, share 2N-2):
      exactly N topplings, against the bound 4 of Theorem 10.4, for N = 10, 100, 1000, 10000.
   3. Abelian property of chip-firing with a sink on 200 random graphs: the stable
      configuration and the number of topplings do not depend on the order. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long run2(long a, long b, long theta, long delta, long share, long maxt) {
  for (long t = 0; t <= maxt; t++) {
    if (a > theta) { a -= delta; b += share; }
    else if (b > theta) { b -= delta; a += share; }
    else return t;
  }
  return -1;
}

static unsigned long long rng_state = 88172645463325252ULL;
static unsigned rnd(unsigned n) {
  rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
  return (unsigned)(rng_state % n);
}

#define MAXV 12
static int adj[MAXV][MAXV], deg[MAXV];

static long fire(int n, const long *h0, long *hout, int mode) {
  long h[MAXV]; memcpy(h, h0, sizeof(long) * n);
  long count = 0;
  for (;;) {
    int cand[MAXV], nc = 0;
    for (int v = 1; v < n; v++) if (h[v] >= deg[v]) cand[nc++] = v;
    if (!nc) break;
    int v = mode == 0 ? cand[0] : mode == 1 ? cand[nc - 1] : cand[rnd(nc)];
    h[v] -= deg[v];
    for (int u = 0; u < n; u++) if (adj[v][u]) h[u] += 1;
    h[0] = 0; /* the sink */
    count++;
  }
  memcpy(hout, h, sizeof(long) * n);
  return count;
}

int main(void) {
  int fails = 0;
  long r = run2(2, 2, 1, 2, 2, 1000000);
  printf("conservative run: %s within 10^6 topplings (bound 4)\n", r < 0 ? "not stable" : "stable");
  if (r >= 0) fails++;
  long Ns[] = {10, 100, 1000, 10000};
  for (int i = 0; i < 4; i++) {
    long N = Ns[i];
    long t = run2(2 * N, 2 * N, N, 2 * N, 2 * N - 2, 100 * N);
    printf("dissipative run, absorbed share 1/%ld: %ld topplings (bound 4)\n", N, t);
    if (t != N) fails++;
  }
  int bad = 0;
  for (int trial = 0; trial < 200; trial++) {
    int n = 4 + rnd(8);
    memset(adj, 0, sizeof adj); memset(deg, 0, sizeof deg);
    for (int v = 1; v < n; v++) { int u = rnd(v); adj[u][v] = adj[v][u] = 1; }
    for (int e = 0; e < n; e++) { int a = rnd(n), b = rnd(n); if (a != b) adj[a][b] = adj[b][a] = 1; }
    for (int v = 0; v < n; v++) for (int u = 0; u < n; u++) deg[v] += adj[v][u];
    long h0[MAXV] = {0}, ha[MAXV], hb[MAXV], hc[MAXV];
    for (int v = 1; v < n; v++) h0[v] = rnd(3 * deg[v] + 1);
    long ca = fire(n, h0, ha, 0), cb = fire(n, h0, hb, 1), cc = fire(n, h0, hc, 2);
    if (ca != cb || ca != cc || memcmp(ha, hb, sizeof(long) * n) || memcmp(ha, hc, sizeof(long) * n)) bad++;
  }
  printf("abelian property: %d of 200 random graphs disagree\n", bad);
  if (bad) fails++;
  printf(fails ? "FAILED\n" : "OK\n");
  return fails != 0;
}
