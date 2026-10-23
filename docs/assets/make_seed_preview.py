"""README preview: exact four-dimensional vertex edges and retained lattice points."""
from pathlib import Path
from itertools import combinations
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from ebllm.construct import reflexive as R

b=json.loads((ROOT/'src/ebllm/construct/data/seed_top346.json').read_text())
r=b['certificates'][1]
V=r['source']['vertices'];fs=R.facets(V)
edges=[(i,j) for i,j in combinations(range(len(V)),2) if R._rank([a for a,c in fs if R._dot(a,V[i])==c==R._dot(a,V[j])])==3]
kept={tuple(p) for p in r['child_points']}

def build(dark):
 bg,panel,ink,sub,line=('#080e1c','#111b30','#edf4ff','#adbbce','#29384f') if dark else ('#f0f5fd','#ffffff','#102038','#526580','#d4deee')
 mint,red,blue=('#62e9c8','#ff8c9d','#9eb4ff') if dark else ('#00866b','#cf4960','#506de0')
 out=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-label="Anaxia certificate explorer: twelve exact intervals, shortest bound 346 relative to the census, sharp constant open">
<defs><radialGradient id="halo"><stop stop-color="{blue}" stop-opacity=".2"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/></radialGradient><linearGradient id="bar"><stop stop-color="{blue}"/><stop offset="1" stop-color="{mint}"/></linearGradient></defs>
<style>text{{font-family:system-ui,Arial,sans-serif}}.fine{{font-family:ui-monospace,monospace}}.flow{{stroke-dasharray:7 11;animation:flow 4s linear infinite}}.breathe{{animation:breathe 4s ease-in-out infinite}}.grow{{transform-origin:720px 0;animation:grow 1.8s ease-out both}}@keyframes flow{{to{{stroke-dashoffset:-72}}}}@keyframes breathe{{50%{{opacity:.35}}}}@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<rect width="1200" height="620" rx="24" fill="{bg}"/><ellipse cx="400" cy="290" rx="430" ry="290" fill="url(#halo)"/>
<text x="42" y="43" fill="{mint}" font-size="12" letter-spacing="3">ANAXIA / THE BLLM ENGINE</text>
<text x="42" y="103" fill="{ink}" font-size="43" font-weight="700">See every cut. Check every bound.</text>
<text x="44" y="139" fill="{sub}" font-size="17">Twelve exact constructions. One finite-interval proof. All source data included.</text>
<rect x="35" y="170" width="615" height="345" rx="18" fill="{panel}" stroke="{line}"/>
<rect x="670" y="170" width="495" height="345" rx="18" fill="{panel}" stroke="{line}"/>
<text x="59" y="204" fill="{ink}" font-size="17" font-weight="600">P: 680 points → Q: 422 points</text>
<text x="59" y="227" fill="{sub}" font-size="12">Exact points and edges; fixed orthogonal projection from 4D</text>''']
 def xy(p):
  return (p[0]*math.cos(.6)+p[3]*math.sin(.6),p[1]*math.cos(1.05)+p[2]*math.sin(1.05))
 P=[xy(p) for p in r['parent_points']]
 minx,maxx=min(p[0] for p in P),max(p[0] for p in P)
 miny,maxy=min(p[1] for p in P),max(p[1] for p in P)
 scale=min(540/(maxx-minx),215/(maxy-miny))
 def pos(p):
  x,y=xy(p);return 342+(x-(minx+maxx)/2)*scale,365-(y-(miny+maxy)/2)*scale
 for i,j in edges:
  x,y=pos(V[i]);u,v=pos(V[j]);out.append(f'<path d="M{x:.2f},{y:.2f} L{u:.2f},{v:.2f}" stroke="{blue}" opacity=".35" fill="none"/>')
 for p in r['parent_points']:
  x,y=pos(p);color=mint if tuple(p) in kept else red
  out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.8" fill="{color}" opacity=".72"/>')
 for i,j in edges[:4]:
  x,y=pos(V[i]);u,v=pos(V[j]);out.append(f'<path class="flow" d="M{x:.2f},{y:.2f} L{u:.2f},{v:.2f}" stroke="{mint}" opacity=".8" fill="none"/>')
 out += [f'<text x="59" y="492" fill="{mint}" class="fine" font-size="13">q = (−1, 0, 4, −3) · retain q·x ≥ −1</text>',f'<text x="696" y="203" fill="{ink}" font-size="17" font-weight="600">The retained certificates</text>']
 for i,rec in enumerate(b['certificates']):
  y=228+i*21
  out.append(f'<text x="696" y="{y+3}" fill="{sub}" font-size="10" class="fine">{i+1:02} {tuple(rec["parent_pair"])}</text><rect x="818" y="{y-7}" width="{rec["depth_upper_bound"]*.80:.1f}" height="8" rx="4" fill="url(#bar)" class="grow" style="animation-delay:{i*.06:.2f}s"/><text x="1144" y="{y+2}" text-anchor="end" fill="{ink}" font-size="11">≤ {rec["depth_upper_bound"]}</text>')
 out += [f'<path class="flow" d="M60,555 H1135" fill="none" stroke="{line}" stroke-width="2"/>']
 for x,title in [(65,'CUT'),(335,'FINITE INTERVAL'),(650,'GENUINE COVERS'),(990,'PAIR BOUND')]:
  out.append(f'<circle cx="{x-12}" cy="554" r="5" fill="{mint}" class="breathe"/><text x="{x}" y="559" font-size="12" font-weight="600" fill="{ink}">{title}</text>')
 out.append(f'<text x="42" y="598" fill="{sub}" font-size="13">22 ≤ D₄ ≤ 346 relative to the supplied census · sharp D₄, Hodge and GSC remain open · click to explore</text></svg>')
 return '\n'.join(out)

for dark in [False,True]:
 p=ROOT/'docs/assets'/('anaxia-seed-explorer-'+('dark' if dark else 'light')+'.svg')
 p.write_text(build(dark),encoding='utf-8')
print('Generated light and dark animated previews from retained witness 2')
