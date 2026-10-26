"""Tests for arm_pc_control.py: kinematics against the CAD, the guard's part boxes, approach planning, protocol.

Run:  python -m pytest -q jobs/20261025-robot-arm-assembly/pc
The CAD checks need build123d (the project's CAD venv) and are skipped without it. The PC tool against the real
sketch, compiled for the PC, is in ../firmware_test/test_firmware.py.
"""
from __future__ import annotations

import importlib.util
import math
import random
import sys
import types
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JOB = HERE.parent
ROOT = JOB.parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = _load(HERE / "arm_pc_control.py", "arm_pc_control")


@pytest.fixture(scope="module")
def cad():
    """The CAD's own frame constants, and assembly_check.py's place() chain for the fingertip."""
    pytest.importorskip("build123d")
    np = pytest.importorskip("numpy")
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(JOB))
    import claw_frame as C
    from hobby_parts import BRIO_4K, MG90S, MG996R, link_back_z
    tt = _load(ROOT / "jobs/20261025-arm-turntable/model.py", "m_turntable")
    up = _load(ROOT / "jobs/20261025-arm-upper-link/model.py", "m_upper")
    fa = _load(ROOT / "jobs/20261025-arm-forearm/model.py", "m_forearm")
    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(MG90S)

    def T(x=0.0, y=0.0, z=0.0):
        m = np.eye(4); m[:3, 3] = (x, y, z); return m

    def Rz(d):
        c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
        m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m

    def frame(o, xd, zd):
        x = np.array(xd, float); x /= np.linalg.norm(x)
        z = np.array(zd, float); z /= np.linalg.norm(z)
        m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, np.cross(z, x), z, o
        return m

    def place_tip(q):                       # assembly_check.py place(), fingertip only
        yaw, sh, el, wr = q[:4]
        U = Rz(yaw) @ frame((tt.XS, tt.UP_Y + lb_mg, tt.ZS), (math.cos(math.radians(sh)), 0, math.sin(math.radians(sh))), (0, 1, 0))
        F = U @ T(100, 0, up.T + lb_mg) @ Rz(-el)
        G = F @ T(90, 0, fa.T + lb_sg) @ Rz(-wr)
        return (G @ np.array([C.X_TIP - 3.0, 0.0, C.ZS, 1.0]))[:3]

    return types.SimpleNamespace(C=C, tt=tt, up=up, fa=fa, lb_mg=lb_mg, lb_sg=lb_sg, BRIO=BRIO_4K, place_tip=place_tip)


def random_pose(rng):
    return tuple(rng.uniform(lo, hi) for lo, hi in pc.LIMITS[:4])


def test_fingertip_matches_assembly_check(cad):
    rng = random.Random(1)
    for q in [(0, 0, 0, 0), (0, 90, 0, 0), (0, 90, -60, 0), (-30, 60, -80, -60), (45, 45, -45, 0)] + \
             [random_pose(rng) for _ in range(300)]:
        mine, ref = pc.fingertip(q), cad.place_tip(q)
        assert max(abs(a - b) for a, b in zip(mine, ref)) < 1e-6, (q, mine, ref)


def test_geometry_constants_match_cad(cad):
    C = cad.C
    assert pc.SHOULDER_X == pytest.approx(cad.tt.XS) and pc.SHOULDER_Z == pytest.approx(cad.tt.ZS)
    assert pc.TIP_L == pytest.approx(C.X_TIP - 3.0)
    assert pc.TIP_Y == pytest.approx(cad.place_tip((0, 0, 0, 0))[1], abs=1e-6)
    assert (pc.UPPER_L, pc.FORE_L) == (cad.up.L, cad.fa.L)


def test_guard_part_boxes_match_cad(cad):
    """If the claw or the servo stack changes in the CAD, these fail: re-measure the part boxes with
    firmware_test/guard_mesh_check.py, then update PARTS here and in arm_test.ino."""
    C, P = cad.C, {i: p for i, p in enumerate(pc.PARTS)}
    y_fore = cad.tt.UP_Y + cad.lb_mg + cad.up.T + cad.lb_mg        # forearm's back face, sideways
    y_claw = y_fore + cad.fa.T + cad.lb_sg                            # claw frame's back face
    assert P[1][5:7] == pytest.approx((y_fore, y_fore + cad.fa.T))
    assert P[3][5] == pytest.approx(y_claw) and P[3][2] == pytest.approx(C.X_F1) and P[3][4] == pytest.approx(C.HALF_Y)
    assert P[4][2] == pytest.approx(C.PAD_X[1]) and P[4][3:5] == pytest.approx(C.MOUNT_Y)
    t = math.radians(C.CAM_TILT)
    assert P[5][1:5] == pytest.approx((C.CAM_XC - cad.BRIO.width / 2 * math.cos(t),
                                       C.CAM_XC + cad.BRIO.width / 2 * math.cos(t) + cad.BRIO.height * math.sin(t),
                                       -cad.BRIO.length / 2, cad.BRIO.length / 2), abs=0.01)
    assert P[6][1:3] == pytest.approx((C.X_P0, C.X_P1))
    assert P[7][2] == pytest.approx(C.NECK_X1 + C.NECK_Y - C.BLADE_T)
    assert P[8][2] == pytest.approx(C.X_TIP)
    # the jaws' y rules: racks max(28.27 - g/2, 15.71 + g/2), necks 14 + g/2, blades 6 + g/2
    assert (-C.RACK_Y[0], C.RACK_Y[1]) == pytest.approx((15.71, 28.27), abs=0.01)
    assert (C.NECK_Y, C.BLADE_T) == (14.0, 6.0)


def test_ik_round_trip():
    rng = random.Random(2)
    n = 0
    while n < 300:
        q = random_pose(rng)
        x, y, z = pc.fingertip(q)
        pitch = q[1] + q[2] + q[3]
        try:
            q2 = pc.ik(x, y, z, pitch)
        except ValueError:
            continue            # the other elbow branch, or a yaw past +-90: ik only gives the elbow-down one
        assert max(abs(a - b) for a, b in zip(pc.fingertip(q2), (x, y, z))) < 1e-6
        assert q2[1] + q2[2] + q2[3] == pytest.approx(pitch)
        n += 1


def test_ik_refuses_what_the_arm_cant_do():
    with pytest.raises(ValueError):
        pc.ik(400, 0, 0)                    # out of reach
    with pytest.raises(ValueError):
        pc.ik(10, 20, 0)                    # inside the arm's sideways offset
    with pytest.raises(ValueError):
        pc.ik(40, 80, -20)                  # needs the elbow past -150


def test_camera_above_tips():
    assert pc.camera_above_tips((0, 90, -150, -30)) == pytest.approx(64.2, abs=0.1)   # claw straight down
    assert pc.camera_above_tips((0, 0, 0, 0)) < -40                                    # level: the camera hangs low
    assert pc.camera_above_tips((0, 45, -60, -30), gap=0) == pytest.approx(13.5, abs=0.1)   # pitch -45


def test_plan_approach():
    poses = pc.plan_approach(160, 80, -25, gap=30)
    assert len(poses) == 5
    heights = [pc.fingertip(q)[2] for q in poses]
    assert heights == pytest.approx([15, 5, -5, -15, -25])
    for q in poses:
        x, y, _ = pc.fingertip(q)
        assert (x, y) == pytest.approx((160, 80), abs=1e-6)
        assert q[1] + q[2] + q[3] == pytest.approx(-90)                   # straight down: camera 64 mm above
        assert min(pc.guard_margins(q)) >= 0 and q[4] == 30
        for v, (lo, hi) in zip(q, pc.LIMITS):
            assert lo <= v <= hi


def test_plan_approach_tilts_when_straight_down_is_out_of_reach():
    with pytest.raises(ValueError):
        pc.ik(225, 80, -15, -90)                        # too far out to point straight down
    poses = pc.plan_approach(225, 80, -15, gap=20)      # (a tilted claw's jaw corner dips below the tip point)
    pitch = poses[-1][1] + poses[-1][2] + poses[-1][3]
    assert -90 < pitch <= -45 and pc.camera_above_tips(poses[-1], 20) >= pc.CAMERA_ABOVE_MM
    assert pc.fingertip(poses[-1]) == pytest.approx((225, 80, -15))


def test_plan_approach_refuses():
    with pytest.raises(ValueError, match="no top-down approach"):
        pc.plan_approach(160, 80, -38, gap=10)          # 2 mm above the desk: inside the guard's 8 mm
    with pytest.raises(ValueError, match="no top-down approach"):
        pc.plan_approach(400, 0, 0, gap=10)


def test_crop_claw():
    np = pytest.importorskip("numpy")
    frame = np.zeros((1080, 1920, 3), np.uint8)
    assert pc.crop_claw(frame).shape == (648, 1920, 3)


class FakePort:
    """pyserial-like port answering like arm_test.ino, line by line, from a script of replies."""
    def __init__(self, replies):
        self.replies, self.sent, self.buf = replies, [], []
        self.port = self.baudrate = self.timeout = None
        self.dtr = self.rts = True

    def open(self):
        self.opened_with = (self.dtr, self.rts)

    def write(self, data):
        cmd = data.decode().strip()
        self.sent.append(cmd)
        self.buf += [(r + "\n").encode() for r in self.replies(cmd)]

    def readline(self):
        return self.buf.pop(0) if self.buf else b""

    def reset_input_buffer(self):
        self.buf = []

    def close(self):
        pass


def _arm(replies, monkeypatch):
    fake = types.ModuleType("serial")
    port = FakePort(replies)
    fake.Serial = lambda: port
    monkeypatch.setitem(sys.modules, "serial", fake)
    return pc.Arm("fake", timeout=1.0), port


def test_protocol(monkeypatch):
    def replies(cmd):
        if cmd == "?":
            return ["claw eased off to 19.0 mm", "pos 0.0 90.0 0.0 0.0 19.0"]
        if cmd.startswith("m "):
            return ["blocked: base"] if cmd.split()[2] == "20.0" else ["ok"]
        if cmd == "h 20.0":
            return ["angles b s e w | claw mm: 0.0 90.0 0.0 0.0 18.5"]
        if cmd == "r":
            return ["blocked: desk", "angles b s e w | claw mm: 0.0 80.0 0.0 0.0 0.0"]
        if cmd == "i 0":
            return ["idle park off"]
        return ["unknown command: b s e w g h r i t c f k u p m ? x"]
    arm, port = _arm(replies, monkeypatch)
    assert port.opened_with == (False, False)
    assert arm.status() == (0.0, 90.0, 0.0, 0.0, 19.0)
    assert arm.move(0, 60, -90.04, -50, 20) is True and port.sent[-1] == "m 0.0 60.0 -90.0 -50.0 20.0"
    with pytest.raises(RuntimeError, match="arm: blocked: base"):
        arm.move(0, 20, -150, 0, 0)
    assert arm.grip(20) is True
    with pytest.raises(ValueError):
        arm.grip(0)
    with pytest.raises(ValueError):
        arm.grip(float("nan"))
    with pytest.raises(ValueError):
        arm.move(float("nan"), 90, 0, 0, 0)
    with pytest.raises(RuntimeError, match="blocked: desk"):
        arm.park()
    arm.idle_park(0)
    assert port.sent[-1] == "i 0"


def _fake_cv2(np, keys, log):
    """Just enough of OpenCV for preview(): frames of 1080 x 1920, scripted keys, a log of what it was asked."""
    cv2 = types.ModuleType("cv2")
    for i, name in enumerate(("CAP_DSHOW", "CAP_ANY", "CAP_PROP_FOURCC", "CAP_PROP_FRAME_WIDTH", "CAP_PROP_FRAME_HEIGHT",
                              "CAP_PROP_FPS", "CAP_PROP_AUTOFOCUS", "CAP_PROP_FOCUS", "ROTATE_90_COUNTERCLOCKWISE",
                              "ROTATE_90_CLOCKWISE", "MARKER_CROSS", "FONT_HERSHEY_SIMPLEX")):
        setattr(cv2, name, i)

    class Cap:
        def __init__(self, camera, api):
            pass

        def set(self, prop, value):
            log.append(("set", prop, value))

        def isOpened(self):
            return True

        def read(self):
            return True, np.zeros((1080, 1920, 3), np.uint8)

        def release(self):
            pass
    cv2.VideoCapture = Cap
    cv2.VideoWriter_fourcc = lambda *c: 0
    cv2.rotate = lambda f, r: np.rot90(f, 1 if r == cv2.ROTATE_90_COUNTERCLOCKWISE else -1)
    cv2.line = lambda f, p0, p1, colour, t: log.append(("line", p0, p1, colour))
    cv2.drawMarker = cv2.putText = cv2.imshow = lambda *a, **k: None
    cv2.resize = lambda f, size: f
    cv2.waitKey = lambda ms: keys.pop(0) if keys else ord("q")
    cv2.destroyAllWindows = lambda: None
    return cv2


def test_preview_keys(monkeypatch, capsys):
    np = pytest.importorskip("numpy")

    def replies(cmd):
        if cmd == "?":
            return ["pos 0.0 90.0 0.0 0.0 0.0"]
        if cmd.startswith("m "):
            return ["ok"]
        if cmd in ("h 20.0", "r"):
            return ["angles b s e w | claw mm: 0.0 90.0 0.0 0.0 18.5"]
        return ["unknown command"]
    arm, port = _arm(replies, monkeypatch)
    log = []
    keys = [ord(k) for k in "ocp[].,"]
    monkeypatch.setitem(sys.modules, "cv2", _fake_cv2(np, keys, log))
    pc.preview(arm, 0, "ccw", 20.0, 200)
    sent = [c for c in port.sent if c != "?"]
    assert sent == ["m 0.0 90.0 0.0 0.0 40.0", "h 20.0", "r", "m 0.0 90.0 0.0 -5.0 0.0", "m 0.0 90.0 0.0 5.0 0.0"]
    cv2 = sys.modules["cv2"]
    assert ("set", cv2.CAP_PROP_AUTOFOCUS, 0) in log and [v for s, p, v in (e for e in log if e[0] == "set")
                                                          if p == cv2.CAP_PROP_FOCUS] == [200, 205, 200]
    assert ("line", (0, 648), (1919, 648), (0, 165, 255)) in log      # the claw's 40 %, on the raw frame
    port.sent.clear()
    monkeypatch.setitem(sys.modules, "cv2", _fake_cv2(np, [ord("c")], log))
    pc.preview(arm, 0, "ccw", None, None)
    assert not [c for c in port.sent if c.startswith("h")]           # no width given: c doesn't squeeze
