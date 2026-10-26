"""arm_test.ino on the PC: compile it against shim/ (no ESP32 toolchain needed), run the scripted serial sessions
in arm_harness.cpp, check that the sketch's guard and pc/arm_pc_control.py's copy agree, and drive the PC tool's
Arm class against the compiled sketch through a pipe.

Run:  python -m pytest -q jobs/20261025-robot-arm-assembly/firmware_test
Needs g++ (skipped without it). It doesn't catch ESP32 link errors or library-version problems: compile once in
the Arduino IDE too. The slow mesh check of the guard is guard_mesh_check.py (run by hand).
"""
from __future__ import annotations

import importlib.util
import os
import random
import select
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JOB = HERE.parent
INO = JOB / "arm_test" / "arm_test.ino"
GXX = shutil.which("g++")
pytestmark = pytest.mark.skipif(GXX is None, reason="needs g++")


def _load_pc():
    spec = importlib.util.spec_from_file_location("arm_pc_control_fw", JOB / "pc" / "arm_pc_control.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build(src: str, out: Path, std: str) -> Path:
    cmd = [GXX, f"-std={std}", "-O1", "-Wall", "-Wextra", "-Wno-unused-parameter", f"-I{HERE / 'shim'}",
           f'-DARM_INO="{INO}"', "-o", str(out), str(HERE / src)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    warnings = [line for line in r.stderr.splitlines() if "arm_test.ino" in line and "warning" in line]
    assert not warnings, "\n".join(warnings)
    return out


@pytest.fixture(scope="module")
def bins(tmp_path_factory):
    d = tmp_path_factory.mktemp("arm_fw")
    return {
        "harness_c++11": _build("arm_harness.cpp", d / "harness11", "c++11"),
        "harness_c++23": _build("arm_harness.cpp", d / "harness23", "c++23"),
        "guard": _build("guard_cli.cpp", d / "guard", "c++23"),
        "bridge": _build("arm_bridge.cpp", d / "bridge", "c++23"),
    }


def test_scripted_sessions(bins):
    logs = []
    for std in ("c++11", "c++23"):
        r = subprocess.run([str(bins[f"harness_{std}"])], capture_output=True, text=True, timeout=300)
        fails = [line for line in r.stdout.splitlines() if line.startswith("  FAIL")]
        assert r.returncode == 0 and not fails, "\n".join(fails) or r.stdout[-2000:]
        assert "ALL ARM CHECKS PASSED" in r.stdout
        logs.append(r.stdout)
    assert logs[0] == logs[1], "the C++11 (core 2.x) and C++23 (core 3.x) builds behave differently"


def test_guard_matches_pc_model(bins):
    pc = _load_pc()
    rng = random.Random(3)
    poses = [(0, 0, 0, 0, 0), (0, 0, -26.4, 0, 0), (0, 54.3, -150, -30, 0), (45, 52.5, -140, -40, 0),
             (90, 40, -120, -60, 0), (-90, 10, -150, 90, 44), (0, 180, 30, 90, 44)]
    poses += [tuple(rng.uniform(lo, hi) for lo, hi in pc.LIMITS) for _ in range(20000)]
    text = "".join(" ".join(f"{v:.6f}" for v in q) + "\n" for q in poses)
    out = subprocess.run([str(bins["guard"])], input=text, capture_output=True, text=True, check=True).stdout.split("\n")
    worst = 0.0
    for q, line in zip(poses, out):
        d, b = (float(v) for v in line.split())
        pd, pb = pc.guard_margins(q)
        worst = max(worst, abs(d - pd), abs(min(b, 1e6) - min(pb, 1e6)))
    assert worst < 0.01, f"sketch and PC guard differ by up to {worst:.4f} mm"


class BridgePort:
    """pyserial-like port: the sketch runs in a subprocess. reset=True: the board resets when the port opens."""
    reset = False
    bridge = None
    opened_with = None

    def __init__(self):
        self.port = self.baudrate = self.timeout = None
        self.dtr = self.rts = True
        self.buf = b""
        self.p = None

    def open(self):
        BridgePort.opened_with = (self.dtr, self.rts)
        self.p = subprocess.Popen([BridgePort.bridge, "1.0" if BridgePort.reset else "0"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        if not BridgePort.reset:                 # no reset: the banner was printed long before we opened
            t = time.monotonic()
            while b"arm_test ready" not in self.buf and time.monotonic() - t < 5:
                self._fill(0.1)
            self._fill(0.05)
            self.buf = b""

    def _fill(self, wait):
        r, _, _ = select.select([self.p.stdout], [], [], wait)
        if r:
            self.buf += os.read(self.p.stdout.fileno(), 65536)

    def readline(self):
        end = time.monotonic() + (self.timeout or 0)
        while b"\n" not in self.buf and time.monotonic() < end:
            self._fill(max(0.0, end - time.monotonic()))
        if b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            return line + b"\n"
        return b""

    def write(self, data):
        self.p.stdin.write(data)
        self.p.stdin.flush()

    def reset_input_buffer(self):
        self._fill(0.0)
        self.buf = b""

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=5)


class ChattyPort(BridgePort):
    """A board in a boot loop: prints a line every 10 ms and never answers."""
    def open(self):
        BridgePort.opened_with = (self.dtr, self.rts)

    def readline(self):
        time.sleep(0.01)
        return b"Brownout detector was triggered\n"

    def write(self, data):
        pass

    def reset_input_buffer(self):
        pass

    def close(self):
        pass


@pytest.fixture
def pc_on_bridge(bins, monkeypatch):
    fake = types.ModuleType("serial")
    fake.Serial = BridgePort
    monkeypatch.setitem(sys.modules, "serial", fake)
    BridgePort.bridge, BridgePort.reset = str(bins["bridge"]), False
    return _load_pc(), fake


def test_pc_tool_against_the_sketch(pc_on_bridge):
    pc, fake = pc_on_bridge
    t = time.monotonic()
    arm = pc.Arm("fake")
    assert BridgePort.opened_with == (False, False) and time.monotonic() - t < 0.6
    assert arm.status() == (0.0, 90.0, -60.0, 0.0, 0.0)                     # first boot: the horn-fitting pose
    assert arm.park() is True and arm.status() == (0.0, 90.0, 0.0, 0.0, 0.0)
    assert arm.move(0, 60, -90, -50, 20) is True and arm.status() == (0.0, 60.0, -90.0, -50.0, 20.0)
    arm.stop()                                                                # nothing moves: "idle", left unread
    assert arm.move(0, 70, -90, -50, 20) is True, "a stale 'idle' must not become the next move's reply"
    with pytest.raises(ValueError):
        arm.move(float("nan"), 60, -90, -50, 20)
    # the guard: the arm straight out, then the forearm down into the desk
    assert arm.move(0, 0, 0, 0, 0) is True
    with pytest.raises(RuntimeError, match="arm: blocked: desk"):
        arm.move(0, 0, -90, 0, 0)
    assert -27 < arm.status()[2] < -25
    with pytest.raises(RuntimeError, match="arm: blocked: desk"):
        arm.claw(30)                                                          # the jaws widen towards the desk
    # the base keep-out: elbow folded, shoulder lowered
    assert arm.park() is True
    assert arm.move(0, 64, -150, -30, 0) is True          # the cover's foot (claw round 3) stops it at s 61.5
    with pytest.raises(RuntimeError, match="arm: blocked: base"):
        arm.move(0, 15, -150, -30, 0)
    assert arm.park() is True
    # a top-down approach, then a grip: the fingertips end where they were asked to
    assert arm.approach(160, 80, -25, open_mm=30) is True
    q = arm.status()
    tip = pc.fingertip(q)
    assert max(abs(a - b) for a, b in zip(tip, (160, 80, -25))) < 0.6, (q, tip)
    assert q[1] + q[2] + q[3] == pytest.approx(-90, abs=0.15) and q[4] == 30.0
    assert arm.grip(20) is True and arm.status()[4] == 18.5
    with pytest.raises(RuntimeError, match="err need the object's width"):
        arm._command("h 60")
    arm.idle_park(0)
    assert arm.park() is True
    arm.close()


def test_pc_tool_reset_and_hang(pc_on_bridge):
    pc, fake = pc_on_bridge
    BridgePort.reset = True                       # the board resets when the port opens: banner after 1 s
    t = time.monotonic()
    arm = pc.Arm("fake")
    dt = time.monotonic() - t
    assert arm.status() == (0.0, 90.0, -60.0, 0.0, 0.0) and 1.0 < dt < 5.0
    arm.close()
    fake.Serial = ChattyPort                      # a board that keeps talking can't hang the script
    t = time.monotonic()
    with pytest.raises(TimeoutError):
        pc.Arm("fake")
    assert time.monotonic() - t < 10


def test_pc_cli_against_the_sketch(pc_on_bridge, monkeypatch, capsys):
    pc, fake = pc_on_bridge
    monkeypatch.setattr(sys, "argv", ["arm_pc_control.py", "--port", "fake", "move", "0", "0", "-90", "0", "0"])
    with pytest.raises(SystemExit, match="arm: blocked: desk"):
        pc.main()
    monkeypatch.setattr(sys, "argv", ["arm_pc_control.py", "--port", "fake", "approach", "160", "80", "-38"])
    with pytest.raises(SystemExit, match="no top-down approach"):
        pc.main()
    monkeypatch.setattr(sys, "argv", ["arm_pc_control.py", "--port", "fake", "park"])
    pc.main()
    assert "parked" in capsys.readouterr().out
