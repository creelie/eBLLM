// Renyi law and gating bounds: closed forms against random feasible points.
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

int main() {
  std::mt19937_64 g(20261018);
  std::uniform_real_distribution<double> U(0.0, 1.0);
  int checks = 0, fails = 0;
  // Renyi: min sum a d^-s subject to sum d <= theta equals theta^-s (sum a^(1/(1+s)))^(1+s)
  for (int t = 0; t < 2000; t++) {
    int n = 1 + g() % 12; double s = 0.1 + 3 * U(g), theta = 0.001 + 0.999 * U(g);
    std::vector<double> a(n); double S = 0;
    for (auto &x : a) { x = 0.01 + U(g); S += std::pow(x, 1 / (1 + s)); }
    double V = std::pow(theta, -s) * std::pow(S, 1 + s);
    double Vstar = 0;
    for (auto x : a) Vstar += x * std::pow(theta * std::pow(x, 1 / (1 + s)) / S, -s);
    checks++; if (std::fabs(Vstar - V) > 1e-9 * V) { fails++; std::printf("FAIL attain\n"); }
    std::vector<double> d(n); double D = 0;
    for (auto &x : d) { x = 1e-3 + U(g); D += x; }
    double W = 0;
    for (int i = 0; i < n; i++) { d[i] *= theta / D; W += a[i] * std::pow(d[i], -s); }
    checks++; if (W < V * (1 - 1e-12)) { fails++; std::printf("FAIL lower\n"); }
  }
  // gating precision bounds and separation ratio
  for (int t = 0; t < 2000; t++) {
    int n = 1 + g() % 60; double eta = 0.5 * U(g), delta = 0.5 * U(g), P = 1, X = 0, Y = 0;
    for (int i = 0; i < n; i++) {
      double rho = 0.9 * U(g), si = (1 - rho) * (1 - eta) + rho * delta;
      double x = rho * delta / ((1 - rho) * (1 - eta));
      P *= (1 - rho) * (1 - eta) / si; X += x; Y += x / (1 + x);
    }
    checks++; if (!(std::exp(-X) <= P * (1 + 1e-12) && P <= std::exp(-Y) * (1 + 1e-12))) {
      fails++; std::printf("FAIL precision\n"); }
    double rho = 0.95 * U(g);
    double ratio = (n / std::pow(1 - rho, n)) / (n / (1 - rho));
    checks++; if (std::fabs(ratio - std::pow(1 - rho, -(n - 1))) > 1e-9 * ratio ||
                  ratio < 1 + (n - 1) * rho - 1e-9) { fails++; std::printf("FAIL separation\n"); }
  }
  std::printf("renyi_gating (C++): %d checks, %d failed\n", checks, fails);
  return fails != 0;
}
