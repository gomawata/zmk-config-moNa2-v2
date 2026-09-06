from pathlib import Path
import re
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_YAML = ROOT / "build.yaml"
COROPIT_CONF = ROOT / "config" / "coropit.conf"


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
    args = target.get("cmake-args", "")
    match = re.search(r"-DEXTRA_CONF_FILE=([^\s]+)", args)
    return Path(match.group(1)).name if match else None


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
            relative = arg.split("=", 1)[1]
            # Model the ../../config path from a virtual ZMK application directory.
            workspace = ROOT
            selected = (workspace / "zmk" / "app" / relative).resolve()
            expected_prefix = workspace / "config"
            local = expected_prefix / selected.relative_to(expected_prefix)
            if not local.is_file():
                raise FileNotFoundError(local)
            values.update(_config_values(local))
    return values


class CoropitConfigTest(unittest.TestCase):
    def test_coropit_target_is_dedicated_and_other_right_targets_stay_separate(self):
        coropit = _target("mona2_r-coropit")
        stock = _target("mona2_r-pmw3610")
        paw3222 = _target("mona2_r-paw3222")

        self.assertEqual(coropit["board"], "xiao_ble/nrf52840/zmk")
        self.assertEqual(coropit["shield"], "mona2_r rgbled_adapter")
        self.assertEqual(coropit["snippet"], "studio-rpc-usb-uart")
        self.assertEqual(_extra_conf_name(coropit), "coropit.conf")

        self.assertIsNone(_extra_conf_name(stock))
        self.assertEqual(stock["artifact-name"], "mona2_r-pmw3610")
        self.assertEqual(_extra_conf_name(paw3222), "paw3222.conf")
        self.assertIn("EXTRA_DTC_OVERLAY_FILE=../../config/paw3222.overlay", paw3222["cmake-args"])
        self.assertNotIn("coropit.conf", paw3222["cmake-args"])

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


if __name__ == "__main__":
    unittest.main()
