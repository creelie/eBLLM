---
id: YM.window
status: open
lean: none
---

# YM.window

the crossover window: order-one coupling, uniformly in the spacing

Part of [[YM.lattice]].
- [[YM.window.box]] (open)
- [[YM.window.lift]] (open)

- round 0, **flow-surgery**: known failure. t^2 E(t) along the Wilson flow is not monotone on a finite torus; no sup-norm control at order-one coupling (source: yang-mills/agents2/crossover.md)
- round 0, **reduction**: known failure. Tomboulis decimations: refuted as written (Kanazawa's U(1) reductio) (source: yang-mills/agents/route-tomboulis.md)
- round 0, **physics-first**: known failure. large-N master loop: needs a weak-coupling a priori estimate nobody has (source: yang-mills/agents/route-largeN.md)
- round 0, **descent**: known failure. Balaban's multiscale induction is controlled only at small coupling (source: yang-mills/agents/route-balaban.md)
- round 1, **construction**: stopped. no checkable formulation of 'construction' at this node is implemented
- round 2, **counterexample**: stopped. no checkable formulation of 'counterexample' at this node is implemented
- round 3, **certificate**: rejected. single-link Dobrushin certificates end at beta_W = 2/9: the coefficient is >= 1 beyond it, so no single-link certificate exists in the window
- round 4, **lift**: stopped. the gap exists at every coupling in two dimensions (string tension -log(I_2/I_1) > 0), but there is no deformation from d = 2 to d = 4: 2D gauge fields have no local degrees of freedom
