# Release algebra and Accuracy26, checked independently of the Python package.
# 1. Over all 2^8 assignments of the eight verifier factors, Rel = 1 iff every factor is 1,
#    and the label is THEOREM / COUNTEREXAMPLE only then.
# 2. Proposition 21.1: the score at step t carries Collapse(P_{t-1}, P_t) too, so it does not
#    decrease from t to t+1 iff R' + M*' + MapDef' + Collapse' + NMDef' <= R + M* + MapDef +
#    Collapse + NMDef.  The paper's condition leaves out Collapse at step t; it is sufficient but
#    not necessary, so its "if and only if" fails whenever Collapse at step t is positive.
# 3. Corollary 21.4: Accuracy26 can tend to 1 while Rel = 0 (here the formal factor is 0).

using Random
fails = 0
V = ["proof", "formal", "code", "trace", "sim", "risk", "lit", "human"]

function emit(f::Vector{Int}; refutation=false, conditional=false, model_ok=false, machinery=true)
    rel = prod(f)
    if rel == 1
        conditional && return "CONDITIONAL"
        return refutation ? "COUNTEREXAMPLE" : "THEOREM"
    end
    model_ok && return "CANDIDATE"
    return machinery ? "OPEN" : "BUJ"
end

for bits in 0:(2^8 - 1)
    f = [(bits >> i) & 1 for i in 0:7]
    for r in (false, true), m in (false, true)
        lab = emit(f; refutation=r, model_ok=m)
        released = lab in ("THEOREM", "COUNTEREXAMPLE")
        if released != all(==(1), f)
            global fails += 1
        end
    end
end
println("release algebra: 256 assignments checked")

acc(R, Ms, Md, C, N, R0, Ms0, Md0, N0) = 1 - (R + Ms + Md + C + N) // (1 + R0 + Ms0 + Md0 + N0)
rng = MersenneTwister(7)
bad = 0
paper_mismatch = 0
paper_unsound = 0
for trial in 1:20000
    base = rand(rng, 0:5, 4) .// rand(rng, 1:4, 4)
    prev = rand(rng, 0:5, 4) .// rand(rng, 1:4, 4)       # R, M*, MapDef, NMDef at t
    Cprev = rand(rng, 0:3) // 4                           # Collapse(P_{t-1}, P_t)
    new = rand(rng, 0:5, 4) .// rand(rng, 1:4, 4)
    Cnew = rand(rng, 0:3) // 4
    a_t = acc(prev[1], prev[2], prev[3], Cprev, prev[4], base...)
    a_t1 = acc(new[1], new[2], new[3], Cnew, new[4], base...)
    lhs = new[1] + new[2] + new[3] + Cnew + new[4]
    correct = lhs <= prev[1] + prev[2] + prev[3] + Cprev + prev[4]
    paper = lhs <= prev[1] + prev[2] + prev[3] + prev[4]
    if (a_t1 >= a_t) != correct
        global bad += 1
    end
    if (a_t1 >= a_t) != paper
        global paper_mismatch += 1
    end
    if paper && !(a_t1 >= a_t)
        global paper_unsound += 1
    end
end
println("Proposition 21.1: corrected condition $bad mismatches in 20000 random steps; ",
        "paper's condition: $paper_mismatch mismatches, $paper_unsound cases where it holds and the score drops")
if bad != 0 || paper_mismatch == 0 || paper_unsound != 0
    global fails += 1
end

# Corollary 21.4: all defects -> 0 while the formal factor stays 0
f = [1, 0, 1, 1, 1, 1, 1, 1]
scores = [acc(1 // k, 1 // k, 0 // 1, 0 // 1, 1 // k, 3 // 1, 1 // 1, 1 // 1, 1 // 1) for k in (1, 10, 100, 1000)]
println("Corollary 21.4: Accuracy26 = ", Float64.(scores), " while Rel = ", prod(f))
if !(issorted(scores) && scores[end] > 0.999 && prod(f) == 0)
    global fails += 1
end
println(fails == 0 ? "OK" : "FAILED")
exit(fails == 0 ? 0 : 1)
