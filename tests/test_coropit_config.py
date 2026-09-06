from pathlib import Path
import re
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_YAML = ROOT / "build.yaml"
COROPIT_CONF = ROOT / "config" / "coropit.conf"
MONA2_R_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_r.overlay"
PAW3222_OVERLAY = ROOT / "config" / "paw3222.overlay"
KEYMAP = ROOT / "config" / "mona2.keymap"


def _yaml_value(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _build_targets():
    targets = []
    current = None
    for line in BUILD_YAML.read_text(encoding="utf-8").splitlines():
        if line.startswith("  - board:"):
            if current is not None:
                targets.append(current)
            current = {"board": _yaml_value(line.split(":", 1)[1])}
            continue
        if current is None:
            continue
        match = re.match(r"^    ([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current[match.group(1)] = _yaml_value(match.group(2))
    if current is not None:
        targets.append(current)
    return targets


def _target(artifact_name):
    return next(
        target
        for target in _build_targets()
        if target.get("artifact-name") == artifact_name
    )


def _extra_conf_name(target):
    selected = _selected_source_path(target, "EXTRA_CONF_FILE")
    return selected.name if selected else None


def _selected_source_path(target, cmake_variable):
    args = target.get("cmake-args", "")
    match = re.search(rf"-D{re.escape(cmake_variable)}=([^\s]+)", args)
    if not match:
        return None

    relative = match.group(1)
    # Model the ../../config path from a virtual ZMK application directory.
    workspace = ROOT
    selected = (workspace / "zmk" / "app" / relative).resolve()
    expected_prefix = workspace / "config"
    try:
        local = expected_prefix / selected.relative_to(expected_prefix)
    except ValueError as exc:
        raise ValueError(f"{cmake_variable} path escapes config: {relative}") from exc
    if not local.is_file():
        raise FileNotFoundError(local)
    return local


def _config_values(path):
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or not line.startswith("CONFIG_"):
            continue
        name, value = line.split("=", 1)
        values[name] = value
    return values


def _source_assignments(target):
    # This merges source assignments, not evaluated Kconfig defaults/dependencies.
    values = _config_values(ROOT / "config" / "mona2_r.conf")
    for arg in shlex.split(target.get("cmake-args", "")):
        if arg.startswith("-DEXTRA_CONF_FILE="):
            local = _selected_source_path(target, "EXTRA_CONF_FILE")
            values.update(_config_values(local))
    return values


def _layer_bindings(layer_name):
    source = KEYMAP.read_text(encoding="utf-8")
    match = re.search(
        rf"{re.escape(layer_name)}\s*\{{.*?bindings\s*=\s*<(?P<body>.*?)>;",
        source,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"layer not found: {layer_name}")
    return re.findall(r"&[^&\s]+(?:\s+(?!&)[^&\s]+)*", match.group("body"))


class CoropitConfigTest(unittest.TestCase):
    def test_mac_thumb_bindings_and_win_layer_baseline(self):
        mac = _layer_bindings("mac_layer")
        self.assertEqual(len(mac), 42)
        self.assertEqual(mac[36:39], ["&lt 3 LANG2", "&lt 5 SPACE", "&lt 7 LANG1"])

        self.assertEqual(
            _layer_bindings("win_layer"),
            [
                "&kp Q", "&kp W", "&kp E", "&kp R", "&kp T", "&kp Y",
                "&kp U", "&kp I", "&kp O", "&kp P", "&kp A", "&kp S",
                "&kp D", "&kp F", "&kp G", "&kp F13", "&kp H", "&kp J",
                "&kp K", "&kp L", "&kp SEMICOLON", "&mt LEFT_SHIFT Z",
                "&kp X", "&kp C", "&kp V", "&kp B", "&kp F14", "&kp F15",
                "&kp N", "&kp M", "&kp COMMA", "&kp DOT", "&kp SLASH",
                "&kp LCTRL", "&kp LEFT_WIN", "&kp F16", "&kp BACKSPACE",
                "&lt 2 ENTER", "&lt_to_layer_0 3 LANG2", "&lt_to_layer_0 3 LANG1",
                "&lt 1 SPACE", "&kp LEFT_ALT",
            ],
        )

    def test_coropit_target_is_dedicated_and_other_right_targets_stay_separate(self):
        coropit = _target("mona2_r-coropit")
        stock = _target("mona2_r-pmw3610")
        paw3222 = _target("mona2_r-paw3222")

        self.assertEqual(coropit["board"], "xiao_ble/nrf52840/zmk")
        self.assertEqual(coropit["shield"], "mona2_r rgbled_adapter")
        self.assertEqual(coropit["snippet"], "studio-rpc-usb-uart")
        self.assertEqual(_extra_conf_name(coropit), "coropit.conf")
        self.assertEqual(
            _selected_source_path(coropit, "EXTRA_DTC_OVERLAY_FILE"),
            ROOT / "config" / "coropit.overlay",
        )

        self.assertIsNone(_extra_conf_name(stock))
        self.assertIsNone(_selected_source_path(stock, "EXTRA_DTC_OVERLAY_FILE"))
        self.assertEqual(stock["artifact-name"], "mona2_r-pmw3610")
        self.assertEqual(_extra_conf_name(paw3222), "paw3222.conf")
        self.assertEqual(
            _selected_source_path(paw3222, "EXTRA_DTC_OVERLAY_FILE"),
            PAW3222_OVERLAY,
        )
        self.assertIn("EXTRA_DTC_OVERLAY_FILE=../../config/paw3222.overlay", paw3222["cmake-args"])
        self.assertNotIn("coropit.conf", paw3222["cmake-args"])

    def test_selected_overlays_preserve_sensor_properties(self):
        coropit_overlay = _selected_source_path(
            _target("mona2_r-coropit"), "EXTRA_DTC_OVERLAY_FILE"
        )
        self.assertRegex(
            coropit_overlay.read_text(encoding="utf-8"),
            r"&trackball_central\s*\{\s*cpi\s*=\s*<3200>;\s*\}",
        )

        self.assertIn("cpi = <600>;", MONA2_R_OVERLAY.read_text(encoding="utf-8"))
        self.assertIn(
            "/delete-property/ cpi;",
            PAW3222_OVERLAY.read_text(encoding="utf-8"),
        )

    def test_actual_source_assignments_preserve_stock_and_sensor_variants(self):
        coropit_config = _source_assignments(_target("mona2_r-coropit"))
        stock_config = _source_assignments(_target("mona2_r-pmw3610"))
        paw3222_config = _source_assignments(_target("mona2_r-paw3222"))

        self.assertEqual(coropit_config["CONFIG_PMW3610_INVERT_X"], "y")
        self.assertEqual(coropit_config["CONFIG_PMW3610_INVERT_Y"], "n")
        self.assertEqual(coropit_config["CONFIG_PMW3610_SWAP_XY"], "n")
        self.assertEqual(coropit_config["CONFIG_ZMK_STUDIO"], "y")
        self.assertEqual(stock_config["CONFIG_PMW3610_INVERT_X"], "y")
        self.assertEqual(paw3222_config["CONFIG_TRACKBALL_PAW3222"], "y")
        self.assertEqual(paw3222_config["CONFIG_PM_DEVICE_RUNTIME"], "n")
        for assignments in (stock_config, paw3222_config):
            self.assertNotIn("CONFIG_PMW3610_INVERT_Y", assignments)
            self.assertNotIn("CONFIG_PMW3610_SWAP_XY", assignments)
        self.assertNotIn("CONFIG_TRACKBALL_PAW3222", coropit_config)
        self.assertNotIn("CONFIG_TRACKBALL_PAW3222", stock_config)

    def test_invalid_selected_extra_conf_path_is_rejected(self):
        target = dict(_target("mona2_r-coropit"))
        target["cmake-args"] = "-DEXTRA_CONF_FILE=../wrong/coropit.conf"
        with self.assertRaises((ValueError, FileNotFoundError)):
            _source_assignments(target)

    def test_invalid_or_missing_selected_extra_overlay_path_is_rejected(self):
        bad_target = dict(_target("mona2_r-coropit"))
        bad_target["cmake-args"] = "-DEXTRA_DTC_OVERLAY_FILE=../wrong/coropit.overlay"
        with self.assertRaises(ValueError):
            _selected_source_path(bad_target, "EXTRA_DTC_OVERLAY_FILE")

        missing_target = dict(_target("mona2_r-coropit"))
        missing_target["cmake-args"] = "-DEXTRA_DTC_OVERLAY_FILE=../../config/missing.overlay"
        with self.assertRaises(FileNotFoundError):
            _selected_source_path(missing_target, "EXTRA_DTC_OVERLAY_FILE")


if __name__ == "__main__":
    unittest.main()
