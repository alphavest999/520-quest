/* 520 Quest music: an original fighting-game style track composed and synthesized live with Web Audio.
   No samples or recordings are used. MUSIC.play("battle" | "feed"), MUSIC.stop(). */
(function () {
  let ctx = null, master = null, comp = null, noise = null, timer = null, mode = null, step = 0, nextT = 0, bar = 0;
  const BPM = { battle: 148, feed: 112 }, LOOK = 0.12;
  const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
  // D minor. Progression per bar (root MIDI notes): Dm, Bb, C, A (battle) / Dm, F, C, Bb (feed)
  const PROG = { battle: [38, 34, 36, 33], feed: [38, 41, 36, 34] };
  const CHORD = { 38: [0, 3, 7], 34: [0, 4, 7], 36: [0, 4, 7], 33: [0, 4, 7], 41: [0, 4, 7] };
  // 16-step bass rhythm: 1 = root, 2 = octave, 3 = fifth, 0 = rest
  const BASS = [1, 0, 1, 2, 1, 0, 1, 3, 1, 0, 1, 2, 3, 0, 2, 1];
  // Lead motif in scale degrees over two bars (null = rest), original to this app.
  const SCALE = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15];
  const LEAD = [[7, null, 4, 5, 7, null, 9, 7, 5, null, 4, null, 3, 4, 5, null], [7, null, 4, 5, 7, null, 9, 10, 9, null, 7, null, 5, 4, 3, null]];
  const ARP = [0, 1, 2, 1, 0, 2, 1, 2];

  function init() {
    if (ctx) return true;
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      comp = ctx.createDynamicsCompressor(); comp.threshold.value = -18; comp.ratio.value = 4;
      master = ctx.createGain(); master.gain.value = 0;
      master.connect(comp).connect(ctx.destination);
      const len = ctx.sampleRate; noise = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = noise.getChannelData(0); for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      return true;
    } catch (e) { return false; }
  }
  function env(g, t, a, peak, dec) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + dec); }
  function tone(type, freq, t, dur, vol, cutoff) {
    const o = ctx.createOscillator(), g = ctx.createGain(), f = ctx.createBiquadFilter();
    o.type = type; o.frequency.value = freq; f.type = "lowpass"; f.frequency.value = cutoff || 2400; f.Q.value = 6;
    env(g, t, 0.005, vol, dur); o.connect(f).connect(g).connect(master); o.start(t); o.stop(t + dur + 0.05);
  }
  function kick(t, vol) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.12);
    env(g, t, 0.002, vol, 0.22); o.connect(g).connect(master); o.start(t); o.stop(t + 0.3);
  }
  function hit(t, vol, hp, dur) {
    const s = ctx.createBufferSource(), g = ctx.createGain(), f = ctx.createBiquadFilter();
    s.buffer = noise; f.type = hp ? "highpass" : "bandpass"; f.frequency.value = hp ? 7000 : 1800;
    env(g, t, 0.001, vol, dur); s.connect(f).connect(g).connect(master); s.start(t); s.stop(t + dur + 0.05);
  }
  function play16(t, s) {
    const full = mode === "battle", root = PROG[mode][bar % 4], ch = CHORD[root], sp = 60 / BPM[mode] / 4;
    // drums
    if (s % 4 === 0) kick(t, full ? 0.9 : 0.6);
    if (full && (s === 10 || s === 14)) kick(t, 0.5);
    if (s === 4 || s === 12) { hit(t, full ? 0.45 : 0.25, false, 0.16); }
    if (full ? true : s % 2 === 0) hit(t, s % 4 === 2 ? 0.14 : 0.07, true, 0.04);
    // bass
    const b = BASS[s];
    if (b && (full || s % 2 === 0)) tone("sawtooth", mtof(root + (b === 2 ? 12 : b === 3 ? 7 : 0)), t, sp * 0.9, full ? 0.32 : 0.22, full ? 900 : 600);
    // arpeggio pad
    if (s % 2 === 0) { const n = root + 24 + ch[ARP[(s / 2) % 8]]; tone("square", mtof(n), t, sp * 1.6, full ? 0.06 : 0.05, 2200); }
    // lead (battle only)
    if (full && bar % 8 >= 4) {
      const deg = LEAD[(bar % 8 >= 6) ? 1 : 0][s];
      if (deg !== null) tone("sawtooth", mtof(62 + SCALE[deg % SCALE.length] + (deg >= SCALE.length ? 12 : 0)), t, sp * 1.8, 0.09, 3200);
    }
    // crash at the top of every 8 bars
    if (full && s === 0 && bar % 8 === 0) hit(t, 0.25, true, 0.9);
  }
  function tick() {
    const sp = 60 / BPM[mode] / 4;
    while (nextT < ctx.currentTime + LOOK) {
      play16(nextT, step); nextT += sp; step = (step + 1) % 16; if (step === 0) bar++;
    }
  }
  function play(m, vol) {
    if (!init()) return;
    if (ctx.state === "suspended") ctx.resume();
    const v = vol != null ? vol : (m === "battle" ? 0.55 : 0.28);
    if (mode === m && timer) { master.gain.setTargetAtTime(v, ctx.currentTime, 0.3); return; }
    if (timer) clearInterval(timer);
    mode = m; step = 0; bar = 0; nextT = ctx.currentTime + 0.08;
    master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setTargetAtTime(v, ctx.currentTime, 0.4);
    timer = setInterval(tick, 25); tick();
  }
  function stop() {
    if (!ctx || !timer) return;
    master.gain.setTargetAtTime(0.0001, ctx.currentTime, 0.25);
    clearInterval(timer); timer = null; mode = null; // already-scheduled notes fade out with the master gain
  }
  // Level-up fanfare: an original rising D-major figure over a held chord, about four seconds long.
  function fanfare() {
    if (!init()) return;
    if (ctx.state === "suspended") ctx.resume();
    const t0 = ctx.currentTime + 0.05, was = master.gain.value;
    master.gain.cancelScheduledValues(t0); master.gain.setValueAtTime(0.6, t0);
    const beat = 0.14, run = [62, 66, 69, 74, 69, 74, 78, 81];
    run.forEach((m, i) => { tone("square", mtof(m), t0 + i * beat, beat * 0.9, 0.09, 3400); tone("sawtooth", mtof(m - 12), t0 + i * beat, beat * 0.9, 0.05, 1800); });
    const hold = t0 + run.length * beat + 0.05;
    [74, 78, 81, 86].forEach(m => tone("sawtooth", mtof(m), hold, 1.6, 0.07, 2600));
    [50, 62].forEach(m => tone("square", mtof(m), hold, 1.6, 0.08, 900));
    [0, 2, 4, 6].forEach(i => kick(t0 + i * beat * 2, 0.7));
    kick(hold, 0.9); hit(hold, 0.3, true, 1.2);
    if (timer) master.gain.setTargetAtTime(was || 0.3, hold + 1.8, 0.3); else master.gain.setTargetAtTime(0.0001, hold + 1.8, 0.3);
  }
  document.addEventListener("visibilitychange", () => { if (!ctx) return; if (document.hidden) ctx.suspend(); else if (timer) ctx.resume(); });
  window.MUSIC = { play, stop, fanfare, get playing() { return mode; } };
})();
