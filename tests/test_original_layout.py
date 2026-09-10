import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYMAP = ROOT / "config" / "mona2.keymap"
FIXTURE = ROOT / "tests" / "fixtures" / "old-main.keymap"
RIGHT_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_r.overlay"
LEFT_OVERLAY = ROOT / "boards" / "shields" / "mona2" / "mona2_l.overlay"
DTSI = ROOT / "boards" / "shields" / "mona2" / "mona2.dtsi"
BUILD = ROOT / "build.yaml"
SOURCE_SHA256 = "adfcddcf616d63021b3a818f0aad10ebeb40b1a86a2926e1ad8f23588dd85348"
PMW3610_MAX_CPI = 3200


def layer_bindings(keymap: str, layer_name: str) -> list[str]:
    match = re.search(
        rf"(?ms)^        {re.escape(layer_name)} \{{.*?^            bindings = <\n(.*?)^            >;",
        keymap,
    )
    if match is None:
        raise AssertionError(f"missing binding block for {layer_name}")
    bindings = match.group(1)
    starts = list(re.finditer(r"&[A-Za-z_][A-Za-z0-9_]*", bindings))
    return [
        " ".join(bindings[start.start() : starts[index + 1].start() if index + 1 < len(starts) else len(bindings)].split())
        for index, start in enumerate(starts)
    ]


class OriginalMacLayoutTests(unittest.TestCase):
    def test_keymap_is_the_checked_in_original_source(self) -> None:
        fixture = FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(fixture).hexdigest(), SOURCE_SHA256)
        self.assertEqual(KEYMAP.read_bytes(), fixture)

    def test_original_has_four_42_key_layers_in_original_order(self) -> None:
        keymap = KEYMAP.read_text()
        layer_names = re.findall(r"(?m)^        (Maclayer|layer_1|layer_3|layer_4) \{$", keymap)
        self.assertEqual(layer_names, ["Maclayer", "layer_1", "layer_3", "layer_4"])
        for layer_name in layer_names:
            self.assertEqual(len(layer_bindings(keymap, layer_name)), 42, layer_name)

    def test_mac_layer_keeps_right_side_editing_and_mouse_positions(self) -> None:
        bindings = layer_bindings(KEYMAP.read_text(), "Maclayer")
        self.assertEqual(bindings[30], "&mkp MB1")
        self.assertEqual(bindings[31], "&mkp MB2")
        self.assertEqual(bindings[39], "&kp BACKSPACE")
        self.assertEqual(bindings[40], "&lt 2 ENTER")

    def test_original_sensor_assignments_are_preserved(self) -> None:
        keymap = KEYMAP.read_text()
        maclayer = re.search(r"(?ms)^        Maclayer \{(.*?)^        \};", keymap)
        self.assertIsNotNone(maclayer)
        self.assertIn("<&scroll_up_down>,\n                <&inc_dec_kp C_VOL_DN C_VOL_UP>", maclayer.group(1))
        self.assertEqual(keymap.count("sensor-bindings = <&scroll_up_down>;"), 3)

    def test_right_trackball_has_no_bluetooth_layer_scroller_or_auto_layer(self) -> None:
        overlay = RIGHT_OVERLAY.read_text()
        dtsi_without_comments = re.sub(r"//.*", "", DTSI.read_text())
        self.assertIn("status = \"okay\";\n    device = <&trackball_central>;", overlay)
        self.assertNotIn("scroller {", overlay)
        self.assertNotRegex(overlay, r"layers\s*=\s*<3>")
        self.assertNotIn("zip_xy_to_scroll_mapper", overlay)
        self.assertNotIn("zip_temp_layer", dtsi_without_comments)

    def test_v2_matrix_and_coropit_settings_remain_at_maximum_cpi(self) -> None:
        overlay = RIGHT_OVERLAY.read_text()
        left_overlay = LEFT_OVERLAY.read_text()
        dtsi = DTSI.read_text()
        build = BUILD.read_text()
        self.assertIn("board: seeeduino_xiao_ble", build)
        self.assertIn("shield: mona2_r rgbled_adapter", build)
        self.assertIn("shield: mona2_l rgbled_adapter", build)
        self.assertIn('compatible = "pixart,pmw3610";', overlay)
        self.assertIn('compatible = "nordic,nrf-spim";', overlay)
        self.assertIn("cs-gpios = <&gpio0 9 GPIO_ACTIVE_LOW>;", overlay)
        self.assertIn("irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;", overlay)
        self.assertIn(f"cpi = <{PMW3610_MAX_CPI}>;", overlay)
        self.assertNotIn("cpi = <600>;", overlay)
        self.assertIn("invert-x;", overlay)
        self.assertIn("invert-y;", overlay)
        self.assertIn("columns = <11>;", dtsi)
        self.assertIn("rows = <4>;", dtsi)
        for pin in ("<&xiao_d 1", "<&xiao_d 2", "<&xiao_d 3", "<&xiao_d 6"):
            self.assertIn(pin, dtsi)
        for pin in ("<&xiao_d 10", "<&xiao_d 9", "<&xiao_d 8", "<&xiao_d 7", "<&gpio0 10"):
            self.assertIn(pin, overlay)
        self.assertIn("&left_encoder {\n    status = \"okay\";", left_overlay)
        self.assertIn("<&gpio0 9 GPIO_ACTIVE_HIGH>", left_overlay)


if __name__ == "__main__":
    unittest.main()
