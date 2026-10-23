"""Exact interval certificates for the shortest reflexive-descent bound.

If Q<P are reflexive, a maximal chain in [Q,P] consists of covers and has
length at most min(|P|-|Q|, |Q*|-|P*|). Concatenating a descent of Q gives
delta(P) <= this cost + L(|Q|,|Q*|). No cut is asserted to be a cover.

The global result uses the supplied KS histogram and its classification counts.
Geometry is recomputed with integer arithmetic; no floating-point hull is used.
"""
from collections import Counter, defaultdict
import csv
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
from . import reflexive as R

DATA = Path(__file__).with_name('data')

def _require(test, message):
    if not test:
        raise ValueError(message)

def _points(values):
    result=[tuple(v) for v in values]
    _require(bool(result) and all(len(v)==4 and all(type(x) is int for x in v)
                                 for v in result), 'expected integer four-vectors')
    _require(len(set(result))==len(result), 'duplicate points')
    return result

def lattice_points(vertices):
    """Exact bounding-box enumeration, solving for the widest coordinate."""
    V=_points(vertices)
    _require(R.dimension(V)==4, 'polytope is not four dimensional')
    fs=R.facets(V)
    lo=[min(v[j] for v in V) for j in range(4)]
    hi=[max(v[j] for v in V) for j in range(4)]
    last=max(range(4),key=lambda j:hi[j]-lo[j])
    other=[j for j in range(4) if j!=last]
    answer=set()
    for values in product(*(range(lo[j],hi[j]+1) for j in other)):
        x=[0]*4
        for j,value in zip(other,values):x[j]=value
        lower,upper=lo[last],hi[last]
        for a,c in fs:
            rhs=c-sum(a[j]*x[j] for j in other)
            if a[last]>0:upper=min(upper,rhs//a[last])
            elif a[last]<0:lower=max(lower,-((-rhs)//a[last]))
            elif rhs<0:upper=lower-1
            if lower>upper:break
        for value in range(lower,upper+1):
            x[last]=value;answer.add(tuple(x))
    return answer

def load_census(path):
    pairs={}
    with open(path,newline='') as f:
        for row in csv.DictReader(f):
            key=(int(row['points']),int(row['dual_points']))
            count=int(row['count'])
            _require(key not in pairs and count>0,'invalid census row')
            pairs[key]=count
    _require(sum(pairs.values())==473800776,'wrong census total')
    return pairs

def pair_bounds(pairs):
    """Independent suffix dynamic program, strict in both point counts."""
    groups=defaultdict(list)
    for p,q in pairs:groups[p].append(q)
    best=[-1]*(max(q for p,q in pairs)+2)
    bounds={}
    for p in sorted(groups):
        pending={q:best[q+1]+1 for q in groups[p]}
        for q,value in pending.items():
            bounds[(p,q)]=value;best[q]=max(best[q],value)
        for q in range(len(best)-2,-1,-1):best[q]=max(best[q],best[q+1])
    return bounds

def verify_interval(record,bounds):
    V=_points(record['source']['vertices'])
    QV=_points(record['child_vertices'])
    _require(R.is_reflexive(V) and R.is_reflexive(QV),'non-reflexive polytope')
    _require(set(V)==set(R.vertices(V)) and set(QV)==set(R.vertices(QV)),
             'a vertex list contains redundant points')
    parent=lattice_points(V);child=lattice_points(QV)
    _require(child<parent,'child is not a strict reflexive subpolytope')
    q=tuple(record['cut'])
    _require(len(q)==4 and all(type(x) is int for x in q),'invalid cut')
    _require(child=={x for x in parent if sum(a*b for a,b in zip(q,x))>=-1},
             'cut does not give the child')
    _require(parent==set(_points(record['parent_points'])),'incomplete parent point list')
    _require(child==set(_points(record['child_points'])),'incomplete child point list')
    dual=lattice_points(R.dual(V));qdual=lattice_points(R.dual(QV))
    _require(dual<qdual,'polarity did not reverse strict inclusion')
    pair=(len(parent),len(dual));qpair=(len(child),len(qdual))
    _require(pair==tuple(record['parent_pair']),'wrong parent pair')
    _require(pair==(record['source']['point_count'],record['source']['dual_point_count']),
             'source count mismatch')
    _require(qpair==tuple(record['child_pair']) and qpair in bounds,'wrong child pair')
    cost=min(pair[0]-qpair[0],qpair[1]-pair[1])
    _require(cost>0 and cost==record['interval_cost'],'wrong interval cost')
    _require(bounds[qpair]==record['child_pair_bound'],'wrong child pair bound')
    bound=cost+bounds[qpair]
    _require(bound==record['depth_upper_bound'],'wrong depth upper bound')
    return dict(parent_pair=pair,child_pair=qpair,interval_cost=cost,upper_bound=bound)

def verify_bundle(bundle=None,census=None):
    if bundle is None:
        bundle=json.loads((DATA/'seed_top346.json').read_text(encoding='utf-8'))
    if census is None:census=DATA/'seed_point_pairs.csv'
    census=Path(census)
    _require(hashlib.sha256(census.read_bytes()).hexdigest()==bundle['census_sha256'],
             'census digest mismatch')
    pairs=load_census(census);bounds=pair_bounds(pairs)
    threshold=bundle['threshold']
    _require(type(threshold) is int and threshold>=0,'invalid threshold')
    expected=Counter({k:n for k,n in pairs.items() if bounds[k]>threshold})
    records=bundle['certificates']
    actual=Counter(tuple(r['parent_pair']) for r in records)
    _require(actual==expected,'certificate coverage does not match the census')
    # Raw coordinate inequality does not prove inequivalence under GL(4,Z).
    # Absolute maximal minors are invariant under a unimodular basis change
    # and a permutation of vertices. Distinct spectra suffice for these data.
    source_keys=[(tuple(r['parent_pair']),tuple(sorted(abs(R._det(c)) for c in
                 combinations(_points(r['source']['vertices']),4)))) for r in records]
    _require(len(set(source_keys))==len(source_keys),
             'minor spectra do not separate source classes')
    verified=[verify_interval(r,bounds) for r in records]
    _require(all(r['upper_bound']<=threshold for r in verified),'threshold not established')
    return dict(shortest_depth_upper_bound=threshold,certificates_verified=len(verified),
                histogram_polytopes=sum(pairs.values()),sharp_constant_known=False,
                scope='relative to the supplied KS census and classification',intervals=verified)

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(json.dumps(verify_bundle(),indent=2))


if __name__=='__main__':main()
