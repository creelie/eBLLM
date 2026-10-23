"""Exact checks for nilpotent-free subspaces of M_3(F_3).

The upper bound is a finite exhaustive C computation. The default mode checks
only the five-dimensional lower bound. --full also recompiles and runs the
entire search; a stored table or a successful lower-bound check cannot stand
in for that run. The archived Lean proof uses two native_decide evaluations.
"""
from itertools import product
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

DATA=Path(__file__).with_name('data')

def _require(test,message):
    if not test:
        raise ValueError(message)

def multiply(x,y):
    _require(len(x)==len(y)==9,'expected two 3 by 3 matrices')
    return tuple(sum(x[3*i+k]*y[3*k+j] for k in range(3))%3
                 for i in range(3) for j in range(3))

def nilpotent(x):
    """For a 3 by 3 matrix, nilpotent is equivalent to X^3=0."""
    return not any(multiply(multiply(x,x),x))

def five_matrix(a,b,c,d,e):
    return (a%3,0,b%3,0,(c-d-e)%3,c%3,b%3,d%3,e%3)

def verify_lower_bound():
    images=set()
    for values in product(range(3),repeat=5):
        x=five_matrix(*values)
        images.add(x)
        _require(not any(values) or not nilpotent(x),
                 'five-dimensional construction contains a nonzero nilpotent')
    _require(len(images)==3**5,'parameter map is not injective')
    # The displayed matrix formula is linear in all five parameters.
    return dict(field_order=3,matrix_size=3,construction_dimension=5,
                construction_elements_checked=len(images),lower_bound_verified=True,
                upper_bound_verified=False)

def load_certificate():
    return json.loads((DATA/'nilpotent_free_f3.json').read_text(encoding='utf-8'))

def verify_source(source,certificate):
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    _require(digest==certificate['source_sha256'],'verifier source digest mismatch')

def check_tree_output(output,certificate,returncode=0):
    _require(returncode==0,'exhaustive verifier exited unsuccessfully')
    actual=[tuple(map(int,m)) for m in re.findall(
        r'^depth (\d+): nodes (\d+) closed (\d+)\s*$',output,re.M)]
    expected=[(d,n,c) for d,(n,c) in enumerate(zip(
        certificate['nodes_by_depth'],certificate['closed_by_depth']))]
    _require(actual==expected,'exhaustive tree table is missing or inconsistent')
    for d in range(6):
        _require(actual[d+1][1]==27*(actual[d][1]-actual[d][2]),
                 'tree coverage recurrence failed')
    total=sum(n for _,n,_ in actual)
    _require(total==3109888,'wrong total node count')
    _require(re.search(r'^total nodes 3109888; open leaves 0\s*$',output,re.M)
             is not None,'open leaves were not excluded')
    _require('exact exhaustive upper-bound audit: PASS' in output,
             'exhaustive verifier did not report success')
    return dict(upper_bound_verified=True,search_nodes=total,open_leaves=0)

def _compiler(compiler=None):
    if compiler:
        return str(compiler)
    if os.name=='nt':
        # Lean distributions bundle a Windows linker and import libraries.
        candidates=sorted((Path.home()/'.elan'/'toolchains').glob('*/bin/clang.exe'),
                          reverse=True)
        for c in candidates:
            if (c.parent.parent/'lib'/'libmsvcrt.a').exists():
                return str(c)
    for name in ('cc','gcc','clang'):
        found=shutil.which(name)
        if found:
            return found
    raise RuntimeError('a C compiler is required for the exhaustive upper bound')

def verify_full(compiler=None):
    result=verify_lower_bound()
    certificate=load_certificate()
    source=DATA/'nilpotent_free_f3.c'
    verify_source(source,certificate)
    cc=_compiler(compiler)
    with tempfile.TemporaryDirectory(prefix='anaxia-nilpotent-') as temp:
        executable=Path(temp)/('verify.exe' if os.name=='nt' else 'verify')
        if os.name=='nt':
            lib=Path(cc).resolve().parent.parent/'lib'
            _require((lib/'libmsvcrt.a').exists(),
                     'Windows full check requires the bundled Lean clang toolchain')
            args=[cc,'--target=x86_64-w64-windows-gnu','-O3','-fno-stack-protector',
                  '-nostdlib','-Wl,--entry,mainCRTStartup',str(source),
                  '-L'+str(lib),'-lmsvcrt','-lkernel32','-o',str(executable)]
        else:
            args=[cc,'-O3','-std=c11','-DPORTABLE',str(source),'-o',str(executable)]
        built=subprocess.run(args,capture_output=True,text=True,timeout=120)
        _require(built.returncode==0,'C compilation failed: '+built.stderr[-1000:])
        run=subprocess.run([str(executable)],capture_output=True,text=True,timeout=120)
        result.update(check_tree_output(run.stdout,certificate,run.returncode))
    result.update(maximum_nilpotent_free_dimension=5,
                  conjecture_refuted='Wigderson Conjecture 8, F=F_3 and n=3',
                  proof_kind='exhaustive computer-assisted proof',
                  computational_trust='C compiler and execution; archived Lean uses native_decide',
                  referee_status='not certified as refereed',
                  preprint=certificate['preprint'])
    return result

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full',action='store_true',help='compile and run the exhaustive upper bound')
    parser.add_argument('--compiler',help='C compiler path (Lean bundled clang on Windows)')
    args=parser.parse_args(argv)
    result=verify_full(args.compiler) if args.full else verify_lower_bound()
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
