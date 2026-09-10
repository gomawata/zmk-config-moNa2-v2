from pathlib import Path
import re
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_YAML = ROOT / "build.yaml"
COROPIT_CONF = ROOT / "config" / "coropit.conf"
COROPIT_OVERLAY = ROOT / "config" / "coropit.overlay"
MONA2_R_CONF = ROOT / "config" / "mona2_r.conf"
MONA2_R_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_r.overlay"
PAW3222_OVERLAY = ROOT / "config" / "paw3222.overlay"
KEYMAP = ROOT / "config" / "mona2.keymap"
README = ROOT / "README.md"


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


def _layer_names():
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*\n\s*display-name\s*=",
        KEYMAP.read_text(encoding="utf-8"),
        re.MULTILINE,
    )


class CoropitConfigTest(unittest.TestCase):
    def test_apple_and_windows_base_layers_are_explicit(self):
        self.assertEqual(
            _layer_names(),
            [
                "apple_layer", "win_layer", "auto_mouse", "num_win", "num_mac",
                "mouse_win", "mouse_mac", "scroll_win", "scroll_mac", "function_win",
                "function_mac", "ble_win", "ble_mac",
            ],
        )

        apple = _layer_bindings("apple_layer")
        win = _layer_bindings("win_layer")
        self.assertEqual(len(apple), 42)
        self.assertEqual(len(win), 42)
        self.assertEqual(apple[33:36], ["&kp LCTRL", "&kp LEFT_GUI", "&kp LEFT_ALT"])
        self.assertEqual(win[33:36], ["&kp LCTRL", "&kp LEFT_WIN", "&kp LEFT_ALT"])
        self.assertEqual(apple[36:42], [
            "&lt 4 LANG2", "&lt 6 SPACE", "&lt 8 LANG1", "&kp ENTER",
            "&kp BACKSPACE", "&kp RIGHT_SHIFT",
        ])
        self.assertEqual(win[36:42], [
            "&lt 3 LANG2", "&lt 5 SPACE", "&lt 7 LANG1", "&kp ENTER",
            "&kp BACKSPACE", "&kp RIGHT_SHIFT",
        ])
        self.assertEqual(apple[20], "&lt 6 SEMICOLON")
        self.assertEqual(apple[32], "&lt 12 SLASH")
        self.assertEqual(win[32], "&lt 11 SLASH")
        self.assertEqual(apple[:20], win[:20])
        self.assertTrue(apple[20].endswith("SEMICOLON"))
        self.assertTrue(win[20].endswith("SEMICOLON"))
        self.assertEqual(apple[21:32], win[21:32])
        self.assertTrue(apple[32].endswith("SLASH"))
        self.assertTrue(win[32].endswith("SLASH"))

    def test_auto_mouse_is_low_priority_and_only_clicks_three_positions(self):
        auto = _layer_bindings("auto_mouse")
        self.assertEqual(len(auto), 42)
        self.assertEqual(auto[15], "&mkp MB1")
        self.assertEqual(auto[26:28], ["&mkp MB3", "&mkp MB2"])
        self.assertTrue(all(
            binding == "&trans"
            for position, binding in enumerate(auto)
            if position not in {15, 26, 27}
        ))
        source = KEYMAP.read_text(encoding="utf-8")
        self.assertIn("bindings = <&lt 2 ESC>;", source)

    def test_manual_layers_do_not_fall_through_to_auto_clicks(self):
        for layer_name in (
            "num_win", "num_mac", "mouse_win", "mouse_mac", "scroll_win", "scroll_mac",
            "ble_win", "ble_mac",
        ):
            bindings = _layer_bindings(layer_name)
            self.assertEqual(len(bindings), 42)
            for position in (15, 26, 27):
                self.assertNotEqual(
                    bindings[position], "&trans",
                    f"{layer_name} position {position} must mask AUTO_MOUSE",
                )
        self.assertEqual(_layer_bindings("ble_win"), _layer_bindings("ble_mac"))

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

    def test_coropit_enables_auto_mouse_and_scroll_mask_follows_layers(self):
        coropit_overlay = COROPIT_OVERLAY.read_text(encoding="utf-8")
        self.assertRegex(
            coropit_overlay,
            r"&mouse_runtime_input_processor\s*\{\s*temp-layer-enabled;\s*"
            r"temp-layer\s*=\s*<2>;\s*"
            r"temp-layer-activation-delay-ms\s*=\s*<100>;\s*"
            r"temp-layer-deactivation-delay-ms\s*=\s*<500>;\s*\}",
        )
        self.assertIn(
            "active-layers = <0x00000180>; /* layer7 + layer8 */",
            MONA2_R_OVERLAY.read_text(encoding="utf-8"),
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

    def test_settings_selects_endpoint_output_and_default_layer(self):
        source = KEYMAP.read_text(encoding="utf-8")
        self.assertIn("#include <behaviors/default_layer.dtsi>", source)
        self.assertIn("#include <dt-bindings/zmk_behavior_default_layer/default_layer.h>", source)
        self.assertEqual(_config_values(MONA2_R_CONF)["CONFIG_ZMK_DEFAULT_LAYER_OS_DETECTION"], "n")
        for profile in range(5):
            self.assertRegex(
                source,
                re.compile(
                    rf"BT{profile}: BT{profile}\s*\{{.*?"
                    rf"bindings\s*=\s*<&bt BT_SEL {profile} &out OUT_BLE>;",
                    re.DOTALL,
                ),
            )
        for settings_layer in ("ble_win", "ble_mac"):
            bindings = _layer_bindings(settings_layer)
            self.assertEqual(bindings[5:10], ["&BT0", "&BT1", "&BT2", "&BT3", "&BT4"])
            self.assertEqual(bindings[16:19], ["&df DF_SEL 0", "&df DF_SEL 1", "&out OUT_USB"])
            self.assertEqual(bindings[26:28], ["&kp COLON", "&bootloader"])

    def test_readme_documents_the_actual_initial_layers_and_controls(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("| 0 | APPLE |", readme)
        self.assertIn("| 1 | WIN |", readme)
        self.assertIn("| 2 | AUTO_MOUSE |", readme)
        self.assertIn("| 11 / 12 | SETTINGS_W / SETTINGS_A |", readme)
        self.assertIn("| 0 | `&lt 2 ESC` | 38, 39 |", readme)
        self.assertIn("入力がその端末へ届くのを確認してから `H` / `J`", readme)
        self.assertIn("最後の通常キー入力から 100 ms 経過後の最初のボール移動", readme)
        self.assertNotIn("`&lt 4 ESC` | 38, 39", readme)

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
