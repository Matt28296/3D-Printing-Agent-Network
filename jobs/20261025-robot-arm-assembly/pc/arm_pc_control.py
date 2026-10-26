#!/usr/bin/env python3
"""Drive the desktop robot arm from a PC and watch the claw through the Brio 4K.

The Brio plugs into the PC (USB), not the ESP32: the ESP32 has no USB host. The ESP32 runs
arm_test.ino and takes simple serial commands; this script is a starting point for your own
vision code (OpenCV), not a finished pick-and-place program.

Angles are joint angles in the CAD's convention (assembly_check.py), the same as the sketch's:
  base -90..90 (0 = the arm along +X), shoulder 0..180 (90 = upright), elbow -150..30 (0 = in line,
  - = folded down), wrist -90..90 (0 = in line, - = fingertips down), claw opening 0..44 mm.
Positions are mm from the yaw axis on the base's top plate: +X out over the ESP32's USB wall, Z up
(the desk is at Z = -40).

Install:  pip install pyserial opencv-python
Examples:
  python arm_pc_control.py --port COM5 status              # Windows; /dev/ttyUSB0 on Linux, /dev/cu.* on macOS
  python arm_pc_control.py --port COM5 move 0 60 -90 -50 20
  python arm_pc_control.py --port COM5 approach 160 80 -25 --open 30   # fingertips to (x, y, z), claw pointing down
  python arm_pc_control.py --port COM5 grip 20             # hold an object 20 mm wide
  python arm_pc_control.py --port COM5 park                # upright: the shoulder holds about nothing
  python arm_pc_control.py --port COM5 preview --object-mm 20 --focus 200
                                                           # live view: o open, c grip, [ ] wrist, p park, q quit

Keep one connection open for a whole session (the preview, or one Arm object in your own code)
rather than starting this script once per move: on some PCs and drivers opening the port still
resets the ESP32. The sketch then restarts where the arm stopped, but each reset costs about 2 s.

The camera sits on the claw's side, turned 90° to the arm: with the claw level, world "up"
appears at the right edge of the raw image. --rotate (default ccw) turns the preview upright.
The claw's own cover fills the bottom 40 % of the raw image: crop_claw() cuts it off for vision code.
"""
from __future__ import annotations

import argparse
import math
import sys
import time

READY = "arm_test ready"

# ---- Geometry (mm), as assembly_check.py places the CAD parts (claw v2, MG90S heights of 2026-10-26) ----------
SHOULDER_X, SHOULDER_Z = 10.15, 60.5    # shoulder axis: along the arm from the yaw axis; above the base top plate
UPPER_L, FORE_L = 100.0, 90.0           # shoulder -> elbow, elbow -> wrist
TIP_L = 76.35                           # wrist axis -> the point between the fingertips (claw_frame.X_TIP - 3)
TIP_Y = 79.1                            # the fingertips sit this far to the side of the yaw axis (+Y at yaw 0)
DESK_Z = -40.0                          # desk top, relative to the base top plate
LIMITS = ((-90.0, 90.0), (0.0, 180.0), (-150.0, 30.0), (-90.0, 90.0), (0.0, 44.0))   # as arm_test.ino
CAMERA_ABOVE_MM = 10.0                  # approach moves keep the Brio's lowest corner this far above the fingertips
CLAW_ROWS = 0.40                        # the claw's cover fills this share of the raw image, at its bottom

# The sketch's guard, line for line (arm_test.ino, "Guard"): every moving part as a box in its link's frame,
# (link, x0, x1, y0, y1, Y0, Y1, kind). It plans moves the sketch will accept; the sketch still checks them.
GUARD_CLEAR = 8.0
BASE_HX, BASE_HY, DRUM_R, DRUM_TOP = 55.0, 52.0, 48.0, 24.5
PARTS = (
    (1, -25.0, 121.0, -17.0, 17.0, -7.5, 35.4, 0),      # upper link and the elbow MG996R
    (2, -25.0, 104.0, -13.0, 13.0, 34.0, 44.0, 0),      # forearm
    (2, 68.4, 100.6, -6.1, 6.1, 25.5, 58.0, 0),         # wrist MG90S
    (3, -8.5, 33.85, -32.0, 32.0, 56.6, 98.6, 0),       # claw frame, cover, pinion and claw MG90S
    (3, -26.55, 14.0, -28.0, 22.0, 98.6, 122.7, 0),     # camera mount
    (3, -21.69, 15.19, -51.0, 51.0, 102.35, 139.23, 1),  # Brio 4K
    (3, 22.6, 30.6, 0.0, 0.0, 62.85, 95.35, 2),         # racks
    (3, 30.6, 42.35, 0.0, 0.0, 62.85, 95.35, 3),        # necks
    (3, 42.35, 79.35, 0.0, 0.0, 62.85, 95.35, 4),       # finger blades
)


def _part_y(kind: int, y0: float, y1: float, half_gap: float) -> tuple[float, float]:
    if kind == 2:
        h = max(28.27 - half_gap, 15.71 + half_gap)
    elif kind == 3:
        h = 14.0 + half_gap
    elif kind == 4:
        h = 6.0 + half_gap
    else:
        return y0, y1
    return -h, h


def _sat_gap(cx, cz, ux, uz, hx, hy, bx0, bx1, bz0, bz1) -> float:
    vx, vz = uz, -ux
    bcx, bcz, bhx, bhz = (bx0 + bx1) / 2, (bz0 + bz1) / 2, (bx1 - bx0) / 2, (bz1 - bz0) / 2
    best = -1e9
    for nx, nz in ((1.0, 0.0), (0.0, 1.0), (ux, uz), (vx, vz)):
        d = (abs((cx - bcx) * nx + (cz - bcz) * nz) - hx * abs(ux * nx + uz * nz) - hy * abs(vx * nx + vz * nz)
             - bhx * abs(nx) - bhz * abs(nz))
        best = max(best, d)
    return best


def _base_span(yaw: float, Y0: float, Y1: float) -> tuple[float, float] | None:
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    A, B = BASE_HX + GUARD_CLEAR, BASE_HY + GUARD_CLEAR
    poly = [(X * c + Yw * s, -X * s + Yw * c) for X, Yw in ((A, B), (-A, B), (-A, -B), (A, -B))]
    for lim, above in ((Y0, True), (Y1, False)):
        out = []
        for i, p in enumerate(poly):
            q = poly[(i + 1) % len(poly)]
            pin, qin = (p[1] >= lim, q[1] >= lim) if above else (p[1] <= lim, q[1] <= lim)
            if pin:
                out.append(p)
            if pin != qin:
                t = (lim - p[1]) / (q[1] - p[1])
                out.append((p[0] + t * (q[0] - p[0]), lim))
        poly = out
        if not poly:
            return None
    xs = [p[0] for p in poly]
    return min(xs), max(xs)


def guard_margins(q, camera: bool = True) -> tuple[float, float]:
    """(desk, base) margins of pose q = (base, shoulder, elbow, wrist, claw_mm): mm beyond the sketch's 8 mm
    clearance; below 0 the sketch refuses to go there (or further in)."""
    yaw, sh, el, wr, gap = q
    ang = {1: sh, 2: sh + el, 3: sh + el + wr}
    ox = {1: SHOULDER_X}
    oz = {1: SHOULDER_Z}
    ox[2] = ox[1] + UPPER_L * math.cos(math.radians(ang[1]))
    oz[2] = oz[1] + UPPER_L * math.sin(math.radians(ang[1]))
    ox[3] = ox[2] + FORE_L * math.cos(math.radians(ang[2]))
    oz[3] = oz[2] + FORE_L * math.sin(math.radians(ang[2]))
    d = min(max(gap, 0.0), 44.0) / 2
    desk = base = 1e9
    for link, x0, x1, y0, y1, Y0, Y1, kind in PARTS:
        if kind == 1 and not camera:
            continue
        y0, y1 = _part_y(kind, y0, y1, d)
        s, c = math.sin(math.radians(ang[link])), math.cos(math.radians(ang[link]))
        desk = min(desk, oz[link] + min(x0 * s, x1 * s) + min(-y0 * c, -y1 * c) - (DESK_Z + GUARD_CLEAR))
        if link == 1:
            continue
        hx, hy, mx, my = (x1 - x0) / 2, (y1 - y0) / 2, (x0 + x1) / 2, (y0 + y1) / 2
        cx, cz = ox[link] + mx * c + my * s, oz[link] + mx * s - my * c
        r = DRUM_R + GUARD_CLEAR
        if Y0 < r:
            xh = math.sqrt(r * r - Y0 * Y0)
            base = min(base, _sat_gap(cx, cz, c, s, hx, hy, -xh, xh, DESK_Z, DRUM_TOP + GUARD_CLEAR))
        span = _base_span(yaw, Y0, Y1)
        if span:
            base = min(base, _sat_gap(cx, cz, c, s, hx, hy, span[0], span[1], DESK_Z, GUARD_CLEAR))
    return desk, base


def fingertip(q) -> tuple[float, float, float]:
    """Point between the fingertips, (x, y, z) mm, for pose q = (base, shoulder, elbow, wrist[, claw])."""
    yaw, sh, el, wr = q[:4]
    a1, a2, a3 = math.radians(sh), math.radians(sh + el), math.radians(sh + el + wr)
    xp = SHOULDER_X + UPPER_L * math.cos(a1) + FORE_L * math.cos(a2) + TIP_L * math.cos(a3)
    z = SHOULDER_Z + UPPER_L * math.sin(a1) + FORE_L * math.sin(a2) + TIP_L * math.sin(a3)
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return xp * c - TIP_Y * s, xp * s + TIP_Y * c, z


def ik(x: float, y: float, z: float, pitch: float = -90.0) -> tuple[float, float, float, float]:
    """(base, shoulder, elbow, wrist) that put the fingertips at (x, y, z) with the claw at `pitch` degrees
    (-90 = pointing straight down). The elbow bends down, as its window does. ValueError if out of reach or
    outside the joint limits."""
    r2 = x * x + y * y
    if r2 <= TIP_Y * TIP_Y:
        raise ValueError(f"({x:.0f}, {y:.0f}) is within {TIP_Y} mm of the yaw axis")
    xp = math.sqrt(r2 - TIP_Y * TIP_Y)
    yaw = math.degrees(math.atan2(y, x) - math.atan2(TIP_Y, xp))
    yaw = (yaw + 180.0) % 360.0 - 180.0
    a3 = math.radians(pitch)
    wx, wz = xp - TIP_L * math.cos(a3) - SHOULDER_X, z - TIP_L * math.sin(a3) - SHOULDER_Z
    c2 = (wx * wx + wz * wz - UPPER_L ** 2 - FORE_L ** 2) / (2 * UPPER_L * FORE_L)
    if not -1.0 <= c2 <= 1.0:
        raise ValueError(f"({x:.0f}, {y:.0f}, {z:.0f}) is out of reach at pitch {pitch:.0f}")
    el = -math.acos(c2)
    sh = math.atan2(wz, wx) - math.atan2(FORE_L * math.sin(el), UPPER_L + FORE_L * math.cos(el))
    q = (yaw, math.degrees(sh), math.degrees(el), pitch - math.degrees(sh) - math.degrees(el))
    for v, (lo, hi), name in zip(q, LIMITS, ("base", "shoulder", "elbow", "wrist")):
        if not lo - 1e-6 <= v <= hi + 1e-6:
            raise ValueError(f"({x:.0f}, {y:.0f}, {z:.0f}) at pitch {pitch:.0f} needs {name} {v:.1f}, outside {lo:.0f}..{hi:.0f}")
    return q


def camera_above_tips(q, gap: float = 0.0) -> float:
    """How far (mm) the Brio's lowest corner sits above the fingertips' lowest corner in pose q; < 0 = below.
    It depends only on the claw's pitch (shoulder + elbow + wrist) and the opening."""
    a = math.radians(q[1] + q[2] + q[3])
    s, c = math.sin(a), math.cos(a)

    def low(x0, x1, y0, y1):
        return min(x0 * s, x1 * s) + min(-y0 * c, -y1 * c)
    return low(-21.69, 15.19, -51.0, 51.0) - low(42.35, 79.35, -(6.0 + gap / 2), 6.0 + gap / 2)


def plan_approach(x: float, y: float, z: float, gap: float, hover: float = 40.0, step: float = 10.0,
                  camera: bool = True) -> list[tuple[float, float, float, float, float]]:
    """Poses for a top-down approach: `hover` mm above (x, y, z), then down in `step` mm moves to it. The claw
    points as near straight down as the arm reaches (-90°, else up to -45°), so the Brio stays at least
    CAMERA_ABOVE_MM above the fingertips and the claw meets the object first. Every pose is inside the joint
    limits and the sketch's guard. ValueError if no pitch works."""
    why = "no pitch tried"
    for pitch in range(-90, -44, 5):
        heights = [z + hover - k * step for k in range(int(math.ceil(hover / step)))] + [z]
        try:
            poses = [ik(x, y, h, pitch) + (gap,) for h in heights]
        except ValueError as err:
            why = str(err)
            continue
        if camera and camera_above_tips(poses[-1], gap) < CAMERA_ABOVE_MM:
            why = f"at pitch {pitch} the camera would come within {CAMERA_ABOVE_MM:.0f} mm of the fingertips' level"
            continue
        bad = [p for p in poses if min(guard_margins(p, camera)) < 0]
        if bad:
            why = f"at pitch {pitch} the guard refuses {fingertip(bad[0])[2]:.0f} mm (8 mm from the desk or base)"
            continue
        return poses
    raise ValueError(f"no top-down approach to ({x:.0f}, {y:.0f}, {z:.0f}): {why}")


def crop_claw(frame):
    """The raw camera frame without its bottom CLAW_ROWS, where the claw's own cover is (deep review 03, SYS-13).
    Use it on the raw frame, before any rotation."""
    return frame[: int(round(frame.shape[0] * (1.0 - CLAW_ROWS)))]


class Arm:
    """Serial link to arm_test.ino (115200 baud, newline-terminated commands), in joint degrees and mm.

    status() -> (base, shoulder, elbow, wrist in degrees, claw opening in mm)
    move(b, s, e, w, mm) -> True when every joint arrived, False if stopped by x
    grip(width), park(), approach(x, y, z) -> the same, through the sketch's own commands
    They raise RuntimeError when the sketch refuses ("err ...") or its guard ends the move early
    ("blocked: desk" / "blocked: base"), and TimeoutError when the arm doesn't answer in time.
    """

    def __init__(self, port: str, baud: int = 115200, timeout: float = 10.0):
        import serial  # pyserial
        self.timeout = timeout                   # longest a move may take before it gives up
        self.s = serial.Serial()                 # configure first, open last
        self.s.port, self.s.baudrate, self.s.timeout = port, baud, 0.2
        self.s.dtr = False                       # keep the auto-reset lines (EN, GPIO0) inactive when the port
        self.s.rts = False                       # opens: avoids the reset on most OS/driver combinations, not all
        self.s.open()
        try:
            self.status(wait=0.5)                # no reset: the sketch answers at once
        except TimeoutError:                     # it did reset: wait for the banner, then ask again
            self._read_until(lambda line: line.startswith(READY), 6.0, required=False)
            self.status()

    def _read_until(self, done, seconds: float, required: bool = True) -> str | None:
        end = time.monotonic() + seconds         # an overall deadline, even if the board keeps talking
        while time.monotonic() < end:
            line = self.s.readline().decode(errors="replace").strip()
            if line and done(line):
                return line
        if required:
            raise TimeoutError("no reply from the arm: is arm_test.ino running on this port?")
        return None

    def _send(self, text: str) -> None:
        self.s.reset_input_buffer()              # drop stale lines (the banner, an old "stopped" or "idle")
        self.s.write((text + "\n").encode())

    def _command(self, text: str, seconds: float | None = None) -> bool:
        """A typed-style command (h, r, g ...): its reply ends with an "angles" line, after "stopped" or
        "blocked: ..." if the move didn't arrive. True when it arrived."""
        self._send(text)
        result = []

        def done(line):
            if line.startswith(("stopped", "blocked")):
                result.append(line)
            return line.startswith(("angles", "err", "unknown"))
        last = self._read_until(done, self.timeout if seconds is None else seconds)
        if last.startswith(("err", "unknown")):
            raise RuntimeError(f"arm: {last}")
        if result and result[0].startswith("blocked"):
            raise RuntimeError(f"arm: {result[0]}")
        return not result

    def status(self, wait: float = 2.0) -> tuple[float, float, float, float, float]:
        """(base, shoulder, elbow, wrist in degrees, claw opening in mm)."""
        self._send("?")
        parts = self._read_until(lambda line: line.startswith("pos "), wait).split()[1:]
        return tuple(float(p) for p in parts)  # type: ignore[return-value]

    def move(self, base: float, shoulder: float, elbow: float, wrist: float, claw_mm: float,
             seconds: float | None = None) -> bool:
        """Move every joint together; True when all arrived, False if stopped by x."""
        q = (base, shoulder, elbow, wrist, claw_mm)
        if not all(math.isfinite(v) for v in q):
            raise ValueError(f"refusing a non-finite target {q}")   # f"{nan:.1f}" would send "nan"
        self._send("m " + " ".join(f"{v:.1f}" for v in q))
        reply = self._read_until(lambda line: line in ("ok", "stopped") or line.startswith(("err", "blocked")),
                                 self.timeout if seconds is None else seconds)
        if reply.startswith(("err", "blocked")):
            raise RuntimeError(f"arm: {reply}")
        return reply == "ok"

    def claw(self, mm: float) -> bool:
        """Jaws to an opening of mm, for an empty claw. To hold something use grip()."""
        b, s, e, w, _ = self.status()
        return self.move(b, s, e, w, mm)

    def grip(self, object_mm: float) -> bool:
        """Hold an object object_mm wide: the sketch closes 1.5 mm under its width, squeezes for at most 2 s,
        then eases off, so the claw servo never stays stalled. Open the claw wider than the object first."""
        if not 0 < object_mm <= LIMITS[4][1] or not math.isfinite(object_mm):
            raise ValueError(f"object width {object_mm} mm: give its measured width, 1-44 mm")
        return self._command(f"h {object_mm:.1f}")

    def park(self) -> bool:
        """Upright, where the shoulder holds about 0 N.mm. Base and claw stay as they are."""
        return self._command("r")

    def idle_park(self, seconds: int) -> None:
        """Park after this many seconds without a command (0 = never). The sketch keeps it in flash.
        Any command counts, so a program that sends ? now and then keeps the arm where it is."""
        self._send(f"i {int(seconds)}")
        self._read_until(lambda line: line.startswith(("idle park", "err")), 2.0)

    def approach(self, x: float, y: float, z: float, open_mm: float, hover: float = 40.0, step: float = 10.0) -> bool:
        """Fingertips to (x, y, z) from above with the claw open to open_mm: first `hover` mm above, then down
        in `step` mm moves with the claw pitched down, the camera above it (plan_approach). True if it arrived."""
        for q in plan_approach(x, y, z, open_mm, hover, step):
            if not self.move(*q):
                return False
        return True

    def stop(self) -> None:
        """Stop the current move. The move's own call then returns False."""
        self.s.write(b"x\n")

    def close(self) -> None:
        self.s.close()


def open_camera(camera: int, focus: int | None = None):
    import cv2
    api = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY   # DirectShow honours the format asked for
    cap = cv2.VideoCapture(camera, api)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))     # before the size: 1080p YUY2 doesn't fit USB 2.0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    if focus is not None:                       # lock the focus: autofocus hunts on the jaws 75 mm away
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        cap.set(cv2.CAP_PROP_FOCUS, focus)
    return cap


def preview(arm: Arm | None, camera: int, rotate: str, object_mm: float | None, focus: int | None) -> None:
    import cv2
    cap = open_camera(camera, focus)
    if not cap.isOpened():
        sys.exit(f"camera {camera} did not open: try --camera 1 (or 2)")
    rot = {"ccw": cv2.ROTATE_90_COUNTERCLOCKWISE, "cw": cv2.ROTATE_90_CLOCKWISE, "none": None}[rotate]
    grip_help = f"c = grip {object_mm:g} mm" if object_mm else "c = grip (start with --object-mm <width>)"
    print(f"o = open claw, {grip_help}, [ and ] = wrist -/+ 5°, p = park, , and . = focus -/+ 5, q = quit")
    failed, shown, message = 0, False, ""
    while True:
        ok, frame = cap.read()
        if not ok:                               # the first frames often fail while the camera starts
            failed += 1
            if failed > 30:
                print("the camera stopped sending frames")
                break
            time.sleep(0.03)
            continue
        failed = 0
        h0, w0 = frame.shape[:2]
        if not shown:
            print(f"camera {camera}: {w0} x {h0}. If this isn't the Brio (a laptop's own camera is often 0), "
                  "quit and use --camera 1")
            shown = True
        edge = int(round(h0 * (1.0 - CLAW_ROWS)))   # below this line of the raw frame: the claw's own cover
        cv2.line(frame, (0, edge), (w0 - 1, edge), (0, 165, 255), 2)   # orange (OpenCV colours are BGR)
        if rot is not None:
            frame = cv2.rotate(frame, rot)
        h, w = frame.shape[:2]
        cv2.drawMarker(frame, (w // 2, h // 2), (0, 255, 255), cv2.MARKER_CROSS, 40, 2)
        if arm is not None or focus is not None:
            text = message or ("arm connected" if arm else "") + (f"  focus {focus}" if focus is not None else "")
            cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255) if message else (0, 255, 0), 2)
        cv2.imshow("Brio on the claw", cv2.resize(frame, (w // 2, h // 2)))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key in (ord(","), ord(".")) and focus is not None:
            focus = max(0, min(255, focus + (5 if key == ord(".") else -5)))
            cap.set(cv2.CAP_PROP_FOCUS, focus)
            print(f"focus {focus}")
        if arm is None:
            continue
        try:
            if key == ord("o"):
                arm.claw(40.0)
                message = ""
            elif key == ord("c"):
                if object_mm:
                    arm.grip(object_mm)
                    message = ""
                else:
                    message = "c grips: measure the object, start with --object-mm <width>"
            elif key == ord("p"):
                arm.park()
                message = ""
            elif key in (ord("["), ord("]")):
                b, s, e, wr, g = arm.status()
                arm.move(b, s, e, wr + (5 if key == ord("]") else -5), g)
                message = ""
        except (RuntimeError, TimeoutError, ValueError) as err:   # e.g. "arm: blocked: desk": show it, keep going
            message = str(err)
            print(message)
    cap.release()
    cv2.destroyAllWindows()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="ESP32 serial port (omit for a camera-only preview)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    mv = sub.add_parser("move", help="move every joint: base shoulder elbow wrist (degrees), claw (mm)")
    for name in ("base", "shoulder", "elbow", "wrist", "claw_mm"):
        mv.add_argument(name, type=float)
    apr = sub.add_parser("approach", help="fingertips to x y z (mm) from above, claw pitched down")
    for name in ("x", "y", "z"):
        apr.add_argument(name, type=float)
    apr.add_argument("--open", type=float, default=30.0, help="claw opening on the way down, mm (default 30)")
    apr.add_argument("--hover", type=float, default=40.0, help="start this far above the target, mm (default 40)")
    gp = sub.add_parser("grip", help="hold an object of this width (mm)")
    gp.add_argument("object_mm", type=float)
    sub.add_parser("park", help="upright, where the shoulder holds about nothing")
    ip = sub.add_parser("idle", help="park after this many seconds without a command (0 = never)")
    ip.add_argument("seconds", type=int)
    pv = sub.add_parser("preview")
    pv.add_argument("--camera", type=int, default=0)
    pv.add_argument("--rotate", choices=["ccw", "cw", "none"], default="ccw")
    pv.add_argument("--object-mm", type=float, help="the object's measured width: c grips 1.5 mm under it")
    pv.add_argument("--focus", type=int, help="lock the focus at this value (0-255; , and . adjust it)")
    a = ap.parse_args()
    try:
        arm = Arm(a.port) if a.port else None
    except TimeoutError as err:
        sys.exit(str(err))
    if a.cmd == "preview":
        preview(arm, a.camera, a.rotate, a.object_mm, a.focus)
        return
    if arm is None:
        sys.exit("give --port")
    try:
        if a.cmd == "status":
            print(arm.status())
        elif a.cmd == "move":
            print("arrived" if arm.move(a.base, a.shoulder, a.elbow, a.wrist, a.claw_mm) else "stopped")
        elif a.cmd == "approach":
            print("arrived" if arm.approach(a.x, a.y, a.z, a.open, a.hover) else "stopped")
        elif a.cmd == "grip":
            print("holding" if arm.grip(a.object_mm) else "stopped")
        elif a.cmd == "park":
            print("parked" if arm.park() else "stopped")
        elif a.cmd == "idle":
            arm.idle_park(a.seconds)
            print(f"idle park after {a.seconds} s" if a.seconds else "idle park off")
    except (RuntimeError, ValueError, TimeoutError) as err:
        sys.exit(str(err))


if __name__ == "__main__":
    main()
