# Memorization Checklist content: Biology & Biochemistry (BBFL). Same markup as content_cpas.py.

BBFL = [
dict(code="BBFL-01", title="Enzyme kinetics: the Michaelis-Menten equation and Km",
 hook="Km is the most tested number in biochemistry. Know what it is and what it is not.",
 formulas=[
  (r"v_0 = \dfrac{V_{\max}[S]}{K_m + [S]}", "Michaelis-Menten equation"),
  (r"V_{\max} = k_{\text{cat}}[E]_T", "maximum rate depends on how much enzyme you have"),
  (r"\text{catalytic efficiency} = \dfrac{k_{\text{cat}}}{K_m}", "the best single measure of a good enzyme"),
  (r"K_m = \dfrac{k_{-1} + k_{\text{cat}}}{k_1}", "what Km is made of"),
 ],
 vars=[
  (r"v_0", "initial reaction rate", "M/s", "speed at the start, before product builds up"),
  (r"V_{\max}", "maximum rate", "M/s", "speed when every enzyme is busy (saturated)"),
  (r"[S]", "substrate concentration", "M", "how much \"food\" the enzyme has"),
  (r"K_m", "Michaelis constant", "M", r"the $[S]$ that gives half of $V_{\max}$"),
  (r"k_{\text{cat}}", "turnover number", "s⁻¹", "reactions one enzyme finishes per second when saturated"),
  (r"[E]_T", "total enzyme concentration", "M", "all enzyme present: free enzyme $[E]$ + enzyme holding substrate $[ES]$"),
  (r"k_1,\ k_{-1}", "binding and unbinding rate constants", "M⁻¹s⁻¹, s⁻¹", "how fast substrate sticks on and falls off"),
 ],
 eli5=r"Picture a car wash. $V_{\max}$ is the top speed when every bay is full. $K_m$ is how many cars must be waiting in line before the wash runs at half speed. A low $K_m$ wash gets busy even with a short line. But $K_m$ is not pure \"stickiness\": it mixes how well cars pull in ($k_1$, $k_{-1}$) with how fast they get washed ($k_{\text{cat}}$). That's why we call it **apparent affinity**.",
 points=[
  r"$K_m$ = $[S]$ at $\tfrac{1}{2}V_{\max}$. Low $K_m$ → half-speed reached at low $[S]$ → higher apparent affinity.",
  r"When $k_{\text{cat}} \ll k_{-1}$, $K_m \approx K_d$ and it really does measure binding.",
  r"Efficiency is $k_{\text{cat}}/K_m$: with the same $k_{\text{cat}}$, a lower $K_m$ means a more efficient enzyme.",
  r"$V_{\max}$ rises if you add more enzyme; $K_m$ does not change with enzyme amount (it is a property of the enzyme).",
  r"$[S] \gg K_m$ → $v_0 \approx V_{\max}$ (zero order in $S$). $[S] \ll K_m$ → $v_0$ rises in proportion to $[S]$ (first order).",
  r"Enzymes lower activation energy. They never change $\Delta G$, $K_{\text{eq}}$, or which direction is favored.",
 ],
 traps=[
  r"\"$K_m$ = affinity\" is only a shortcut. A mutation that speeds up $k_{\text{cat}}$ raises $K_m$ even if binding is unchanged.",
  r"Low $K_m$ by itself does not make an enzyme fast; $V_{\max}$ and $k_{\text{cat}}$ measure speed.",
 ],
 mnemonics=[
  r"**$K_m$ = \"Kinda Medium\"**: the substrate level for medium (half) speed.",
  r"**$k_{\text{cat}}$ = a cat eating mice**: how many substrates one enzyme \"eats\" per second.",
  r"Efficiency = **\"fast cat, low Km wins.\"**",
 ],
 fig="bbfl01-mm.svg", figcap="Michaelis-Menten (MM) graph: the curve levels off at Vmax; Km is the [S] where the rate is Vmax/2."),

dict(code="BBFL-02", title="Reading the Michaelis-Menten (MM) graph vs the Lineweaver-Burk (LB) graph",
 hook="Same enzyme, two graphs. Learn where Km and Vmax hide on each.",
 formulas=[
  (r"\dfrac{1}{v_0} = \dfrac{K_m}{V_{\max}}\cdot\dfrac{1}{[S]} + \dfrac{1}{V_{\max}}", "Lineweaver-Burk (a straight line, y = mx + b)"),
  (r"y\text{-intercept} = \dfrac{1}{V_{\max}}", "where the line hits the vertical axis"),
  (r"x\text{-intercept} = -\dfrac{1}{K_m}", "where the line hits the horizontal axis"),
  (r"\text{slope} = \dfrac{K_m}{V_{\max}}", "steepness of the line"),
 ],
 vars=[
  (r"v_0 \text{ vs } [S]", "Michaelis-Menten (MM) graph", "", r"a curve that rises and flattens at $V_{\max}$"),
  (r"\tfrac{1}{v_0} \text{ vs } \tfrac{1}{[S]}", "Lineweaver-Burk (LB) graph", "", "\"double reciprocal\": flip both axes and the curve becomes a straight line"),
 ],
 eli5=r"The MM graph is the real-life picture: add more substrate, the enzyme speeds up, then maxes out. The LB graph is a math trick: flip both numbers upside down and the curve straightens into a line, so the intercepts are easy to read. The catch: everything on LB is \"one over\" something, so you have to flip back.",
 points=[
  ("MM graph ($v_0$ vs $[S]$):", [
    r"$V_{\max}$ = height of the plateau.",
    r"$K_m$ is read **directly** on the x-axis: go to $V_{\max}/2$ on the y-axis, across to the curve, down to $[S]$.",
  ]),
  ("LB graph ($1/v_0$ vs $1/[S]$):", [
    r"y-intercept = $1/V_{\max}$. Higher y-intercept → **lower** $V_{\max}$.",
    r"x-intercept = $-1/K_m$. Solve algebraically: $K_m = -1/(\text{x-intercept})$. Example: x-intercept = −0.5 mM⁻¹ → $K_m$ = 2 mM.",
    r"Smaller $K_m$ → $-1/K_m$ is a bigger negative number → x-intercept moves **left** (farther from zero).",
    r"Larger $K_m$ → x-intercept moves **right** (closer to zero).",
  ]),
  r"On LB, the right side of the graph is **low** $[S]$ (big $1/[S]$); the y-axis itself is infinite $[S]$.",
 ],
 traps=[
  r"On LB, \"left\" means smaller $K_m$, not \"needs less substrate at every point.\" Always flip back to the real value.",
  r"A higher LB line (bigger $1/v_0$) means a **slower** enzyme.",
 ],
 mnemonics=[
  r"**\"Y is for Vmax, X marks Km\"** (and both are upside down).",
  r"**\"Flip it to find it\"**: $K_m = -1/\text{x-int}$, $V_{\max} = 1/\text{y-int}$.",
 ],
 fig="bbfl02-mm-lb.svg", figcap="The same two enzymes on both graphs. Lower Km (orange): reaches half-speed sooner on MM; x-intercept farther left on LB."),

dict(code="BBFL-03", title="Enzyme inhibitors: what happens to Km and Vmax",
 hook="One table, memorized cold, answers every inhibitor question.",
 formulas=[
  (r"\alpha = 1 + \dfrac{[I]}{K_i}", "how strongly the inhibitor acts"),
  (r"\text{Competitive: } K_m^{\text{app}} = \alpha K_m,\quad V_{\max} \text{ unchanged}", ""),
  (r"\text{Noncompetitive: } V_{\max}^{\text{app}} = \dfrac{V_{\max}}{\alpha},\quad K_m \text{ unchanged}", ""),
  (r"\text{Uncompetitive: } K_m^{\text{app}} = \dfrac{K_m}{\alpha'},\quad V_{\max}^{\text{app}} = \dfrac{V_{\max}}{\alpha'}", ""),
 ],
 vars=[
  (r"[I]", "inhibitor concentration", "M", ""),
  (r"K_i", "inhibitor dissociation constant", "M", "low $K_i$ = inhibitor binds tightly"),
  (r"K_m^{\text{app}}", "apparent Km", "M", "the Km you measure with inhibitor present"),
 ],
 eli5=r"**Competitive**: a kid sitting in your chair (active site). Bring enough friends (substrate) and you win the chair back, so $V_{\max}$ is still reachable but you need more substrate ($K_m$ up). **Noncompetitive**: someone jams the machine from the side; more substrate can't fix it ($V_{\max}$ down). **Uncompetitive**: the inhibitor only grabs enzymes already holding substrate and locks them, so both numbers drop.",
 points=[
  ("Competitive (binds free enzyme at the active site):", [
    r"$K_m$ ↑, $V_{\max}$ same. LB lines cross **on the y-axis**. Overcome by adding more substrate.",
  ]),
  ("Noncompetitive (binds E and ES equally, at another site):", [
    r"$K_m$ same, $V_{\max}$ ↓. LB lines cross **on the x-axis**.",
  ]),
  ("Uncompetitive (binds only the ES complex):", [
    r"$K_m$ ↓ **and** $V_{\max}$ ↓ by the same factor. LB lines are **parallel**.",
  ]),
  ("Mixed (binds E and ES, but not equally):", [
    r"$V_{\max}$ ↓; $K_m$ ↑ if it prefers E, ↓ if it prefers ES. LB lines cross left of the y-axis, off the x-axis.",
  ]),
  r"Irreversible inhibitors (like aspirin on COX) act like removing enzyme: $V_{\max}$ ↓.",
 ],
 traps=[
  r"Only **competitive** inhibition can be overcome by flooding with substrate.",
  r"Uncompetitive inhibition **lowers** $K_m$ (apparent affinity goes up), even though the enzyme is inhibited.",
 ],
 mnemonics=[
  r"**Competitive → Crosses at the Y-axis** (Km goes up, \"compete\" for the seat).",
  r"**Noncompetitive → No change in Km**, crosses at the x-axis.",
  r"**UNcompetitive → UNder for both** (Km and Vmax both drop), lines parallel like the two lines in \"U\".",
 ],
 fig="bbfl03-inhibitors.svg", figcap="Lineweaver-Burk patterns: competitive (same y-intercept), noncompetitive (same x-intercept), uncompetitive (parallel lines)."),

dict(code="BBFL-04", title="Isoelectric point (pI) and amino acid charge",
 hook="Average the right two pKas and you have the pI.",
 formulas=[
  (r"\text{pI} = \dfrac{\text{p}K_{a1} + \text{p}K_{a2}}{2}", "neutral side chain: average the two backbone pKas"),
  (r"\text{pI} = \dfrac{\text{p}K_{a,\text{COOH}} + \text{p}K_{a,\text{side}}}{2}", "acidic side chain (Asp, Glu)"),
  (r"\text{pI} = \dfrac{\text{p}K_{a,\text{NH}_3^+} + \text{p}K_{a,\text{side}}}{2}", "basic side chain (Lys, Arg, His)"),
 ],
 vars=[
  (r"\text{pI}", "isoelectric point", "pH units", "the pH where net charge = 0"),
  (r"\text{p}K_{a1}", "α-carboxyl pKa", "≈ 2", ""),
  (r"\text{p}K_{a2}", "α-amino pKa", "≈ 9–9.5", ""),
  (r"\text{p}K_{a,\text{side}}", "side-chain pKa", "", "Asp 3.9, Glu 4.1, His 6.0, Cys 8.3, Tyr 10.1, Lys 10.5, Arg 12.5"),
 ],
 eli5=r"Each group holds onto its H⁺ when the pH is below its p$K_a$ and lets go above it. The pI is the pH where the + and − charges cancel. Rule of thumb: average the two p$K_a$ values on either side of the neutral (zwitterion) form.",
 points=[
  r"Neutral amino acids: pI ≈ (2 + 9.5)/2 ≈ 5.5–6.",
  r"Acidic: Asp pI ≈ (2 + 3.9)/2 ≈ 3. Basic: Lys ≈ (9 + 10.5)/2 ≈ 9.8, Arg ≈ 10.8, His ≈ 7.6.",
  r"pH **below** pI → net **positive**. pH **above** pI → net **negative**.",
  r"At physiological pH 7.4: Asp, Glu are −; Lys, Arg are +; His is mostly neutral (p$K_a$ 6).",
  r"Isoelectric focusing: a protein moves through a pH gradient and stops where pH = its pI.",
 ],
 traps=[
  r"For acidic amino acids, average the two **low** pKas; for basic ones, average the two **high** pKas. Never average all three.",
 ],
 mnemonics=[
  r"**\"pH Below pI → Bonus protons → Positive.\"**",
  r"**\"Protons stay on when pH is below pKa.\"**",
 ],
 fig="bbfl04-gly.svg", figcap="Glycine titration curve: plateaus at pKa1 ≈ 2.3 and pKa2 ≈ 9.6; pI = (2.3 + 9.6)/2 ≈ 6.0 at the first equivalence point."),

dict(code="BBFL-06", title="The 20 amino acids by group",
 hook="Know each group, its one-letter codes, and the oddballs (Gly, Pro, Cys, His).",
 formulas=[],
 vars=[],
 eli5=r"Sort amino acids by how their side chain feels about water. Nonpolar ones are greasy and hide inside proteins. Polar ones like water. Acidic ones carry a − charge and basic ones carry a + charge at body pH.",
 points=[
  ("Nonpolar (hydrophobic): G A V L I M P F W", [
    r"Glycine, Alanine, Valine, Leucine, Isoleucine, Methionine, Proline, Phenylalanine, Tryptophan.",
  ]),
  ("Polar, uncharged: S T C N Q Y", [
    r"Serine, Threonine, Cysteine, Asparagine, Glutamine, Tyrosine.",
  ]),
  ("Acidic (negative at pH 7.4): D E", [
    r"Aspartate (Asp, D), Glutamate (Glu, E).",
  ]),
  ("Basic (positive at pH 7.4): K R H", [
    r"Lysine (K), Arginine (R), Histidine (H; p$K_a$ 6, so only partly charged).",
  ]),
  ("Aromatic: F Y W", [
    r"Absorb UV at 280 nm (mostly Trp and Tyr), which is how we measure protein concentration.",
  ]),
  ("Oddballs:", [
    r"**Glycine**: side chain is just H → achiral, very flexible.",
    r"**Proline**: ring locks the backbone → breaks α-helices, common in turns.",
    r"**Cysteine**: SH group forms disulfide bridges (–S–S–). Cys and Met contain sulfur.",
    r"**Histidine**: p$K_a$ near 7 → buffers and acts as an acid/base in active sites.",
    r"Ser, Thr, Tyr have OH groups → sites of phosphorylation by kinases.",
  ]),
  r"All amino acids in human proteins are L. All chiral L-amino acids are (S) except Cysteine, which is (R).",
  r"One-letter codes that don't match: **F** = Phe (\"Fenylalanine\"), **W** = Trp (\"tWyptophan\", double ring), **Y** = Tyr, **R** = Arg (\"aRginine\"), **K** = Lys (K is next to L), **D** = Asp (\"asparDic\"), **E** = Glu (\"glutEmate\"), **N** = Asn (\"asparagiNe\"), **Q** = Gln (\"Q-tamine\").",
 ],
 traps=[
  r"Tyrosine is aromatic **and** polar (its OH). Tryptophan is aromatic and usually grouped with nonpolar.",
  r"Asparagine (N) and glutamine (Q) are the **amides** of aspartate and glutamate: polar but **not** charged.",
 ],
 mnemonics=[
  r"Nonpolar **G A V L I M P F W**: **\"Grumpy Aliens Visit Lonely Islands; Many Penguins Fly Westward.\"**",
  r"Polar **S T C N Q Y**: **\"STaCy Never Quits Yoga.\"**",
  r"Acidic **D E**: **\"DEad negative\"**: D and E carry the − charge.",
  r"Basic **K R H**: **\"Kinda Really Happy\"**: happy = positive.",
  r"Aromatic **F Y W**: **\"For Your Whiff\"** (aromatic = smells).",
  r"Essential amino acids: **\"PVT TIM HaLL\"**: Phe, Val, Thr, Trp, Ile, Met, His, Leu, Lys (Arg only in growth).",
 ],
 fig="bbfl06-aa.svg", figcap="Side chains grouped by property. Structures drawn from verified SMILES at pH 7.4."),

dict(code="BBFL-07", title="Hemoglobin and the O₂ dissociation curve",
 hook="Sigmoid vs hyperbola, and what shifts the curve right or left.",
 formulas=[],
 vars=[
  (r"P_{50}", "O₂ partial pressure at 50% saturation", "mmHg", "Hb ≈ 26 mmHg, myoglobin ≈ 2–3 mmHg"),
  (r"\text{Hb},\ \text{Mb}", "hemoglobin, myoglobin", "", "Hb: 4 subunits, carries O₂ in blood; Mb: 1 subunit, stores O₂ in muscle"),
 ],
 eli5=r"Hemoglobin is a delivery truck with four seats. Once one O₂ sits down, the others hop on more easily (cooperativity), which makes the S-shaped curve. In hard-working tissue (hot, acidic, lots of CO₂) the truck lets go of O₂ more easily: that's a right shift. Myoglobin is a storage locker: it grabs O₂ tightly and only lets go when muscle is desperate.",
 points=[
  r"Hb: sigmoidal curve (cooperative binding). Mb: hyperbolic curve (one site, no cooperativity), higher affinity.",
  r"**Right shift** = lower affinity = more O₂ unloaded to tissues; $P_{50}$ goes **up**.",
  r"Right shift causes: ↑CO₂, ↑H⁺ (↓pH), ↑2,3-BPG, exercise, ↑temperature.",
  r"**Left shift** = higher affinity: fetal hemoglobin (HbF), carbon monoxide, ↓temperature, ↑pH, ↓2,3-BPG.",
  r"Bohr effect: H⁺ and CO₂ lower Hb's O₂ affinity.",
  r"CO binds Hb about 200–250× more tightly than O₂, blocking seats **and** shifting the curve left.",
 ],
 traps=[
  r"Fetal Hb binds 2,3-BPG **poorly**, so its curve is shifted **left** (it pulls O₂ from mom).",
  r"Right shift means \"lets go more easily,\" not \"carries more.\"",
 ],
 mnemonics=[
  r"**\"CADET, face Right!\"**: CO₂, Acid, 2,3-DPG (BPG), Exercise, Temperature.",
  r"**\"Fetal = Firm grip = Left.\"**",
 ],
 fig="bbfl07-hb.svg", figcap="Hemoglobin (sigmoid) and myoglobin (hyperbola). A right shift raises P50 and unloads more O₂."),

dict(code="BBFL-11", title="Metabolism: the rate-limiting enzymes",
 hook="Each pathway has one gatekeeper enzyme. Know it and what turns it on or off.",
 formulas=[],
 vars=[],
 eli5=r"Every pathway is a road with one toll booth that sets the speed of the whole road. Control the toll booth and you control the traffic. Lots of energy (ATP) slows the energy-making roads; low energy (AMP) speeds them up.",
 points=[
  r"Glycolysis: **PFK-1**. Activated by AMP and fructose-2,6-bisphosphate; inhibited by ATP and citrate.",
  r"Gluconeogenesis: **fructose-1,6-bisphosphatase**.",
  r"Glycogen synthesis: **glycogen synthase** (insulin). Glycogen breakdown: **glycogen phosphorylase** (glucagon, epinephrine).",
  r"Pentose phosphate pathway: **glucose-6-phosphate dehydrogenase (G6PD)**, which makes NADPH.",
  r"Citric acid cycle: **isocitrate dehydrogenase**. Inhibited by ATP and NADH, activated by ADP.",
  r"Fatty acid synthesis: **acetyl-CoA carboxylase**. β-oxidation: **carnitine acyltransferase I (CPT-1)**.",
  r"Cholesterol synthesis: **HMG-CoA reductase** (blocked by statins).",
  r"Urea cycle: **carbamoyl phosphate synthetase I**.",
  r"ATP yield ≈ 30–32 per glucose. Each NADH ≈ 2.5 ATP, each FADH₂ ≈ 1.5 ATP.",
  r"Insulin (fed state) → build and store. Glucagon (fasting) → break down and release.",
 ],
 traps=[
  r"Hexokinase is not the rate-limiting step of glycolysis; PFK-1 is.",
  r"Citrate inhibits PFK-1 but activates acetyl-CoA carboxylase (plenty of fuel → store it as fat).",
 ],
 mnemonics=[
  r"**\"PFK = Pretty Freaking Key\"** for glycolysis.",
  r"**\"Statins Stop the Sterol factory\"** (HMG-CoA reductase).",
  r"**\"Insulin = In storage; Glucagon = Glucose gone out.\"**",
 ],
 fig=None),

dict(code="BBFL-05", title="Hardy-Weinberg equilibrium",
 hook="Start from the recessive phenotype, take the square root, and you have q.",
 formulas=[
  (r"p + q = 1", "allele frequencies"),
  (r"p^2 + 2pq + q^2 = 1", "genotype frequencies"),
 ],
 vars=[
  (r"p", "dominant allele frequency", "", ""),
  (r"q", "recessive allele frequency", "", ""),
  (r"p^2", "homozygous dominant", "", "AA"),
  (r"2pq", "heterozygous carriers", "", "Aa"),
  (r"q^2", "homozygous recessive", "", "aa: the only genotype that **shows** a recessive trait"),
 ],
 eli5=r"Put every allele in a big bag. $p$ is the share that are A, $q$ the share that are a. Pull two at random to make a baby: AA happens $p \times p$ of the time, aa $q \times q$, and Aa can happen two ways, so $2pq$.",
 points=[
  r"Recipe: fraction showing the recessive trait = $q^2$ → $q = \sqrt{q^2}$ → $p = 1 - q$ → carriers = $2pq$.",
  r"Example: 1 in 10,000 affected → $q$ = 0.01, $p$ ≈ 0.99 → carriers ≈ 2% (about 1 in 50).",
  r"Shortcut when $q$ is small: carriers ≈ $2q$.",
  r"Five conditions: large population, random mating, no mutation, no migration (gene flow), no natural selection.",
  r"If the conditions hold, allele frequencies stay the same every generation (no evolution).",
 ],
 traps=[
  r"Dominant phenotype = $p^2 + 2pq$, not $p^2$. Always start with the recessive phenotype.",
  r"For X-linked traits in males, the affected fraction equals $q$ (one X), not $q^2$.",
 ],
 mnemonics=[
  r"**\"q-squared shows the trait.\"**",
  r"Conditions: a **\"boring\" population**: big, random, closed, no new mutations, no favorites.",
 ],
 fig="bbfl05-hw.svg", figcap="A Punnett square for a whole population: the areas are p², 2pq and q²."),

dict(code="BBFL-08", title="DNA replication and the central dogma",
 hook="5′ → 3′ always, and the enzymes at the fork in order.",
 formulas=[],
 vars=[],
 eli5=r"DNA is a zipper. Helicase unzips it, and polymerase builds a new half on each old half. Polymerase can only add to the 3′ end, so one new strand (leading) is built smoothly toward the fork, and the other (lagging) is built backward in short pieces (Okazaki fragments) that get glued together.",
 points=[
  r"Central dogma: DNA → RNA (transcription) → protein (translation). Retroviruses use reverse transcriptase: RNA → DNA.",
  r"Replication is semiconservative: each new double helix = 1 old strand + 1 new strand.",
  r"New strands grow 5′ → 3′; the template is read 3′ → 5′.",
  ("Enzymes at the fork, in order:", [
    r"Helicase unwinds → single-strand binding proteins (SSB) keep strands apart → topoisomerase (gyrase) relieves supercoiling ahead.",
    r"Primase lays an RNA primer → DNA polymerase III (prokaryotes) or δ/ε (eukaryotes) extends from the primer's 3′-OH.",
    r"DNA polymerase I (prokaryotes) or RNase H (eukaryotes) removes primers → DNA ligase seals the gaps.",
  ]),
  r"Leading strand: continuous, toward the fork. Lagging strand: Okazaki fragments, away from the fork.",
  r"Telomerase extends chromosome ends using its own RNA template (active in stem and cancer cells).",
  r"A pairs with T by **2** H-bonds; G pairs with C by **3**, so GC-rich DNA melts at a higher temperature.",
  r"Prokaryotes: one origin, circular DNA. Eukaryotes: many origins, linear chromosomes.",
 ],
 traps=[
  r"DNA polymerase cannot start from scratch; it needs a primer. RNA polymerase does not.",
  r"Polymerase proofreads with 3′ → 5′ exonuclease activity, even though it builds 5′ → 3′.",
 ],
 mnemonics=[
  r"Purines (two rings): **\"Pure As Gold\"** (A, G). Pyrimidines: **\"CUT the Py\"** (C, U, T).",
  r"Fork order: **\"Hungry Sharks Took Pretty Pink Lollipops\"**: Helicase, SSB, Topoisomerase, Primase, Polymerase, Ligase.",
  r"**\"Leading leads, lagging lags\"**: smooth vs choppy.",
 ],
 fig="bbfl08-fork.svg", figcap="Replication fork moving right: the leading strand grows continuously toward the fork; the lagging strand grows away from it in Okazaki fragments."),

dict(code="BBFL-09", title="Mitosis vs meiosis",
 hook="Count chromosomes by counting centromeres, and know which division splits what.",
 formulas=[],
 vars=[
  (r"2n", "diploid", "", "two copies of each chromosome; humans 2n = 46"),
  (r"n", "haploid", "", "one copy of each; human gametes n = 23"),
 ],
 eli5=r"Mitosis is a photocopier: one cell becomes two identical cells. Meiosis is a card shuffle: one cell becomes four different cells with half the cards each, so sperm + egg can add back up to a full deck.",
 points=[
  r"Mitosis: 1 division → 2 identical diploid cells (2n → 2n). Body cells, growth, repair.",
  r"Meiosis: 2 divisions → 4 genetically different haploid cells (2n → n). Gametes.",
  r"**Meiosis I** separates homologous chromosomes (reductional: 2n → n). **Meiosis II** separates sister chromatids (like mitosis).",
  r"Crossing over: prophase I, between homologs (tetrads, chiasmata). Independent assortment: metaphase I.",
  r"Count chromosomes by centromeres. After S phase a human cell has 46 chromosomes but 92 chromatids. After meiosis I: 23 chromosomes, 46 chromatids.",
  r"Cell cycle: G1 → S (DNA copied) → G2 → M. Phases of M: prophase, metaphase, anaphase, telophase.",
  r"Nondisjunction (failure to separate) → aneuploidy, like trisomy 21.",
 ],
 traps=[
  r"Cells are already haploid after meiosis I, even though each chromosome still has two chromatids.",
  r"Sister chromatids are identical copies; homologous chromosomes come one from mom and one from dad.",
 ],
 mnemonics=[
  r"**PMAT**: **\"Please Make Another Twin.\"**",
  r"**\"Meiosis I splits the Individuals (homolog pairs); Meiosis II splits the twins (sisters).\"**",
  r"**\"Mitosis = My Identical Twin.\"**",
 ],
 fig="bbfl09-ploidy.svg", figcap="Chromosomes and chromatids in one human cell through the cell cycle and meiosis."),

dict(code="BBFL-10", title="Immunology: innate vs adaptive",
 hook="Who responds first, who remembers, and which MHC talks to which T cell.",
 formulas=[],
 vars=[],
 eli5=r"Innate immunity is the security guard: always on duty, attacks anything suspicious, but never remembers faces. Adaptive immunity is the detective: slow the first time, very specific, and keeps a file (memory cells) so the next attack is crushed fast.",
 points=[
  ("Innate (fast, nonspecific, no memory):", [
    r"Skin and mucus, macrophages, neutrophils (first to arrive, most abundant white cell), natural killer (NK) cells, complement, fever, inflammation, interferons.",
  ]),
  ("Adaptive (slow at first, specific, memory):", [
    r"B cells (mature in **B**one marrow) → plasma cells make antibodies: humoral immunity.",
    r"T cells (mature in **T**hymus): helper CD4⁺ and cytotoxic CD8⁺: cell-mediated immunity.",
  ]),
  ("MHC presentation:", [
    r"MHC I: on all nucleated cells; shows peptides from **inside** the cell → recognized by **CD8** cytotoxic T cells (kill infected or cancer cells).",
    r"MHC II: only on antigen-presenting cells (dendritic cells, macrophages, B cells); shows peptides from **outside** → recognized by **CD4** helper T cells.",
  ]),
  ("Antibody classes (GAMED):", [
    r"IgG: most common, crosses the placenta. IgA: in secretions and breast milk. IgM: made first, a pentamer. IgE: allergy and parasites. IgD: B-cell receptor.",
  ]),
  r"Active immunity: your body makes antibodies (infection, vaccine). Passive: you receive them (breast milk, placenta, antibody injection).",
 ],
 traps=[
  r"Red blood cells have no nucleus, so no MHC I.",
  r"NK cells are innate: they kill cells that are **missing** MHC I.",
 ],
 mnemonics=[
  r"**Rule of 8**: CD**4** × MHC **II** = 8; CD**8** × MHC **I** = 8.",
  r"Antibodies: **GAMED** (IgG, IgA, IgM, IgE, IgD).",
  r"White cell counts, most to least: **\"Never Let Monkeys Eat Bananas\"**: neutrophils, lymphocytes, monocytes, eosinophils, basophils.",
 ],
 fig="bbfl10-mhc.svg", figcap="MHC I presents inside peptides to CD8 T cells; MHC II on antigen-presenting cells presents outside peptides to CD4 T cells."),
]
