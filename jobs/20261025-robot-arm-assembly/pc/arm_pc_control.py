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

The camera sits on the claw's side, turned 90° to the arm: with the claw level, world "up"
appears at the right edge of the raw image. --rotate (default ccw) turns the preview upright.
"""
from __future__ import annotations

import argparse
import sys
import time


class Arm:
    """Serial link to arm_test.ino (115200 baud, newline-terminated commands)."""

    def __init__(self, port: str, baud: int = 115200, timeout: float = 30.0):
        import serial  # pyserial
        self.s = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2.0)                      # the ESP32 resets when the port opens
        self.s.reset_input_buffer()

    def _cmd(self, text: str, expect: str | None = None) -> str:
        self.s.write((text + "\n").encode())
        while True:
            line = self.s.readline().decode(errors="replace").strip()
            if not line:
                raise TimeoutError(f"no reply to {text!r}")
            if expect is None or line.startswith(expect):
                return line

    def status(self) -> tuple[float, float, float, float, float]:
        """(base, shoulder, elbow, wrist in degrees, claw opening in mm)."""
        parts = self._cmd("?", expect="pos").split()[1:]
        return tuple(float(p) for p in parts)  # type: ignore[return-value]

    def move(self, base: float, shoulder: float, elbow: float, wrist: float, claw_mm: float) -> bool:
        """Move every joint together; True when all arrived, False if stopped."""
        self.s.write(f"m {base:.0f} {shoulder:.0f} {elbow:.0f} {wrist:.0f} {claw_mm:.1f}\n".encode())
        while True:
            reply = self.s.readline().decode(errors="replace").strip()
            if not reply:
                raise TimeoutError("the arm did not answer the move")
            if reply in ("ok", "stopped") or reply.startswith("err"):
                return reply == "ok"

    def claw(self, mm: float) -> bool:
        b, s, e, w, _ = self.status()
        return self.move(b, s, e, w, mm)

    def stop(self) -> None:
        self.s.write(b"x\n")


def preview(arm: Arm | None, camera: int, rotate: str) -> None:
    import cv2
    cap = cv2.VideoCapture(camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    rot = {"ccw": cv2.ROTATE_90_COUNTERCLOCKWISE, "cw": cv2.ROTATE_90_CLOCKWISE, "none": None}[rotate]
    if not cap.isOpened():
        sys.exit(f"camera {camera} did not open: try --camera 1")
    print("o/c = open/close claw, [ and ] = wrist -/+ 5°, q = quit")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if rot is not None:
            frame = cv2.rotate(frame, rot)
        h, w = frame.shape[:2]
        cv2.drawMarker(frame, (w // 2, h // 2), (0, 255, 255), cv2.MARKER_CROSS, 40, 2)
        if arm is not None:
            cv2.putText(frame, "arm connected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.imshow("Brio on the claw", cv2.resize(frame, (w // 2, h // 2)))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if arm is None:
            continue
        if key in (ord("o"), ord("c")):
            arm.claw(40.0 if key == ord("o") else 0.0)
        elif key in (ord("["), ord("]")):
            b, s, e, wr, g = arm.status()
            arm.move(b, s, e, wr + (5 if key == ord("]") else -5), g)
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
    arm = Arm(a.port) if a.port else None
    if a.cmd == "status":
        print(arm.status() if arm else "give --port")
    elif a.cmd == "move":
        if not arm:
            sys.exit("give --port")
        print("arrived" if arm.move(a.base, a.shoulder, a.elbow, a.wrist, a.claw_mm) else "stopped")
    else:
        preview(arm, a.camera, a.rotate)


if __name__ == "__main__":
    main()
