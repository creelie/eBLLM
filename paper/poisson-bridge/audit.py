"""Re-elaborate the auxiliary core-only Lean file and reject nonstandard axioms."""
from pathlib import Path
import argparse,re,subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lean',default='lean')
args=parser.parse_args()
here=Path(__file__).resolve().parent
root=here.parents[1]
source=(here/'PowerCounting.lean').read_text(encoding='utf-8')
names=re.findall(r'^theorem\s+([^\s(:]+)',source,re.M)
assert len(names)==17
build=root/'build'
build.mkdir(exist_ok=True)
target=build/'poisson-axioms.lean'
target.write_text(source+'\n'+'\n'.join('#print axioms '+n for n in names)+'\n',encoding='utf-8')
run=subprocess.run([args.lean,str(target)],capture_output=True,text=True,encoding='utf-8',timeout=180)
output=run.stdout+run.stderr
(build/'poisson-axioms.log').write_text(output,encoding='utf-8')
if run.returncode:
    raise SystemExit(output)
rows=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",output,re.M)
assert {name for name,_ in rows}==set(names)
assert all({a.strip() for a in axioms.split(',') if a.strip()} <= {'propext','Quot.sound'} for _,axioms in rows)
print('17 auxiliary Lean theorems passed; standard core axioms only')
