import hashlib
from pathlib import Path
import re
import shlex
from typing import Optional
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_YAML = ROOT / "build.yaml"
KEYMAP = ROOT / "config" / "mona2.keymap"
FIXTURE = ROOT / "tests" / "fixtures" / "old-main.keymap"
COROPIT_CONF = ROOT / "config" / "coropit.conf"
COROPIT_OVERLAY = ROOT / "config" / "coropit.overlay"
MONA2_R_CONF = ROOT / "config" / "mona2_r.conf"
MONA2_R_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_r.overlay"
MONA2_L_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_l.overlay"
MONA2_DTSI = ROOT / "boards" / "shields" / "mona2" / "mona2.dtsi"
PAW3222_OVERLAY = ROOT / "config" / "paw3222.overlay"
README = ROOT / "README.md"

SOURCE_SHA256 = "adfcddcf616d63021b3a818f0aad10ebeb40b1a86a2926e1ad8f23588dd85348"
SOURCE_KEYMAP_SHA256 = (
    "b8db582ba23740735a1561105a0677cf"
    "847a941d6d4c79ac6224d1ab6add4bb6"
)
LAYERS = ("Maclayer", "layer_1", "layer_3", "layer_4")
ALLOWED_BINDING_DIFFS = {
    "Maclayer": {15: "&kp LC(LS(NUMBER_4))"},
    "layer_3": {
        3: "&kp LG(LC(V))",
        4: "&kp LC(LA(LG(T)))",
        5: "&kp LC(LA(LG(LEFT_ARROW)))",
        6: "&kp LC(LA(LG(F)))",
        7: "&kp LC(LA(LG(RIGHT_ARROW)))",
        8: "&kp LC(LA(LG(C)))",
        9: "&kp LC(LA(LG(R)))",
        25: "&kp LC(LA(LG(B)))",
    },
}


def _layer_bindings(keymap: str, layer_name: str) -> list[str]:
    match = re.search(
        rf"(?ms)^        {re.escape(layer_name)} \{{.*?^            bindings = <\n(.*?)^            >;",
        keymap,
    )
    if match is None:
        raise AssertionError(f"missing binding block for {layer_name}")
    body = match.group(1)
    starts = list(re.finditer(r"&[A-Za-z_][A-Za-z0-9_]*", body))
    return [
        " ".join(body[start.start(): starts[index + 1].start() if index + 1 < len(starts) else len(body)].split())
        for index, start in enumerate(starts)
    ]


def _sensor_bindings(keymap: str, layer_name: str) -> str:
    match = re.search(
        rf"(?ms)^        {re.escape(layer_name)} \{{(.*?)^        \}};",
        keymap,
    )
    if match is None:
        raise AssertionError(f"missing layer block for {layer_name}")
    sensor = re.search(r"sensor-bindings\s*=\s*(.*?);", match.group(1), re.DOTALL)
    if sensor is None:
        raise AssertionError(f"missing sensor bindings for {layer_name}")
    return " ".join(sensor.group(1).split())


def _keymap_layer_names(keymap: str) -> list[str]:
    match = re.search(r"(?ms)^    keymap\s*\{(?P<body>.*)^    \};$", keymap)
    if match is None:
        raise AssertionError("missing keymap block")
    return re.findall(r"(?m)^        ([A-Za-z_][A-Za-z0-9_]*) \{$", match.group("body"))


def _node_block(keymap: str, header: str, indentation: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(indentation)}{re.escape(header)}\s*\{{.*?^{re.escape(indentation)}\}};",
        keymap,
    )
    if match is None:
        raise AssertionError(f"missing node block: {header}")
    return " ".join(match.group(0).split())


def _define_value(keymap: str, name: str) -> str:
    match = re.search(rf"(?m)^#define {re.escape(name)}\s+(.+)$", keymap)
    if match is None:
        raise AssertionError(f"missing define: {name}")
    return match.group(1).strip()


def _yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _build_targets() -> list[dict[str, str]]:
    targets = []
    current = None
    for line in BUILD_YAML.read_text(encoding="utf-8").splitlines():
        if line.startswith("  - board:"):
            if current is not None:
                targets.append(current)
            current = {"board": _yaml_value(line.split(":", 1)[1])}
        elif current is not None:
            match = re.match(r"^    ([A-Za-z0-9_-]+):\s*(.*)$", line)
            if match:
                current[match.group(1)] = _yaml_value(match.group(2))
    if current is not None:
        targets.append(current)
    return targets


def _target(artifact_name: str) -> dict[str, str]:
    return next(target for target in _build_targets() if target.get("artifact-name") == artifact_name)


def _selected_source_path(target: dict[str, str], cmake_variable: str) -> Optional[Path]:
    match = re.search(rf"-D{re.escape(cmake_variable)}=([^\s]+)", target.get("cmake-args", ""))
    if match is None:
        return None
    selected = (ROOT / "zmk" / "app" / match.group(1)).resolve()
    config_root = ROOT / "config"
    try:
        local = config_root / selected.relative_to(config_root)
    except ValueError as exc:
        raise ValueError(f"{cmake_variable} path escapes config") from exc
    if not local.is_file():
        raise FileNotFoundError(local)
    return local


def _config_values(path: Path) -> dict[str, str]:
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line.startswith("CONFIG_"):
            name, value = line.split("=", 1)
            values[name] = value
    return values


def _source_assignments(target: dict[str, str]) -> dict[str, str]:
    values = _config_values(MONA2_R_CONF)
    for arg in shlex.split(target.get("cmake-args", "")):
        if arg.startswith("-DEXTRA_CONF_FILE="):
            extra = _selected_source_path(target, "EXTRA_CONF_FILE")
            assert extra is not None
            values.update(_config_values(extra))
    return values


class CoropitConfigTest(unittest.TestCase):
    def test_fixture_is_the_unchanged_old_mac_source(self) -> None:
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), SOURCE_SHA256)

    def test_current_keymap_matches_the_verified_four_layer_source(self) -> None:
        self.assertEqual(hashlib.sha256(KEYMAP.read_bytes()).hexdigest(), SOURCE_KEYMAP_SHA256)

    def _assert_old_layout_contract(self, source: str) -> None:
        fixture = FIXTURE.read_text(encoding="utf-8")
        self.assertEqual(_keymap_layer_names(source), list(LAYERS))
        for layer_name in LAYERS:
            actual = _layer_bindings(source, layer_name)
            original = _layer_bindings(fixture, layer_name)
            self.assertEqual(len(actual), 42, layer_name)
            self.assertEqual(len(original), 42, layer_name)
            for position, (before, after) in enumerate(zip(original, actual)):
                expected = ALLOWED_BINDING_DIFFS.get(layer_name, {}).get(position, before)
                self.assertEqual(after, expected, f"{layer_name} position {position}")
            self.assertEqual(_sensor_bindings(source, layer_name), _sensor_bindings(fixture, layer_name))

        # These definitions are outside individual layer bindings but determine
        # the old tap-hold timing and encoder scroll behavior.
        self.assertEqual(_node_block(source, "&mt", ""), _node_block(fixture, "&mt", ""))
        self.assertEqual(
            _node_block(source, "to_layer_0: to_layer_0", "        "),
            _node_block(fixture, "to_layer_0: to_layer_0", "        "),
        )
        self.assertEqual(
            _node_block(source, "lt_to_layer_0: lt_to_layer_0", "        "),
            _node_block(fixture, "lt_to_layer_0: lt_to_layer_0", "        "),
        )
        self.assertEqual(
            _node_block(source, "scroll_up_down: behavior_sensor_rotate_mouse_wheel_up_down", "        "),
            _node_block(fixture, "scroll_up_down: behavior_sensor_rotate_mouse_wheel_up_down", "        "),
        )
        self.assertEqual(
            _define_value(source, "ZMK_POINTING_DEFAULT_SCRL_VAL"),
            _define_value(fixture, "ZMK_POINTING_DEFAULT_SCRL_VAL"),
        )

    def test_four_layers_keep_all_old_bindings_except_approved_diffs(self) -> None:
        self._assert_old_layout_contract(KEYMAP.read_text(encoding="utf-8"))

    def test_layout_contract_rejects_an_extra_layer(self) -> None:
        source = KEYMAP.read_text(encoding="utf-8")
        extra_layer = """        unexpected_layer {
            bindings = <
&trans &trans &trans &trans &trans &trans &trans &trans &trans &trans
&trans &trans &trans &trans &trans &trans &trans &trans &trans &trans &trans
&trans &trans &trans &trans &trans &trans &trans &trans &trans &trans &trans &trans
&trans &trans &trans &trans &trans &trans &trans &trans &trans
            >;
            sensor-bindings = <&scroll_up_down>;
        };

"""
        changed = source.replace("        layer_4 {", extra_layer + "        layer_4 {", 1)
        with self.assertRaises(AssertionError):
            self._assert_old_layout_contract(changed)

    def test_layout_contract_rejects_tap_hold_or_sensor_behavior_mutation(self) -> None:
        source = KEYMAP.read_text(encoding="utf-8")
        changed = source.replace("tapping-term-ms = <300>;", "tapping-term-ms = <999>;", 1)
        with self.assertRaises(AssertionError):
            self._assert_old_layout_contract(changed)
        changed = source.replace("tap-ms = <20>;", "tap-ms = <99>;", 1)
        with self.assertRaises(AssertionError):
            self._assert_old_layout_contract(changed)

    def test_approved_shortcuts_and_hold_paths_are_exact(self) -> None:
        source = KEYMAP.read_text(encoding="utf-8")
        mac = _layer_bindings(source, "Maclayer")
        number = _layer_bindings(source, "layer_1")
        editing = _layer_bindings(source, "layer_3")
        settings = _layer_bindings(source, "layer_4")
        self.assertEqual(mac[35], "&kp F13")
        self.assertEqual(mac[37:41], ["&lt 2 SPACE", "&lt 1 LANGUAGE_1", "&kp BACKSPACE", "&lt 2 ENTER"])
        self.assertEqual(number[14], "&kp LS(LC(NUMBER_4))")
        self.assertEqual(editing[3:10], [
            "&kp LG(LC(V))", "&kp LC(LA(LG(T)))", "&kp LC(LA(LG(LEFT_ARROW)))",
            "&kp LC(LA(LG(F)))", "&kp LC(LA(LG(RIGHT_ARROW)))",
            "&kp LC(LA(LG(C)))", "&kp LC(LA(LG(R)))",
        ])
        self.assertEqual(editing[25], "&kp LC(LA(LG(B)))")
        self.assertEqual(settings[27], "&bootloader")
        self.assertNotIn("at_and_slash", source)
        self.assertNotIn("#define MOUSE", source)
        self.assertNotIn("#define SCROLL", source)

    def test_coropit_target_uses_modern_board_and_sensor_settings(self) -> None:
        coropit = _target("mona2_r-coropit")
        self.assertEqual(coropit["board"], "xiao_ble/nrf52840/zmk")
        self.assertEqual(coropit["shield"], "mona2_r rgbled_adapter")
        self.assertEqual(coropit["snippet"], "studio-rpc-usb-uart")
        self.assertEqual(_selected_source_path(coropit, "EXTRA_CONF_FILE"), COROPIT_CONF)
        self.assertEqual(_selected_source_path(coropit, "EXTRA_DTC_OVERLAY_FILE"), COROPIT_OVERLAY)
        coropit_config = _source_assignments(coropit)
        self.assertEqual(coropit_config["CONFIG_PMW3610_INVERT_X"], "y")
        self.assertEqual(coropit_config["CONFIG_PMW3610_INVERT_Y"], "n")
        self.assertEqual(coropit_config["CONFIG_PMW3610_SWAP_XY"], "n")
        self.assertRegex(COROPIT_OVERLAY.read_text(encoding="utf-8"), r"cpi\s*=\s*<1600>;")

    def test_other_right_sensor_targets_remain_separate(self) -> None:
        stock = _target("mona2_r-pmw3610")
        paw3222 = _target("mona2_r-paw3222")
        self.assertEqual(stock["board"], "xiao_ble/nrf52840/zmk")
        self.assertIsNone(_selected_source_path(stock, "EXTRA_CONF_FILE"))
        self.assertEqual(_selected_source_path(paw3222, "EXTRA_DTC_OVERLAY_FILE"), PAW3222_OVERLAY)
        self.assertIn("/delete-property/ cpi;", PAW3222_OVERLAY.read_text(encoding="utf-8"))
        self.assertIn("cpi = <600>;", MONA2_R_OVERLAY.read_text(encoding="utf-8"))
        stock_config = _source_assignments(stock)
        paw3222_config = _source_assignments(paw3222)
        self.assertEqual(stock_config["CONFIG_PMW3610_INVERT_X"], "y")
        self.assertEqual(paw3222_config["CONFIG_TRACKBALL_PAW3222"], "y")
        self.assertEqual(paw3222_config["CONFIG_PM_DEVICE_RUNTIME"], "n")
        for assignments in (stock_config, paw3222_config):
            self.assertNotIn("CONFIG_PMW3610_INVERT_Y", assignments)
            self.assertNotIn("CONFIG_PMW3610_SWAP_XY", assignments)

    def test_studio_and_hardware_base_remain_without_new_layer_paths(self) -> None:
        values = _config_values(MONA2_R_CONF)
        self.assertEqual(values["CONFIG_ZMK_STUDIO"], "y")
        self.assertEqual(values["CONFIG_ZMK_RUNTIME_INPUT_PROCESSOR"], "y")
        self.assertEqual(values["CONFIG_ZMK_RUNTIME_SENSOR_ROTATE"], "y")
        for name in values:
            self.assertFalse(name.startswith("CONFIG_ZMK_DEFAULT_LAYER_MIN_INDEX"), name)
            self.assertFalse(name.startswith("CONFIG_ZMK_DEFAULT_LAYER_MAX_INDEX"), name)
            self.assertFalse(name.startswith("CONFIG_ZMK_DEFAULT_LAYER_STUDIO_RPC"), name)
        self.assertEqual(values["CONFIG_ZMK_DEFAULT_LAYER"], "n")
        self.assertEqual(values["CONFIG_ZMK_OS_DETECTION"], "y")
        self.assertEqual(values["CONFIG_ZMK_MOUSE_GESTURE_RPC"], "n")
        self.assertFalse(any(name.startswith("CONFIG_ZMK_OS_DETECTION_LAYER_") for name in values))
        overlay = MONA2_R_OVERLAY.read_text(encoding="utf-8")
        self.assertIn('compatible = "cormoran,pmw3610";', overlay)
        self.assertIn("input-processors = <&mouse_runtime_input_processor &zip_scroll_scaler 1 100>;", overlay)
        self.assertNotIn("scroll_runtime_input_processor", overlay)
        self.assertNotIn("mouse_gesture", overlay)
        self.assertNotIn("inertial_scroll", overlay)
        self.assertNotIn("temp-layer", COROPIT_OVERLAY.read_text(encoding="utf-8"))
        self.assertIn("&left_encoder {\n    status = \"okay\";", MONA2_L_OVERLAY.read_text(encoding="utf-8"))
        dtsi = MONA2_DTSI.read_text(encoding="utf-8")
        self.assertIn("columns = <11>;", dtsi)
        self.assertIn("rows = <4>;", dtsi)
        for pin in ("<&xiao_d 1", "<&xiao_d 2", "<&xiao_d 3", "<&xiao_d 6"):
            self.assertIn(pin, dtsi)

    def test_readme_matches_four_layer_mac_configuration(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("| 0 | `Maclayer` |", readme)
        self.assertIn("| 1 | `layer_1` |", readme)
        self.assertIn("| 2 | `layer_3` |", readme)
        self.assertIn("| 3 | `layer_4` |", readme)
        self.assertIn("AquaVoice", readme)
        self.assertIn("Restore Stock Settings", readme)
        self.assertIn("Runtime Input Processorのマウス設定は残ることがあります。", readme)
        self.assertIn("更新後、使い始める前にDYA Studioでmouseの一時レイヤーと`xy-to-scroll`が無効であることを確認し、必要なら無効にして保存してください。", readme)
        self.assertIn("右側を再起動して", readme)
        self.assertIn("`AUTO_MOUSE`、Windows配列、OS別デフォルトレイヤーはありません。", readme)
        self.assertNotIn("SETTINGS_W", readme)

    def test_invalid_extra_paths_are_rejected(self) -> None:
        bad = dict(_target("mona2_r-coropit"))
        bad["cmake-args"] = "-DEXTRA_CONF_FILE=../wrong/coropit.conf"
        with self.assertRaises((ValueError, FileNotFoundError)):
            _source_assignments(bad)
        bad["cmake-args"] = "-DEXTRA_DTC_OVERLAY_FILE=../wrong/coropit.overlay"
        with self.assertRaises(ValueError):
            _selected_source_path(bad, "EXTRA_DTC_OVERLAY_FILE")
        bad["cmake-args"] = "-DEXTRA_DTC_OVERLAY_FILE=../../config/missing.overlay"
        with self.assertRaises(FileNotFoundError):
            _selected_source_path(bad, "EXTRA_DTC_OVERLAY_FILE")


if __name__ == "__main__":
    unittest.main()
