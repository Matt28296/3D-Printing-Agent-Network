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
    """The CAD's own modules and assembly_check.py's chain(), the arm's kinematics as the CAD checks place it."""
    pytest.importorskip("build123d")
    pytest.importorskip("trimesh")
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(JOB))
    import assembly_check as AC
    import claw_frame as C
    from hobby_parts import MG90S, MG996R, link_back_z
    mods = {k: AC.load_model(v) for k, v in AC.JOBS.items()}
    place = AC.chain(mods)
    return types.SimpleNamespace(AC=AC, C=C, mods=mods, tt=mods["turntable"], up=mods["upper"], fa=mods["forearm"],
                                 lb_mg=link_back_z(MG996R), lb_sg=link_back_z(MG90S), MG90S=MG90S,
                                 place_tip=lambda q: place(tuple(q[:4]) + (0.0,))[1])


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
    """If the claw or the servo stack changes in the CAD, these fail: re-measure the part boxes (and run
    firmware_test/guard_mesh_check.py), then update PARTS here and in arm_test.ino."""
    np = pytest.importorskip("numpy")
    C, AC, P = cad.C, cad.AC, {i: p for i, p in enumerate(pc.PARTS)}
    y_fore = cad.tt.UP_Y + cad.lb_mg + cad.up.T + cad.lb_mg        # forearm's back face, sideways
    y_claw = y_fore + cad.fa.T + cad.lb_sg                            # claw frame's back face
    assert P[1][5:7] == pytest.approx((y_fore, y_fore + cad.fa.T))
    # claw body: claw MG90S's case bottom .. the cover's front plate; the front plate's foot .. the top wall
    assert P[3][1:7] == pytest.approx((C.X_B - cad.MG90S.tab_height, C.X_F1, -C.HALF_Y, C.HALF_Y,
                                       y_claw + C.FRONT_Z0, y_claw + C.Z_TOP1))
    # camera mount and the Brio with its plug and thumb screw: bounding boxes of the CAD solids in the claw frame
    lo, hi = AC.to_mesh(cad.mods["camera_mount"].design()).bounds
    assert P[4][1:7] == pytest.approx((lo[0], hi[0], lo[1], hi[1], y_claw + lo[2], y_claw + hi[2]), abs=0.01)
    brio = AC.to_mesh(AC.brio_with_plug()).apply_transform(AC.T(C.CAM_XC, 0, C.CAM_ZC) @ AC.Ry(C.CAM_TILT))
    lo, hi = brio.bounds
    assert P[5][1:7] == pytest.approx((lo[0], hi[0], lo[1], hi[1], y_claw + lo[2], y_claw + hi[2]), abs=0.01)
    # jaws: x bands rack | neck and its 45° step down to the finger root | root and taper | tip, each band's end
    # padded by the kink fillet; sideways, jaw B is jaw A turned about the pinion axis
    jaw_x = (C.X_P0, C.X_P1, C.NECK_X1 + C.NECK_Y - C.BLADE_T_ROOT + C.KINK_FILLET, C.TAPER_X1 + C.KINK_FILLET, C.X_TIP)
    jaw_Y = (y_claw + 2 * C.ZS - C.Z_TOP0, y_claw + C.Z_TOP0)
    for i, k in zip(range(6, 10), range(4)):
        assert P[i][1:3] == pytest.approx(jaw_x[k:k + 2]) and P[i][5:7] == pytest.approx(jaw_Y), P[i]
    lo, hi = AC.to_mesh(cad.mods["claw_jaw"].design()).bounds
    assert (lo[0], hi[0], lo[1], hi[1]) == pytest.approx((C.X_P0, C.X_TIP, C.RACK_Y[0], C.RACK_Y[1]), abs=0.01)
    assert hi[2] == pytest.approx(C.Z_TOP0, abs=0.01)
    # their half-widths: racks max(31.42 - g/2, 25.13 + g/2), necks 24 + g/2, roots 12 + g/2, tips 6 + g/2
    assert pc._part_y(2, 0, 0, 0) == pytest.approx((-C.RACK_Y[1], C.RACK_Y[1]), abs=0.01)
    assert pc._part_y(2, 0, 0, 22) == pytest.approx((-(22 - C.RACK_Y[0]), 22 - C.RACK_Y[0]), abs=0.01)
    assert [pc._part_y(k, 0, 0, 0)[1] for k in (3, 4, 5)] == [C.NECK_Y + C.NECK_FILLET, C.BLADE_T_ROOT, C.BLADE_T]
    assert np.isfinite(lo).all()


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
    assert pc.camera_above_tips((0, 90, -150, -30)) == pytest.approx(83.35 - 17.79)    # straight down: 65.6 mm
    assert pc.camera_above_tips((0, 0, 0, 0)) == pytest.approx(12 - 51)                # level: the camera hangs low
    assert pc.camera_above_tips((0, 45, -60, -30), gap=0) == pytest.approx(15.2, abs=0.1)   # pitch -45 (claw round 3)
    assert pc.camera_above_tips((0, 45, -60, -25), gap=0) < pc.CAMERA_ABOVE_MM             # pitch -40: too flat


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
    assert pc.crop_claw(frame).shape == (583, 1920, 3)        # CLAW_ROWS 0.46


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
    assert ("line", (0, 583), (1919, 583), (0, 165, 255)) in log      # the claw's 46 %, on the raw frame
    port.sent.clear()
    monkeypatch.setitem(sys.modules, "cv2", _fake_cv2(np, [ord("c")], log))
    pc.preview(arm, 0, "ccw", None, None)
    assert not [c for c in port.sent if c.startswith("h")]           # no width given: c doesn't squeeze
