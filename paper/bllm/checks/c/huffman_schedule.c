/* Integer soundness: the optimal schedule cost equals A (k + Huffman expected length).
   Exhaustive search over schedules on random small instances, D-ary Huffman by merging. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static unsigned long long state = 20261018ULL;
static double uni(void) {
  state = state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(state >> 11) / 9007199254740992.0;
}

/* D-ary Huffman expected length (in code symbols) for weights w[0..n-1]. */
static double huffman(const double *w, int n, int D) {
  double node[64]; int m = 0; double cost = 0.0;
  for (int i = 0; i < n; i++) node[m++] = w[i];
  while ((m - 1) % (D - 1) != 0) node[m++] = 0.0;
  while (m > 1) {
    double tot = 0.0;
    for (int t = 0; t < D; t++) {
      int best = 0;
      for (int j = 1; j < m; j++) if (node[j] < node[best]) best = j;
      tot += node[best]; node[best] = node[--m];
    }
    node[m++] = tot; cost += tot;
  }
  return cost;
}

static double best_cost; static int n_g, D_g, k_g, rmax_g; static double a_g[8];
static void search(int i, double kraft, double cost) {
  if (kraft > pow((double)D_g, -k_g) * (1 + 1e-12)) return;
  if (i == n_g) { if (cost < best_cost) best_cost = cost; return; }
  for (int r = 0; r <= rmax_g; r++)
    search(i + 1, kraft + pow((double)D_g, -r), cost + a_g[i] * r);
}

int main(void) {
  int checks = 0, fails = 0;
  for (int trial = 0; trial < 400; trial++) {
    n_g = 2 + (int)(uni() * 5); D_g = 2 + (int)(uni() * 3); k_g = (int)(uni() * 3);
    rmax_g = k_g + 7;
    double A = 0.0, w[8];
    for (int i = 0; i < n_g; i++) { a_g[i] = 0.05 + uni(); A += a_g[i]; }
    for (int i = 0; i < n_g; i++) w[i] = a_g[i] / A;
    best_cost = 1e300; search(0, 0.0, 0.0);
    double predicted = A * (k_g + huffman(w, n_g, D_g));
    checks++;
    if (fabs(best_cost - predicted) > 1e-9 * predicted) {
      fails++; printf("FAIL trial %d: search %.12f huffman %.12f\n", trial, best_cost, predicted);
    }
    double H = 0.0; for (int i = 0; i < n_g; i++) H -= w[i] * log(w[i]);
    double L = log((double)D_g), lo = A / L * (H + k_g * L);
    checks++;
    if (!(lo - 1e-9 <= best_cost && best_cost <= lo + A + 1e-9)) {
      fails++; printf("FAIL bounds trial %d\n", trial);
    }
  }
  printf("huffman_schedule (C): %d checks, %d failed\n", checks, fails);
  return fails != 0;
}
