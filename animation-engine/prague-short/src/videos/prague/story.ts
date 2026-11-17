// Prague 1618 short — timeline, camera, DOF.
// 10-second test clip (300 frames @ 30 fps).
// Shot 1 (0-149): wide 3/4 front — THURN approaches the castle gate across the courtyard.
// Shot 2 (150-299): medium side-track — camera glides alongside THURN as he nears the gate.
export const FPS = 30;
export const TOTAL = 300;
export const D0 = 0; // ground y (was bridge deck height in the bridge template)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };

// THURN walks from z = 18 to z = 1 over 300 frames (1.7 m/s, brisk walk toward the gate).
export const THURN_Z = (f: number) => 18 - f * (17 / 299);
export const marchPhase = (t: number) => ((t % 1) + 1) % 1; // t in seconds

export type Light = "day";
export type ShotDef = { id: number; a: number; b: number; light: Light };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 150, light: "day" },
  { id: 2, a: 150, b: 300, light: "day" },
];

export const XFADE: Record<number, number> = { 2: 12 };
export const FLASH_AT = 9999; // no end-hook flash

export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2)
      return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

// Camera grammar: slow symmetric smootherstep push-ins; no hand-held float.
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
const full = (p: V3, l: V3, fov = 40, roll = 0): Cam => ({ pos: p, look: l, fov, roll });

// Shot 1 — wide 3/4 front: camera ahead-right of THURN, gate arch fills background.
// Very slow push-in (k shrinks camera-to-look distance by 6 % over 150 f).
const S1 = (f: number): Cam => {
  const tz = THURN_Z(f);
  const k = 1 - glide(Math.min(1, f / 149)) * 0.06;
  return full([7.5 * k, 2.6, tz + 10], [0, 1.6, tz], 42);
};

// Shot 2 — medium side-track: camera to THURN's right, tracking forward.
// Slight negative roll for forward-momentum feel.
const S2 = (f: number): Cam => {
  const tz = THURN_Z(f);
  const k = 1 - glide(Math.min(1, (f - 150) / 149)) * 0.07;
  return full([5.5 * k, 1.9, tz + 3], [0, 1.65, tz - 1], 38, -0.015);
};

const CAMS: Record<number, (f: number) => Cam> = { 1: S1, 2: S2 };
export const camAt = (id: number, f: number): Cam => (CAMS[id] ?? S1)(f);
export const kickAt = (_t: number) => 0;
export const keyEnd = (_id: number, f: number) => f;

// DOF: shot 1 all sharp; shot 2 mild DOF focused on THURN.
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 0 },
  { f: 150, dur: 15, cInf: 10, focus: (f) => [0, 1.6, THURN_Z(f)] as V3 },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export const focusAt = (id: number, f: number): V3 => {
  const d = dofAt(f); return d.focus ? d.focus(f) : camAt(id, f).look;
};

export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
