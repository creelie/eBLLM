// Exhaustive checks of the scope-loss and collapse-guard findings.
// 1. Over every pair of partial maps f : A -> B, g : B -> C with |A|, |B|, |C| <= 3:
//    loss(g o f) = loss(f) + #{x : f(x) defined, g(f(x)) lost} always; the superadditivity of
//    Lemma 6.2 fails for some pairs; the union bound loss(g o f) <= loss(f) + loss(g) holds when f
//    is injective where defined.
// 2. Over every playbook of up to 4 bullets (each core or not) and every update that resolves
//    and/or deletes bullets: the v1.1 guard with theta = 0 never accepts the deletion of an
//    unresolved core failure and always accepts pure resolutions; the paper's guard with
//    theta < 1/|Core| rejects every update that resolves a core failure.
#include <cstdio>
#include <vector>

int main() {
  int fails = 0;
  long pairs = 0, superFail = 0;
  for (int na = 0; na <= 3; na++)
    for (int nb = 1; nb <= 3; nb++)
      for (int nc = 1; nc <= 3; nc++) {
        long F = 1, G = 1;
        for (int i = 0; i < na; i++) F *= nb + 1;
        for (int i = 0; i < nb; i++) G *= nc + 1;
        for (long fi = 0; fi < F; fi++)
          for (long gi = 0; gi < G; gi++) {
            std::vector<int> f(na), g(nb);  // value nb (resp. nc) means lost
            long t = fi; for (int i = 0; i < na; i++) { f[i] = t % (nb + 1); t /= nb + 1; }
            t = gi; for (int i = 0; i < nb; i++) { g[i] = t % (nc + 1); t /= nc + 1; }
            int lf = 0, lg = 0, lh = 0, pulled = 0;
            for (int x : f) lf += x == nb;
            for (int y : g) lg += y == nc;
            for (int x : f) { if (x == nb || g[x] == nc) lh++; if (x != nb && g[x] == nc) pulled++; }
            pairs++;
            if (lh != lf + pulled) fails++;
            if (lh < lf + lg) superFail++;
            bool inj = true;
            for (int i = 0; i < na; i++) for (int j = i + 1; j < na; j++) if (f[i] != nb && f[i] == f[j]) inj = false;
            if (inj && lh > lf + lg) fails++;
          }
      }
  std::printf("scope loss: %ld pairs, decomposition and union bound hold; superadditivity fails for %ld\n", pairs, superFail);
  if (superFail == 0) fails++;

  long updates = 0, v11bad = 0, resolveRejectedPaper = 0, resolveUpdates = 0;
  for (int n = 1; n <= 4; n++)
    for (int coreMask = 0; coreMask < (1 << n); coreMask++)
      for (int resolveMask = 0; resolveMask < (1 << n); resolveMask++)
        for (int deleteMask = 0; deleteMask < (1 << n); deleteMask++) {
          int ncore = __builtin_popcount(coreMask);
          if (!ncore) continue;
          updates++;
          // after the update: bullet i is present unless deleted; core unless resolved
          int lostPaper = 0, lostV11 = 0, resolvedCore = 0;
          for (int i = 0; i < n; i++) {
            if (!(coreMask >> i & 1)) continue;
            bool del = deleteMask >> i & 1, res = resolveMask >> i & 1;
            if (del || res) lostPaper++;
            if (del) lostV11++;
            if (res && !del) resolvedCore++;
          }
          // v1.1 guard with theta = 0: accept iff lostV11 * 1 <= 0 * ncore
          bool acceptV11 = lostV11 * 1 <= 0 * ncore;
          bool erasesCore = (deleteMask & coreMask) != 0;
          if (acceptV11 && erasesCore) v11bad++;               // an unresolved failure erased
          if (deleteMask == 0 && !acceptV11) v11bad++;         // a pure resolution rejected
          // paper guard with theta = 1/(ncore+1) < 1/|Core|: accept iff lostPaper/ncore <= theta
          bool acceptPaper = lostPaper * (ncore + 1) <= ncore;
          if (resolvedCore > 0) { resolveUpdates++; if (!acceptPaper) resolveRejectedPaper++; }
        }
  std::printf("collapse guard: %ld updates; v1.1 violations %ld; paper guard rejects %ld of %ld resolving updates\n",
              updates, v11bad, resolveRejectedPaper, resolveUpdates);
  if (v11bad || resolveRejectedPaper != resolveUpdates) fails++;
  std::printf(fails ? "FAILED\n" : "OK\n");
  return fails != 0;
}
