#!/usr/bin/env python3
"""Drive the desktop robot arm from a PC and watch the claw through the Brio 4K.

The Brio plugs into the PC (USB), not the ESP32: the ESP32 has no USB host. The ESP32 runs
arm_test.ino and takes simple serial commands; this script is a starting point for your own
vision code (OpenCV), not a finished pick-and-place program.

Install:  pip install pyserial opencv-python
Examples:
  python arm_pc_control.py --port COM5 status            # Windows; /dev/ttyUSB0 on Linux, /dev/cu.* on macOS
  python arm_pc_control.py --port COM5 move 90 60 80 100 20
  python arm_pc_control.py --port COM5 preview --camera 0  # live view; o/c open/close, [ ] wrist, q quit

Keep one connection open for a whole session (the preview, or one Arm object in your own code)
rather than starting this script once per move: on some PCs and drivers opening the port still
resets the ESP32. The sketch then restarts where the arm stopped, but each reset costs about 2 s.

The camera sits on the claw's side, turned 90° to the arm: with the claw level, world "up"
appears at the right edge of the raw image. --rotate (default ccw) turns the preview upright.
"""
from __future__ import annotations

import argparse
import math
import sys
import time

READY = "arm_test ready"


class Arm:
    """Serial link to arm_test.ino (115200 baud, newline-terminated commands).

    status() -> (base, shoulder, elbow, wrist in degrees, claw opening in mm)
    move(b, s, e, w, mm) -> True when every joint arrived, False if stopped by x
    move() raises RuntimeError when the sketch refuses the move ("err ...") or its desk guard
    stops it ("blocked: desk"), and TimeoutError when the arm doesn't answer in time.
    """

    def __init__(self, port: str, baud: int = 115200, timeout: float = 10.0):
        import serial  # pyserial
        self.timeout = timeout                   # longest a move may take before move() gives up
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
            raise ValueError(f"refusing a non-finite target {q}")   # f"{nan:.0f}" would send "nan"
        self._send(f"m {base:.0f} {shoulder:.0f} {elbow:.0f} {wrist:.0f} {claw_mm:.1f}")
        reply = self._read_until(lambda line: line in ("ok", "stopped") or line.startswith(("err", "blocked")),
                                 self.timeout if seconds is None else seconds)
        if reply.startswith(("err", "blocked")):
            raise RuntimeError(f"arm: {reply}")
        return reply == "ok"

    def claw(self, mm: float) -> bool:
        b, s, e, w, _ = self.status()
        return self.move(b, s, e, w, mm)

    def stop(self) -> None:
        """Stop the current move. The move's own call then returns False."""
        self.s.write(b"x\n")

    def close(self) -> None:
        self.s.close()


def open_camera(camera: int):
    import cv2
    api = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY   # DirectShow honours the format asked for
    cap = cv2.VideoCapture(camera, api)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))     # before the size: 1080p YUY2 doesn't fit USB 2.0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap


def preview(arm: Arm | None, camera: int, rotate: str) -> None:
    import cv2
    cap = open_camera(camera)
    if not cap.isOpened():
        sys.exit(f"camera {camera} did not open: try --camera 1 (or 2)")
    rot = {"ccw": cv2.ROTATE_90_COUNTERCLOCKWISE, "cw": cv2.ROTATE_90_CLOCKWISE, "none": None}[rotate]
    print("o/c = open/close claw, [ and ] = wrist -/+ 5°, q = quit")
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
        if not shown:
            h0, w0 = frame.shape[:2]
            print(f"camera {camera}: {w0} x {h0}. If this isn't the Brio (a laptop's own camera is often 0), "
                  "quit and use --camera 1")
            shown = True
        if rot is not None:
            frame = cv2.rotate(frame, rot)
        h, w = frame.shape[:2]
        cv2.drawMarker(frame, (w // 2, h // 2), (0, 255, 255), cv2.MARKER_CROSS, 40, 2)
        if arm is not None:
            cv2.putText(frame, message or "arm connected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 0, 255) if message else (0, 255, 0), 2)
        cv2.imshow("Brio on the claw", cv2.resize(frame, (w // 2, h // 2)))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if arm is None:
            continue
        try:
            if key in (ord("o"), ord("c")):
                arm.claw(40.0 if key == ord("o") else 0.0)
                message = ""
            elif key in (ord("["), ord("]")):
                b, s, e, wr, g = arm.status()
                arm.move(b, s, e, wr + (5 if key == ord("]") else -5), g)
                message = ""
        except (RuntimeError, TimeoutError) as err:    # e.g. "arm: blocked: desk": show it, keep the preview
            message = str(err)
            print(message)
    cap.release()
    cv2.destroyAllWindows()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="ESP32 serial port (omit for camera-only preview)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    mv = sub.add_parser("move")
    for name in ("base", "shoulder", "elbow", "wrist", "claw_mm"):
        mv.add_argument(name, type=float)
    pv = sub.add_parser("preview")
    pv.add_argument("--camera", type=int, default=0)
    pv.add_argument("--rotate", choices=["ccw", "cw", "none"], default="ccw")
    a = ap.parse_args()
    try:
        arm = Arm(a.port) if a.port else None
    except TimeoutError as err:
        sys.exit(str(err))
    if a.cmd == "status":
        print(arm.status() if arm else "give --port")
    elif a.cmd == "move":
        if not arm:
            sys.exit("give --port")
        try:
            print("arrived" if arm.move(a.base, a.shoulder, a.elbow, a.wrist, a.claw_mm) else "stopped")
        except (RuntimeError, ValueError, TimeoutError) as err:
            sys.exit(str(err))
    else:
        preview(arm, a.camera, a.rotate)


if __name__ == "__main__":
    main()
