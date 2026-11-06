# Memorization Checklist content: Organic Chemistry and Lab Techniques. Same markup as content_cpas.py.

OCHEM = [
dict(code="OChem-01", title="Acidity: what makes an acid strong (ARIO)",
 hook="A strong acid has a happy (stable) conjugate base. ARIO tells you why.",
 formulas=[], vars=[],
 eli5=r"An acid gives away H⁺ and is left holding a negative charge. If that leftover piece can carry the charge comfortably (spread out, or held by a big or greedy atom), the acid gives up H⁺ easily: it is a strong acid.",
 points=[
  ("A: Atom", [
    r"Down a group, bigger atoms spread charge better → more acidic: HI > HBr > HCl > HF.",
    r"Across a row, more electronegative → more acidic: HF > H₂O > NH₃ > CH₄.",
  ]),
  ("R: Resonance", [
    r"Charge shared over several atoms → more stable base. Carboxylic acid (p$K_a$ ≈ 5) > phenol (≈ 10) > alcohol (≈ 16).",
  ]),
  ("I: Induction", [
    r"Electron-withdrawing groups (F, Cl, NO₂) nearby pull charge away → more acidic. Closer and more of them = stronger. Trifluoroacetic acid (p$K_a$ ≈ 0.2) ≫ acetic acid (4.76).",
  ]),
  ("O: Orbital", [
    r"More s character holds the lone pair closer to the nucleus: sp (alkyne, p$K_a$ ≈ 25) > sp² (alkene, ≈ 44) > sp³ (alkane, ≈ 50).",
  ]),
  r"Lower p$K_a$ = stronger acid. A strong acid has a weak conjugate base.",
 ],
 traps=[
  r"Atom size beats electronegativity when comparing down a group: HF is a **weak** acid even though F is the most electronegative.",
 ],
 mnemonics=[
  r"**ARIO**: check in this order: Atom, Resonance, Induction, Orbital. **\"It's-a me, ARIO!\"**",
  r"**\"Stable base, strong acid.\"**",
 ],
 fig="ochem01-pka.svg", figcap="p$K_a$ ladder of common functional groups (lower = more acidic)."),

dict(code="OChem-02", title="SN1 vs SN2",
 hook="Look at the substrate first, then the nucleophile, then the solvent.",
 formulas=[
  (r"\text{SN2: rate} = k[\text{R–X}][\text{Nu}^-]", "one step, both molecules in the rate law"),
  (r"\text{SN1: rate} = k[\text{R–X}]", "two steps, only the substrate in the rate law"),
 ],
 vars=[
  (r"\text{R–X}", "substrate (alkyl halide)", "", "carbon holding the leaving group X"),
  (r"\text{Nu}^-", "nucleophile", "", "electron-rich attacker (\"nucleus lover\")"),
 ],
 eli5=r"SN2 is a one-step swap: the nucleophile pushes in from the back while the leaving group leaves out the front, flipping the molecule inside out like an umbrella in the wind. SN1 is two steps: the leaving group leaves first, making a flat carbocation, and then the nucleophile attacks from either face.",
 points=[
  ("SN2:", [
    r"One concerted step, backside attack → **inversion** of configuration.",
    r"Substrate: methyl > 1° > 2° (3° is too crowded: no SN2).",
    r"Strong nucleophile; polar **aprotic** solvent (acetone, DMSO, DMF, acetonitrile).",
  ]),
  ("SN1:", [
    r"Two steps; slow step = leaving group leaves to form a carbocation.",
    r"Substrate: 3° > 2° (1° and methyl cations are too unstable: no SN1).",
    r"Weak nucleophile; polar **protic** solvent (water, alcohols). Gives a **racemic** mix; carbocations may rearrange.",
  ]),
  r"Good leaving groups are weak bases: I⁻ > Br⁻ > Cl⁻ > F⁻; tosylate; water after –OH is protonated.",
 ],
 traps=[
  r"The \"1\" and \"2\" refer to how many molecules are in the rate law, not the number of steps (SN1 has 2 steps, SN2 has 1).",
  r"A chiral 3° substrate in water → racemic product (SN1), not inversion.",
 ],
 mnemonics=[
  r"**\"Protic Protects the carbocation\"** → SN1. **\"Aprotic leaves the nucleophile naked and angry\"** → SN2.",
  r"**\"SN2 = 2 molecules collide, 1 step, 1 flip.\"**",
 ],
 fig="ochem02-sn2.svg", figcap="SN2: backside attack through a 5-coordinate transition state; the three other groups flip like an umbrella."),

dict(code="OChem-03", title="E1 vs E2: Zaitsev vs Hofmann",
 hook="Strong base → E2. Bulky base → the less substituted alkene.",
 formulas=[
  (r"\text{E2: rate} = k[\text{R–X}][\text{base}]", "one step"),
  (r"\text{E1: rate} = k[\text{R–X}]", "two steps, through a carbocation"),
 ],
 vars=[],
 eli5=r"Elimination pulls off an H and a leaving group from neighboring carbons to make a C=C double bond. A normal base grabs whichever H gives the most stable (most substituted) alkene. A bulky base is too fat to reach the inner H, so it grabs an H on the outside edge.",
 points=[
  r"E2: one step, strong base, H and leaving group must be **anti-periplanar** (180° apart).",
  r"E1: two steps (carbocation), weak base, heat, polar protic solvent; competes with SN1.",
  r"Zaitsev product = **more** substituted alkene (major with small bases like EtO⁻, OH⁻, and in E1).",
  r"Hofmann product = **less** substituted alkene (major with bulky bases like t-BuO⁻ or LDA).",
  ("Quick decision guide:", [
    r"3° substrate + strong base → E2.",
    r"1° substrate + strong, small nucleophile → SN2. 1° + bulky base → E2.",
    r"3° substrate + weak nucleophile, no heat → SN1; with heat → E1.",
  ]),
  r"Heat favors elimination over substitution (more molecules made → $\Delta S > 0$).",
 ],
 traps=[
  r"In E2 on a cyclohexane, H and leaving group must both be **axial** (trans-diaxial).",
 ],
 mnemonics=[
  r"**\"Zaitsev = Zee most substituted\"**; **\"Hofmann = Hefty base, least substituted.\"**",
  r"**\"Heat makes things leave\"** (Elimination).",
 ],
 fig="ochem03-zaitsev.svg", figcap="2-Bromobutane: small base gives mainly 2-butene (Zaitsev); bulky tert-butoxide gives mainly 1-butene (Hofmann)."),

dict(code="OChem-04", title="Stereochemistry: R/S and D/L",
 hook="Priorities by atomic number, lowest in back, then trace 1 → 2 → 3.",
 formulas=[
  (r"\text{max stereoisomers} = 2^n", "$n$ = number of chiral centers"),
 ],
 vars=[],
 eli5=r"Rank the four groups on the chiral carbon by atomic number. Point the lowest one away from you, like a steering wheel column. If 1 → 2 → 3 turns the wheel clockwise, it's R (Right turn). Counterclockwise is S.",
 points=[
  r"Cahn-Ingold-Prelog priority: higher atomic number at the first point of difference wins. A double bond counts as two single bonds to that atom.",
  r"Lowest priority on a wedge (toward you)? Find the direction, then **reverse** it.",
  r"Swapping any two groups flips R ↔ S. Swapping twice gets you back.",
  r"Fischer projection: horizontal lines come **toward** you, vertical lines go **away**.",
  r"D/L: look at the OH on the chiral carbon **farthest from the carbonyl**. Right = D, left = L. Natural sugars are D; amino acids are L.",
  r"Enantiomers: all centers flipped (mirror images). Diastereomers: some flipped. Meso: has chiral centers but an internal mirror plane, so it is achiral.",
 ],
 traps=[
  r"R/S, D/L, and (+)/(−) optical rotation are three separate labels. None predicts the others.",
  r"Enantiomers share boiling point, melting point, and solubility; diastereomers do not.",
 ],
 mnemonics=[
  r"**R = Right turn (clockwise), S = Sinister (counterclockwise).**",
  r"**D = Dexter = right**; **L = Left** (Latin).",
  r"Fischer: **\"horizontal arms hug you.\"**",
 ],
 fig="ochem04-fischer.svg", figcap="Glyceraldehyde in Fischer projection: OH on the right = D (which is R); OH on the left = L (which is S)."),

dict(code="OChem-05", title="Spectroscopy: IR and ¹H NMR",
 hook="Five IR peaks and one NMR ruler cover nearly every question.",
 formulas=[
  (r"\text{peaks} = n + 1", "NMR splitting: $n$ = neighboring H's on adjacent carbons"),
 ],
 vars=[
  (r"\text{cm}^{-1}", "wavenumber", "", "IR peak position"),
  (r"\text{ppm}", "chemical shift", "", "NMR peak position; higher = more deshielded (downfield)"),
 ],
 eli5=r"IR asks: \"Which bonds are here?\" Each bond vibrates at its own note. NMR asks: \"What is each H next to?\" H's near electron-greedy atoms are exposed (deshielded) and show up farther left (higher ppm).",
 points=[
  ("IR (memorize these five):", [
    r"O–H alcohol: broad, ~3200–3600 cm⁻¹.",
    r"O–H carboxylic acid: very broad, ~2500–3300 cm⁻¹.",
    r"N–H: sharp, ~3300 cm⁻¹ (1° amine shows two spikes).",
    r"C=O: strong, sharp, ~1700 cm⁻¹ (1650–1750).",
    r"C≡C or C≡N: ~2100–2260 cm⁻¹.",
  ]),
  ("¹H NMR shifts:", [
    r"Alkyl 0.9–1.5 · next to C=O 2–2.5 · next to O or halogen 3–4 · alkene 4.5–6.5 · aromatic 6.5–8 · aldehyde 9–10 · carboxylic acid 10–13.",
  ]),
  r"Integration (peak area) = number of H's. Number of peaks = number of distinct H environments.",
  r"Splitting: $n$ neighbors → $n + 1$ peaks (doublet, triplet, quartet…).",
  r"UV-Vis: more conjugation → absorbs longer wavelength.",
 ],
 traps=[
  r"An O–H on a carboxylic acid is much broader and lower than an alcohol O–H.",
  r"H's on the same carbon (equivalent) do not split each other.",
 ],
 mnemonics=[
  r"**\"Deshielded = Downfield = higher ppm.\"**",
  r"IR C=O at 1700: **\"Carbonyl of the 1700s.\"**",
  r"**\"Broad O–H is a Big Old Hug.\"**",
 ],
 fig="ochem05-spec.svg", figcap="Where the key IR bands and ¹H NMR shifts fall."),

dict(code="OChem-06", title="Carbonyls: reactivity and redox",
 hook="Rank the acid derivatives and know your reducing agents.",
 formulas=[], vars=[],
 eli5=r"The carbonyl carbon is a little bit positive (δ+), so electron-rich nucleophiles attack it. The better the leaving group attached to it, and the less it is calmed by nearby lone pairs, the more reactive the carbonyl.",
 points=[
  r"Acid derivative reactivity: acid chloride > anhydride > ester ≈ carboxylic acid > amide.",
  r"You can convert down the ladder (more reactive → less reactive) easily, not up.",
  r"Aldehydes > ketones (less crowded, only one electron-donating alkyl group).",
  r"Aldehydes/ketones undergo nucleophilic **addition**; acid derivatives undergo nucleophilic acyl **substitution**.",
  r"α-hydrogens (next to C=O) are acidic (p$K_a$ ≈ 20) → enolates, aldol reactions, keto-enol tautomerism (keto form favored).",
  ("Redox:", [
    r"LiAlH₄ (strong) reduces aldehydes, ketones, esters, and acids → alcohols. NaBH₄ (mild) reduces only aldehydes and ketones.",
    r"Oxidation: 1° alcohol → aldehyde (PCC) → carboxylic acid (strong oxidants like CrO₃, KMnO₄). 2° alcohol → ketone. 3° alcohol → no reaction.",
  ]),
  r"Aldehyde + 1 alcohol → hemiacetal; + 2 alcohols → acetal (a protecting group). Aldehyde/ketone + 1° amine → imine.",
 ],
 traps=[
  r"PCC stops at the aldehyde; strong oxidants keep going to the carboxylic acid.",
  r"Amides are the least reactive derivative because nitrogen's lone pair donates strongly by resonance.",
 ],
 mnemonics=[
  r"**\"Cats Always Eat Ants\"**: Chloride > Anhydride > Ester > Amide.",
  r"**\"NaBH₄ is Not As Bad\"** (mild); LiAlH₄ is the strong one.",
 ],
 fig="ochem06-derivatives.svg", figcap="Acid derivatives from most to least reactive (acetyl examples)."),
]

LAB = [
dict(code="Lab-01", title="Blotting: Southern, Northern, Western",
 hook="Which molecule, and which probe.",
 formulas=[], vars=[],
 eli5=r"All blots work the same way: separate molecules on a gel, press them onto a membrane, then wash on a \"search probe\" that sticks only to the one you're looking for.",
 points=[
  r"**Southern** blot → **DNA**, detected with a complementary DNA probe.",
  r"**Northern** blot → **RNA**, detected with a complementary nucleic-acid probe.",
  r"**Western** blot → **protein**, detected with an antibody.",
  r"Steps: gel electrophoresis → transfer to membrane → block → probe → detect.",
  r"ELISA: antibody-based test in a plate to detect or measure a protein (e.g., a hormone or HIV antibodies).",
  r"RT-PCR/qPCR measure mRNA via cDNA; they are faster alternatives to a Northern blot.",
 ],
 traps=[
  r"Western blots use antibodies, not nucleic-acid probes.",
 ],
 mnemonics=[
  r"**SNoW DRoP**: **S**outhern = **D**NA, **N**orthern = **R**NA, **o** = **o**, **W**estern = **P**rotein.",
 ],
 fig="lab01-blots.svg", figcap="SNoW DRoP: the target molecule and probe for each blot."),

dict(code="Lab-02", title="Gel electrophoresis and SDS-PAGE",
 hook="DNA runs to red (+), and small things run farthest.",
 formulas=[], vars=[],
 eli5=r"A gel is a jungle gym. An electric field pulls charged molecules through it. Small molecules slip through quickly and travel far; big ones get tangled and stay near the start.",
 points=[
  r"DNA and RNA are negative (phosphate backbone) → migrate toward the **positive anode**.",
  r"Smaller fragments travel **farther**. Compare to a ladder of known sizes.",
  r"Agarose gels for DNA; polyacrylamide gels (PAGE) for proteins.",
  r"SDS-PAGE: SDS unfolds proteins and coats them with uniform negative charge → separates by **mass only**.",
  r"Adding β-mercaptoethanol or DTT breaks disulfide bonds → subunits run separately.",
  r"Native PAGE: protein stays folded → separates by size, shape, and charge; activity is kept.",
  r"Isoelectric focusing: protein stops where pH = pI (net charge 0).",
 ],
 traps=[
  r"In electrophoresis (an electrolytic setup) the anode is **positive**. Oxidation is still at the anode, reduction still at the cathode.",
 ],
 mnemonics=[
  r"**\"Run to red\"**: DNA runs to the red (+) lead.",
  r"**\"Small = Swift.\"**",
 ],
 fig="lab02-gel.svg", figcap="Agarose gel: wells at the negative end; DNA runs toward +; small fragments travel farthest."),

dict(code="Lab-03", title="Chromatography: TLC, column and HPLC",
 hook="Like sticks to like. The one that sticks less comes out first.",
 formulas=[
  (r"R_f = \dfrac{\text{distance moved by spot}}{\text{distance moved by solvent front}}", "retention factor (TLC), always between 0 and 1"),
 ],
 vars=[
  (r"R_f", "retention factor", "no unit", "how far a spot traveled compared with the solvent"),
 ],
 eli5=r"Molecules race through a column or up a plate. The stationary phase is sticky for things like itself. If the plate is polar, polar molecules keep stopping to \"hug\" it and fall behind; nonpolar ones race ahead with the solvent.",
 points=[
  r"Normal phase TLC/column: polar stationary phase (silica) → nonpolar compounds move farthest (high $R_f$) and elute first.",
  r"Reverse-phase HPLC: nonpolar stationary phase (C18), polar mobile phase → **polar compounds elute first**.",
  r"Size-exclusion: **large** molecules elute first (too big to enter the bead pores).",
  r"Ion-exchange: cation-exchange beads are negative and hold positive proteins; anion-exchange beads are positive and hold negative proteins. Elute with salt.",
  r"Affinity: beads carry a specific binding partner (antibody, Ni²⁺ for His-tags); elute with free ligand (e.g., imidazole).",
  r"Gas chromatography: separates by volatility; lower boiling point exits first.",
 ],
 traps=[
  r"\"Reverse phase\" reverses the order: polar comes out first.",
  r"Size-exclusion is the only one where big things win the race.",
 ],
 mnemonics=[
  r"**\"Polar sticks to Polar Plate\"** → low $R_f$.",
  r"Size-exclusion: **\"Big boys skip the maze.\"**",
 ],
 fig="lab03-tlc.svg", figcap="TLC plate on silica: the less polar compound travels farther (higher Rf)."),

dict(code="Lab-04", title="PCR: polymerase chain reaction",
 hook="Hot, cool, warm: 95 → 55 → 72 °C, and copies double each cycle.",
 formulas=[
  (r"\text{copies} = N_0 \times 2^n", "$n$ cycles, $N_0$ starting copies"),
 ],
 vars=[],
 eli5=r"PCR is a DNA photocopier. Heat splits the two strands, cooling lets short primers stick to the edges of the target, and a heat-proof polymerase fills in the rest. Every cycle doubles the copies: 30 cycles ≈ a billion.",
 points=[
  r"**Denature** ~95 °C: H-bonds break, strands separate.",
  r"**Anneal** ~50–65 °C: primers bind to their complementary sequences.",
  r"**Extend** ~72 °C: Taq polymerase builds new DNA 5′ → 3′.",
  r"Taq polymerase comes from *Thermus aquaticus*, a hot-spring bacterium, so it survives 95 °C.",
  r"Ingredients: template DNA, two primers (forward and reverse, flanking the target), dNTPs, Mg²⁺, Taq.",
  r"RT-PCR: reverse transcriptase first turns mRNA into cDNA. qPCR: tracks product in real time; lower Ct = more starting template.",
  r"GC-rich DNA or primers need higher temperatures (3 H-bonds per G–C pair).",
 ],
 traps=[
  r"Human DNA polymerase would be destroyed at 95 °C; that's why Taq is used.",
  r"Primers set what gets copied. No primer match, no product.",
 ],
 mnemonics=[
  r"**\"Hot, Cool, Warm\"**: 95 → 55 → 72.",
  r"**$2^{10} \approx 1000$**, so 30 cycles ≈ $10^9$ copies.",
 ],
 fig="lab04-pcr.svg", figcap="Temperature during three PCR cycles: denature, anneal, extend, repeat."),

dict(code="Lab-05", title="Spectrophotometry: the Beer-Lambert law",
 hook="Absorbance is proportional to concentration. That's how you measure it.",
 formulas=[
  (r"A = \varepsilon\, l\, c", "Beer-Lambert law"),
  (r"A = -\log T = \log\dfrac{I_0}{I}", "absorbance from transmittance"),
  (r"T = \dfrac{I}{I_0}", "fraction of light that gets through"),
 ],
 vars=[
  (r"A", "absorbance", "no unit", "how much light the sample soaks up"),
  (r"\varepsilon", "molar absorptivity", "M⁻¹cm⁻¹", "how strongly the molecule absorbs at that wavelength"),
  (r"l", "path length", "cm", "width of the cuvette, usually 1 cm"),
  (r"c", "concentration", "M", "what you usually solve for"),
  (r"I_0,\ I", "incident and transmitted light", "", "light going in, light coming out"),
 ],
 eli5=r"Shine a flashlight through tea. Stronger tea (higher $c$), a wider cup (longer $l$), or a darker kind of tea (bigger $\varepsilon$) all let less light through. Absorbance goes up in a straight line with concentration, so a standard curve lets you read off an unknown.",
 points=[
  r"Make a standard curve (A vs known c), then read the unknown's concentration from its A.",
  r"A = 1 → 10% of light gets through; A = 2 → 1%.",
  r"Measure at $\lambda_{\max}$ (the wavelength of strongest absorbance) for the best sensitivity.",
  r"Proteins absorb at 280 nm (Trp, Tyr); nucleic acids at 260 nm. Pure DNA has A₂₆₀/A₂₈₀ ≈ 1.8.",
  r"Always zero the instrument with a blank (solvent only).",
 ],
 traps=[
  r"Absorbance and transmittance are not opposites on a straight scale: A is a **log**.",
 ],
 mnemonics=[
  r"$A = \varepsilon l c$: **\"A = ELC\"** (say \"A equals elk\").",
  r"**\"Every +1 in A = 10× less light.\"**",
 ],
 fig="lab05-beer.svg", figcap="Standard curve: absorbance rises linearly with concentration; read an unknown from its absorbance."),
]
