/* 520 Quest question generator: builds fresh calculation questions with new numbers every time.
   Each question id is "g_<template>_<seed>", so the same id always rebuilds the same question
   (that is how missed generated questions come back in the Revenge queue). */
(function () {
  function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const pick = (r, arr) => arr[Math.floor(r() * arr.length)];
  const int = (r, lo, hi) => lo + Math.floor(r() * (hi - lo + 1));
  // Up to 3 significant figures, no trailing zeros.
  const f = n => { if (!isFinite(n)) return "∞"; if (n === 0) return "0"; const a = Math.abs(n); const d = a >= 100 ? 0 : a >= 10 ? 1 : a >= 1 ? 2 : 3; return String(+n.toFixed(d)); };
  const frac = (n, d) => { const g = (a, b) => b ? g(b, a % b) : a; const k = g(n, d); return (n / k) + "/" + (d / k); };

  // Each template returns { q, right: [text, why], wrong: [[text, why] x3], note }.
  const T = [
    { k: "fall", s: "CP", c: "4A", d: 1, build(r) {
      const t = int(r, 2, 6), h = 5 * t * t;
      return { q: `A rock is dropped from rest off a ${h} m cliff. Ignoring air resistance, how long does it take to hit the ground? (g = 10 m/s²)`,
        right: [`${t} s`, `h = ½gt², so t = √(2h/g) = √(${2 * h}/10) = ${t} s.`],
        wrong: [[`${f(t * t)} s`, "Forgot the square root."], [`${f(Math.sqrt(h / 10))} s`, "Dropped the factor of 2 in t = √(2h/g)."], [`${f(h / 10)} s`, "Divided height by g; that is not a time formula."]],
        note: "Free fall from rest: h = ½gt² and v = gt." }; } },
    { k: "vfall", s: "CP", c: "4A", d: 1, build(r) {
      const v = pick(r, [10, 20, 30, 40]), h = v * v / 20;
      return { q: `A ball is dropped from rest from a height of ${h} m. What is its speed just before it lands? (g = 10 m/s², ignore air resistance)`,
        right: [`${v} m/s`, `v = √(2gh) = √(2·10·${h}) = ${v} m/s.`],
        wrong: [[`${f(Math.sqrt(10 * h))} m/s`, "Dropped the 2 in v = √(2gh)."], [`${2 * v} m/s`, "Doubled the correct answer."], [`${f(20 * h)} m/s`, "Forgot to take the square root of 2gh."]],
        note: "Energy shortcut: mgh = ½mv², so mass cancels." }; } },
    { k: "range", s: "CP", c: "4A", d: 2, build(r) {
      const t = int(r, 1, 4), h = 5 * t * t, v = pick(r, [5, 10, 15, 20]);
      return { q: `A ball rolls off a ${h} m high table at ${v} m/s horizontally. How far from the table does it land? (g = 10 m/s²)`,
        right: [`${v * t} m`, `Fall time t = √(2h/g) = ${t} s; horizontal distance = v·t = ${v}·${t} = ${v * t} m.`],
        wrong: [[`${v * h / 10} m`, "Used h/g as the fall time instead of √(2h/g)."], [`${f(v * t / 2)} m`, "Halved the distance; horizontal speed is constant."], [`${v * t * t} m`, "Used t² instead of t for horizontal motion."]],
        note: "Horizontal and vertical motion are independent: time comes from the fall." }; } },
    { k: "ke", s: "CP", c: "4A", d: 1, build(r) {
      const m = pick(r, [2, 4, 5, 10, 20]), v = pick(r, [2, 3, 4, 6, 10]), ke = m * v * v / 2;
      return { q: `What is the kinetic energy of a ${m} kg object moving at ${v} m/s?`,
        right: [`${f(ke)} J`, `KE = ½mv² = ½·${m}·${v}² = ${f(ke)} J.`],
        wrong: [[`${f(m * v * v)} J`, "Forgot the ½."], [`${f(m * v / 2)} J`, "Forgot to square the velocity."], [`${f(m * v)} J`, "That is momentum (kg·m/s), not energy."]],
        note: "Doubling speed quadruples kinetic energy." }; } },
    { k: "power", s: "CP", c: "4A", d: 2, build(r) {
      const m = pick(r, [10, 20, 50]), h = pick(r, [2, 3, 4, 5]), t = pick(r, [2, 4, 5, 10]), P = m * 10 * h / t;
      return { q: `A motor lifts a ${m} kg load ${h} m straight up at constant speed in ${t} s. What average power does it deliver? (g = 10 m/s²)`,
        right: [`${f(P)} W`, `P = W/t = mgh/t = ${m}·10·${h}/${t} = ${f(P)} W.`],
        wrong: [[`${f(m * 10 * h)} W`, "That is the work in joules; divide by time."], [`${f(m * h / t)} W`, "Left out g, so this uses mass instead of weight."], [`${f(m * 10 * h * t)} W`, "Multiplied by time instead of dividing."]],
        note: "Power = work / time = force × velocity." }; } },
    { k: "ohm", s: "CP", c: "4C", d: 1, build(r) {
      const R = pick(r, [2, 4, 5, 10, 20]), I = pick(r, [0.5, 1, 2, 3]), V = R * I;
      return { q: `A ${f(V)} V battery drives current through a single ${R} Ω resistor. What current flows?`,
        right: [`${f(I)} A`, `I = V/R = ${f(V)}/${R} = ${f(I)} A.`],
        wrong: [[`${f(V * R)} A`, "Multiplied V by R instead of dividing."], [`${f(R / V)} A`, "Inverted the ratio; I = V/R."], [`${f(V * V / R)} A`, "That is power in watts (V²/R)."]],
        note: "Ohm's law: V = IR." }; } },
    { k: "par", s: "CP", c: "4C", d: 2, build(r) {
      const [a, b] = pick(r, [[3, 6], [4, 4], [6, 12], [10, 10], [4, 12], [12, 6], [20, 5], [2, 2]]), p = a * b / (a + b);
      return { q: `Resistors of ${a} Ω and ${b} Ω are connected in parallel. What is the equivalent resistance?`,
        right: [`${f(p)} Ω`, `1/R = 1/${a} + 1/${b}, so R = (${a}·${b})/(${a}+${b}) = ${f(p)} Ω.`],
        wrong: [[`${a + b} Ω`, "That is the series sum."], [`${f((a + b) / 2)} Ω`, "Averaged them; parallel resistance is less than the smallest resistor."], [`${f(1 / a + 1 / b)} Ω`, "Stopped at 1/R; take the reciprocal."]],
        note: "Parallel resistance is always smaller than the smallest branch." }; } },
    { k: "pwr", s: "CP", c: "4C", d: 2, build(r) {
      const V = pick(r, [6, 10, 12, 20, 120]), R = pick(r, [2, 3, 4, 5, 6, 10]), P = V * V / R;
      return { q: `How much power is dissipated by a ${R} Ω resistor connected across ${V} V?`,
        right: [`${f(P)} W`, `P = V²/R = ${V}²/${R} = ${f(P)} W.`],
        wrong: [[`${f(V / R)} W`, "That is the current in amps."], [`${f(V * R)} W`, "Multiplied V by R; P = V²/R."], [`${f(V * V * R)} W`, "Multiplied by R instead of dividing."]],
        note: "P = IV = I²R = V²/R." }; } },
    { k: "cap", s: "CP", c: "4C", d: 2, build(r) {
      const C = pick(r, [2, 4, 5, 10]), V = pick(r, [2, 4, 10, 20]), U = C * V * V / 2;
      return { q: `A ${C} μF capacitor is charged to ${V} V. How much energy does it store?`,
        right: [`${f(U)} μJ`, `U = ½CV² = ½·${C} μF·${V}² = ${f(U)} μJ.`],
        wrong: [[`${f(C * V * V)} μJ`, "Forgot the ½."], [`${f(C * V)} μJ`, "That is the charge Q = CV, in μC."], [`${f(C * V / 2)} μJ`, "Forgot to square the voltage."]],
        note: "U = ½QV = ½CV² = Q²/2C." }; } },
    { k: "gay", s: "CP", c: "4B", d: 2, build(r) {
      const T1 = pick(r, [200, 250, 300, 400]), k = pick(r, [1.5, 2, 3]), T2 = T1 * k, P1 = pick(r, [1, 2, 3]);
      return { q: `A sealed rigid container of gas at ${P1} atm is heated from ${T1} K to ${f(T2)} K. What is the new pressure?`,
        right: [`${f(P1 * k)} atm`, `At constant volume P/T is constant: P₂ = ${P1}·(${f(T2)}/${T1}) = ${f(P1 * k)} atm.`],
        wrong: [[`${f(P1 / k)} atm`, "Inverted the temperature ratio; heating raises pressure."], [`${P1} atm`, "Pressure does change when a rigid container is heated."], [`${f(P1 + (T2 - T1) / 100)} atm`, "Pressure scales with the ratio of absolute temperatures, not the difference."]],
        note: "Always use kelvin in gas laws." }; } },
    { k: "boyle", s: "CP", c: "4B", d: 1, build(r) {
      const P1 = pick(r, [1, 2, 3, 4]), V1 = pick(r, [2, 4, 6, 12]), k = pick(r, [2, 3, 4]), V2 = V1 * k;
      return { q: `At constant temperature, ${V1} L of gas at ${P1} atm expands to ${V2} L. What is the new pressure?`,
        right: [`${f(P1 / k)} atm`, `Boyle's law: P₁V₁ = P₂V₂, so P₂ = ${P1}·${V1}/${V2} = ${f(P1 / k)} atm.`],
        wrong: [[`${f(P1 * k)} atm`, "Pressure falls when volume rises at constant T."], [`${f(P1 - (V2 - V1) / 10)} atm`, "Pressure scales with the volume ratio, not the difference."], [`${P1} atm`, "Pressure must change when volume changes at constant T."]],
        note: "Boyle: P and V are inversely proportional." }; } },
    { k: "cont", s: "CP", c: "4B", d: 2, build(r) {
      const v = pick(r, [1, 2, 3, 4]), k = pick(r, [2, 3]);
      return { q: `Blood flows at ${v} m/s through a vessel. The vessel narrows to 1/${k} of its original radius. Assuming steady incompressible flow, what is the speed in the narrow section?`,
        right: [`${v * k * k} m/s`, `A₁v₁ = A₂v₂ and A ∝ r², so v rises by ${k}² = ${k * k}: ${v * k * k} m/s.`],
        wrong: [[`${v * k} m/s`, "Scaled with radius; area goes with radius squared."], [`${f(v / (k * k))} m/s`, "Flow speeds up in a narrower tube, it doesn't slow down."], [`${v * k ** 4} m/s`, "The r⁴ dependence is Poiseuille's law for flow rate, not the continuity equation."]],
        note: "Continuity: Av = constant." }; } },
    { k: "pois", s: "CP", c: "4B", d: 2, build(r) {
      const k = pick(r, [2, 3]), dir = pick(r, ["halved", "increased"]), n = k ** 4;
      return dir === "halved"
        ? { q: `If a blood vessel's radius is halved while the pressure difference, length and viscosity stay the same, how does the flow rate change?`,
            right: ["It drops to 1/16", "Poiseuille: Q ∝ r⁴, and (½)⁴ = 1/16."],
            wrong: [["It drops to 1/2", "Flow depends on r⁴, not r."], ["It drops to 1/4", "That would be r², the area, not Poiseuille's r⁴."], ["It rises 4-fold", "Narrowing a vessel lowers flow at the same pressure."]],
            note: "Small radius changes have huge effects on flow (r⁴)." }
        : { q: `By what factor does flow through a tube change if its radius increases ${k}-fold with the same pressure difference, length and viscosity?`,
            right: [`${n}-fold increase`, `Q ∝ r⁴, so ${k}⁴ = ${n}.`],
            wrong: [[`${k}-fold increase`, "Flow goes with r⁴, not r."], [`${k * k}-fold increase`, "That is the area (r²) scaling."], [`${k ** 3}-fold increase`, "Used r³; Poiseuille's law is r⁴."]],
            note: "Poiseuille: Q = πr⁴ΔP / 8ηL." }; } },
    { k: "buoy", s: "CP", c: "4B", d: 2, build(r) {
      const rho = pick(r, [200, 400, 500, 600, 750, 800, 900]); const pct = rho / 10;
      return { q: `A block of density ${rho} kg/m³ floats in fresh water (1000 kg/m³). What fraction of its volume is submerged?`,
        right: [`${pct}%`, `Floating: fraction submerged = ρ_object/ρ_fluid = ${rho}/1000 = ${pct}%.`],
        wrong: [[`${100 - pct}%`, "That is the fraction above the water."], ["100%", "It floats, so it is not fully submerged."], [`${f(1000 / rho * 10)}%`, "Inverted the density ratio."]],
        note: "Floating objects displace their own weight of fluid." }; } },
    { k: "lens", s: "CP", c: "4D", d: 2, build(r) {
      const [fl, o] = pick(r, [[10, 20], [10, 15], [10, 30], [20, 40], [20, 30], [5, 10], [15, 30], [12, 24], [10, 5], [20, 10]]), i = 1 / (1 / fl - 1 / o);
      const real = i > 0;
      return { q: `An object sits ${o} cm in front of a converging lens with focal length ${fl} cm. Where is the image?`,
        right: [`${f(Math.abs(i))} cm, ${real ? "on the far side (real)" : "on the object's side (virtual)"}`, `1/f = 1/o + 1/i → 1/i = 1/${fl} − 1/${o}, so i = ${f(i)} cm${real ? "; positive means real" : "; negative means virtual"}.`],
        wrong: [[`${f(fl + o)} cm, on the far side (real)`, "Added f and o; use the thin lens equation."], [`${f(Math.abs(1 / (1 / fl + 1 / o)))} cm, on the far side (real)`, "Added 1/f and 1/o instead of subtracting."], [`${f(Math.abs(i))} cm, ${real ? "on the object's side (virtual)" : "on the far side (real)"}`, `Right distance, wrong side: ${real ? "a positive image distance is real" : "a negative image distance is virtual"}.`]],
        note: "Object inside the focal length of a converging lens gives a virtual, upright image." }; } },
    { k: "diop", s: "CP", c: "4D", d: 1, build(r) {
      const fcm = pick(r, [10, 20, 25, 50, 100, 200]), P = 100 / fcm;
      return { q: `A converging lens has a focal length of ${fcm} cm. What is its power?`,
        right: [`+${f(P)} D`, `P = 1/f in meters = 1/${f(fcm / 100)} m = +${f(P)} diopters.`],
        wrong: [[`+${fcm} D`, "Focal length must be in meters, not cm."], [`+${f(fcm / 100)} D`, "That is f in meters; power is its reciprocal."], [`−${f(P)} D`, "Converging lenses have positive power."]],
        note: "Diopters = 1 / focal length in meters." }; } },
    { k: "db", s: "CP", c: "4D", d: 2, build(r) {
      const n = pick(r, [1, 2, 3, 4]), dB = 10 * n;
      return { q: `A sound's intensity level rises by ${dB} dB. By what factor did its intensity increase?`,
        right: [`${10 ** n}`, `Each 10 dB is a 10× intensity increase, so ${dB} dB = 10^${n} = ${10 ** n}×.`],
        wrong: [[`${dB}`, "Decibels are logarithmic, not linear."], [`${n}`, "That is the number of 10 dB steps, not the factor."], [`${2 ** n}`, "Each 10 dB step multiplies intensity by 10, not 2."]],
        note: "β = 10 log(I/I₀): +10 dB = 10× intensity, +3 dB ≈ 2×." }; } },
    { k: "half", s: "CP", c: "4E", d: 1, build(r) {
      const th = pick(r, [2, 3, 5, 6, 8, 10]), n = int(r, 2, 5), m = pick(r, [64, 80, 96, 128, 160]); const left = m / 2 ** n;
      return { q: `A radioactive sample starts with ${m} mg of an isotope whose half-life is ${th} days. How much remains after ${th * n} days?`,
        right: [`${f(left)} mg`, `${th * n}/${th} = ${n} half-lives, so ${m}·(½)^${n} = ${f(left)} mg.`],
        wrong: [[`${f(m / (2 * n))} mg`, "Divided by 2n instead of 2ⁿ."], [`${f(m - left)} mg`, "That is the amount that decayed."], [`${f(m / 2 ** (n - 1))} mg`, "Counted one half-life too few."]],
        note: "After n half-lives, (½)ⁿ remains." }; } },
    { k: "photon", s: "CP", c: "4E", d: 2, build(r) {
      const lam = pick(r, [200, 300, 400, 500, 600]), E = 1240 / lam;
      return { q: `What is the energy of a photon with wavelength ${lam} nm? (hc ≈ 1240 eV·nm)`,
        right: [`${f(E)} eV`, `E = hc/λ = 1240/${lam} = ${f(E)} eV.`],
        wrong: [[`${f(lam / 1240)} eV`, "Inverted the formula; E = hc/λ."], [`${f(1240 * lam / 1000)} eV`, "Energy falls as wavelength rises, it doesn't grow with it."], [`${f(E * 2)} eV`, "Doubled the result."]],
        note: "Shorter wavelength means higher photon energy." }; } },
    { k: "pha", s: "CP", c: "5A", d: 1, build(r) {
      const n = int(r, 1, 5), base = pick(r, ["HCl", "HNO₃", "HBr"]);
      return { q: `What is the pH of a 1 × 10⁻${n} M solution of ${base} at 25 °C?`,
        right: [`${n}`, `${base} is a strong acid, so [H⁺] = 10⁻${n} M and pH = −log[H⁺] = ${n}.`],
        wrong: [[`${14 - n}`, "That is the pOH, not the pH."], [`−${n}`, "pH = −log[H⁺], which is positive here."], [`${n + 1}`, "Strong acids dissociate fully: [H⁺] equals the acid concentration."]],
        note: "Strong acid: pH = −log[acid]." }; } },
    { k: "phb", s: "CP", c: "5A", d: 2, build(r) {
      const n = int(r, 1, 4);
      return { q: `What is the pH of a 1 × 10⁻${n} M NaOH solution at 25 °C?`,
        right: [`${14 - n}`, `[OH⁻] = 10⁻${n} M → pOH = ${n} → pH = 14 − ${n} = ${14 - n}.`],
        wrong: [[`${n}`, "That is the pOH; subtract from 14."], [`${14 + n}`, "pH + pOH = 14, so subtract."], [`${7 + n}`, "Neutral is 7, but pH comes from 14 − pOH."]],
        note: "pH + pOH = 14 at 25 °C." }; } },
    { k: "hh", s: "CP", c: "5A", d: 2, build(r) {
      const pKa = pick(r, [3.8, 4.2, 4.8, 6.1, 6.8, 7.2, 9.2]), [ratio, lg, txt] = pick(r, [[10, 1, "10:1"], [0.1, -1, "1:10"], [1, 0, "1:1"], [100, 2, "100:1"]]);
      const pH = +(pKa + lg).toFixed(1);
      return { q: `A buffer has pKa = ${pKa} and a [A⁻]:[HA] ratio of ${txt}. What is its pH?`,
        right: [`${pH}`, `Henderson-Hasselbalch: pH = pKa + log([A⁻]/[HA]) = ${pKa} + (${lg}) = ${pH}.`],
        wrong: [[`${+(pKa - lg).toFixed(1)}`, "Flipped the ratio; it's [A⁻]/[HA]."], [`${+(pKa + ratio).toFixed(1)}`, "Added the ratio itself instead of its log."], [`${+(14 - pH).toFixed(1)}`, "That would be the pOH."]].filter(w => w[0] !== String(pH)).concat([[`${+(pKa + lg + 0.5).toFixed(1)}`, "Rounding slip: log(10) = 1 exactly."]]).slice(0, 3),
        note: "When [A⁻] = [HA], pH = pKa." }; } },
    { k: "dil", s: "CP", c: "5A", d: 1, build(r) {
      const M1 = pick(r, [1, 2, 3, 6, 12]), V1 = pick(r, [10, 20, 25, 50]), V2 = V1 * pick(r, [2, 4, 5, 10]), M2 = M1 * V1 / V2;
      return { q: `${V1} mL of ${M1} M HCl is diluted with water to a final volume of ${V2} mL. What is the new concentration?`,
        right: [`${f(M2)} M`, `M₁V₁ = M₂V₂ → M₂ = ${M1}·${V1}/${V2} = ${f(M2)} M.`],
        wrong: [[`${f(M1 * V2 / V1)} M`, "Inverted the volume ratio; dilution lowers concentration."], [`${f(M1 * V1 / (V2 + V1))} M`, `${V2} mL is already the final volume; don't add the ${V1} mL again.`], [`${M1} M`, "Adding water changes concentration."]],
        note: "Moles are conserved in a dilution: M₁V₁ = M₂V₂." }; } },
    { k: "fp", s: "CP", c: "5A", d: 2, build(r) {
      const [salt, i] = pick(r, [["NaCl", 2], ["CaCl₂", 3], ["glucose", 1], ["KBr", 2], ["MgCl₂", 3]]), m = pick(r, [0.5, 1, 2]), dT = 1.86 * i * m;
      return { q: `What is the freezing point depression of a ${m} m aqueous ${salt} solution? (K_f for water = 1.86 °C/m; assume complete dissociation)`,
        right: [`${f(dT)} °C`, `ΔT = i·K_f·m = ${i}·1.86·${m} = ${f(dT)} °C (i = ${i} for ${salt}).`],
        wrong: [i === 1 ? [`${f(1.86 * m * 2)} °C`, "Glucose doesn't dissociate, so i = 1."] : [`${f(1.86 * m)} °C`, `Forgot the van 't Hoff factor (i = ${i}).`],
          [`${f(1.86 * (i + 1) * m)} °C`, "Overcounted the ions; use i particles per formula unit."], [`${f(1.86 * i / m)} °C`, "Divided by molality instead of multiplying."]],
        note: "Colligative properties depend on the number of dissolved particles." }; } },
    { k: "gibbs", s: "CP", c: "5E", d: 2, build(r) {
      const H = pick(r, [-80, -40, 40, 60, 90]), S = pick(r, [-200, -100, 100, 150, 200]), T = pick(r, [200, 300, 400, 500]);
      const G = H - T * S / 1000;
      const sp = G < 0 ? "spontaneous" : "nonspontaneous";
      return { q: `For a reaction, ΔH = ${H} kJ/mol and ΔS = ${S} J/(mol·K). What is ΔG at ${T} K, and is the reaction spontaneous?`,
        right: [`${f(G)} kJ/mol, ${sp}`, `ΔG = ΔH − TΔS = ${H} − ${T}(${S / 1000}) = ${f(G)} kJ/mol; ${G < 0 ? "negative" : "positive"} means ${sp}.`],
        wrong: [[`${f(H - T * S)} kJ/mol, ${H - T * S < 0 ? "spontaneous" : "nonspontaneous"}`, "Forgot to convert ΔS from J to kJ."], [`${f(H + T * S / 1000)} kJ/mol, ${H + T * S / 1000 < 0 ? "spontaneous" : "nonspontaneous"}`, "Sign error: ΔG = ΔH − TΔS."], [`${f(G)} kJ/mol, ${G < 0 ? "nonspontaneous" : "spontaneous"}`, "Right number, wrong conclusion: negative ΔG is spontaneous."]],
        note: "Convert ΔS to kJ before combining with ΔH." }; } },
    { k: "rate", s: "CP", c: "5E", d: 2, build(r) {
      const n = pick(r, [0, 1, 2]), k = pick(r, [2, 3]);
      const fac = k ** n;
      return { q: `When [A] is multiplied by ${k} (all else constant), the initial rate is multiplied by ${fac}. What is the reaction order in A?`,
        right: [`${["Zero", "First", "Second"][n]} order`, `Rate ∝ [A]ⁿ: ${k}ⁿ = ${fac}, so n = ${n}.`],
        wrong: [0, 1, 2, 3].filter(x => x !== n).slice(0, 3).map(x => [`${["Zero", "First", "Second", "Third"][x]} order`, `That would make the rate change by ${k}^${x} = ${k ** x}.`]),
        note: "Order = log(rate factor) / log(concentration factor)." }; } },
    { k: "hw", s: "BB", c: "1C", d: 2, build(r) {
      const q = pick(r, [0.1, 0.2, 0.3, 0.4]), p = +(1 - q).toFixed(1), q2 = +(q * q).toFixed(2), c = +(2 * p * q).toFixed(2);
      return { q: `In a population in Hardy-Weinberg equilibrium, ${f(q2 * 100)}% of individuals show a recessive trait. What percentage are heterozygous carriers?`,
        right: [`${f(c * 100)}%`, `q² = ${q2} → q = ${q}, p = ${p}; carriers = 2pq = 2·${p}·${q} = ${f(c * 100)}%.`],
        wrong: [[`${f(q * 100)}%`, "That is q, the recessive allele frequency."], [`${f(p * q * 100)}%`, "Forgot the 2 in 2pq."], [`${f(p * p * 100)}%`, "That is p², the homozygous dominant frequency."]],
        note: "Start from q² (the recessive phenotype), take the square root, then use p + q = 1." }; } },
    { k: "cross", s: "BB", c: "1C", d: 2, build(r) {
      const cases = [
        ["Aa × Aa", "show the dominant phenotype", "3/4", [["1/2", "That is the heterozygote fraction."], ["1/4", "That is the recessive fraction."], ["1", "aa offspring are possible."]], "AA + 2 Aa out of 4."],
        ["Aa × aa", "show the recessive phenotype", "1/2", [["1/4", "That is for Aa × Aa."], ["3/4", "That is the dominant fraction in Aa × Aa."], ["0", "Aa × aa gives aa half the time."]], "Aa × aa gives Aa : aa = 1 : 1."],
        ["AaBb × AaBb", "show both recessive traits", "1/16", [["1/4", "That is one trait alone."], ["9/16", "That is both dominant."], ["3/16", "That is one dominant, one recessive."]], "(1/4)(1/4) = 1/16 with independent assortment."],
        ["AaBb × AaBb", "show both dominant traits", "9/16", [["3/4", "That is one trait alone."], ["1/16", "That is both recessive."], ["3/16", "That is one specific mixed class."]], "(3/4)(3/4) = 9/16."],
        ["AaBb × aabb", "show both recessive traits", "1/4", [["1/16", "That is for AaBb × AaBb."], ["1/2", "That is one trait alone."], ["9/16", "That is the dihybrid both-dominant fraction."]], "(1/2)(1/2) = 1/4: a test cross."],
        ["AaBbCc × AaBbCc", "be homozygous recessive for all three genes", "1/64", [["1/8", "That is (1/2)³; each gene gives 1/4 here."], ["3/64", "Multiply 1/4 three times."], ["1/16", "That covers only two genes."]], "(1/4)³ = 1/64."]
      ];
      const [cr, what, ans, wr, why] = pick(r, cases);
      return { q: `In the cross ${cr}, with complete dominance and unlinked genes, what fraction of offspring will ${what}?`,
        right: [ans, `Correct: ${why}`], wrong: wr, note: "Multiply probabilities for independent genes." }; } },
    { k: "mm", s: "BB", c: "1A", d: 2, build(r) {
      const n = pick(r, [1, 3, 4, 9]), V = pick(r, [60, 80, 100, 120]), v = V * n / (n + 1);
      return { q: `An enzyme follows Michaelis-Menten kinetics with Vmax = ${V} μmol/min. What is the reaction rate when [S] = ${n === 1 ? "Km" : n + "Km"}?`,
        right: [`${f(v)} μmol/min`, `v = Vmax[S]/(Km + [S]) = ${V}·${n}/(1 + ${n}) = ${f(v)} μmol/min.`],
        wrong: [[`${f(V / 2)} μmol/min`, "Vmax/2 only happens at [S] = Km."],
          [`${V} μmol/min`, "Vmax is only approached at very high [S]."], [`${f(V * n / (n + 2))} μmol/min`, "Denominator should be Km + [S]."]].filter(w => w[0] !== `${f(v)} μmol/min`).concat([[`${f(V / (n + 1))} μmol/min`, "Inverted the fraction."]]).slice(0, 3),
        note: "At [S] = Km, v = Vmax/2." }; } },
    { k: "pep", s: "BB", c: "1B", d: 1, build(r) {
      const n = int(r, 20, 120);
      return { q: `An mRNA open reading frame is ${3 * n + 3} nucleotides long, from the start codon through the stop codon. How many amino acids does the encoded peptide have?`,
        right: [`${n}`, `${3 * n + 3}/3 = ${n + 1} codons, and the stop codon adds no amino acid: ${n}.`],
        wrong: [[`${n + 1}`, "The stop codon does not code for an amino acid."], [`${3 * n + 3}`, "Each amino acid needs a 3-nucleotide codon."], [`${n - 1}`, "The start codon (AUG, Met) does add an amino acid."]],
        note: "Codons = nucleotides/3; subtract one for the stop codon." }; } },
    { k: "sens", s: "PS", c: "SK", d: 2, build(r) {
      const tp = pick(r, [45, 72, 80, 90]), fn = pick(r, [5, 8, 10, 20]), tn = pick(r, [150, 180, 270]), fp = pick(r, [30, 20, 50]);
      const se = tp / (tp + fn) * 100, sp = tn / (tn + fp) * 100;
      const ask = pick(r, ["sensitivity", "specificity"]); const v = ask === "sensitivity" ? se : sp;
      return { q: `A screening test is given to ${tp + fn + tn + fp} people. Of those with the disease, ${tp} test positive and ${fn} test negative. Of those without it, ${tn} test negative and ${fp} test positive. What is the test's ${ask}?`,
        right: [`${f(v)}%`, ask === "sensitivity" ? `Sensitivity = TP/(TP + FN) = ${tp}/${tp + fn} = ${f(se)}%.` : `Specificity = TN/(TN + FP) = ${tn}/${tn + fp} = ${f(sp)}%.`],
        wrong: [[`${f(ask === "sensitivity" ? sp : se)}%`, `That is the ${ask === "sensitivity" ? "specificity" : "sensitivity"}.`], [`${f(tp / (tp + fp) * 100)}%`, "That is the positive predictive value."], [`${f(tn / (tn + fn) * 100)}%`, "That is the negative predictive value."]],
        note: "SeNsitivity rules OUT (few false negatives); SPecificity rules IN (few false positives)." }; } },
    { k: "stats", s: "PS", c: "SK", d: 1, build(r) {
      const base = Array.from({ length: 5 }, () => int(r, 2, 9));
      const mid = [...base.slice(0, 4)].sort((a, b) => a - b)[2], others = base.slice(0, 4).reduce((a, b) => a + b);
      base[4] = Math.max(int(r, 20, 40), 5 * mid - others + 3); // big enough that the mean clearly exceeds the median
      const sorted = [...base].sort((a, b) => a - b), mean = base.reduce((a, b) => a + b) / 5, med = sorted[2];
      return { q: `Five participants report ${base.join(", ")} hours of sleep debt. Which statement is true?`,
        right: [`The mean (${f(mean)}) is greater than the median (${med})`, `The outlier ${base[4]} pulls the mean up; the median is the middle value ${med}.`],
        wrong: [[`The median (${med}) is greater than the mean (${f(mean)})`, "A high outlier makes the mean larger, not smaller."], [`The mean and median are equal`, "They differ because of the outlier."], [`The mode is ${base[4]}`, `${base[4]} appears only once.`]],
        note: "Skewed data: the mean chases the tail; the median resists outliers." }; } }
  ];

  function make(k, seed) {
    const t = T.find(x => x.k === k); if (!t) return null;
    for (let tries = 0; tries < 6; tries++) {
      const r = rng(seed * 7919 + tries * 104729 + k.length), b = t.build(r);
      const opts = [b.right, ...b.wrong.slice(0, 3)];
      if (new Set(opts.map(o => o[0])).size !== 4) continue;
      const order = [0, 1, 2, 3].sort(() => r() - .5);
      return { id: `g_${k}_${seed}`, s: t.s, c: t.c, d: t.d, q: b.q, o: order.map(i => opts[i]), a: order.indexOf(0), note: b.note || "", gen: true };
    }
    return null;
  }
  // Build a fresh question for a section ("ALL", "CP", "BB", "PS") or one category, or null if none fit.
  function fresh(sec, cat) {
    const pool = T.filter(t => (!cat || t.c === cat) && (sec === "ALL" || t.s === sec));
    if (!pool.length) return null;
    for (let i = 0; i < 5; i++) { const t = pool[Math.floor(Math.random() * pool.length)], q = make(t.k, Math.floor(Math.random() * 1e9)); if (q) return q; }
    return null;
  }
  function fromId(id) { const m = /^g_([a-z]+)_(\d+)$/.exec(id); return m ? make(m[1], +m[2]) : null; }
  window.GEN = { fresh, fromId, templates: T.map(t => ({ k: t.k, s: t.s, c: t.c })) };
})();
