# Validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/test_coropit_config.py
git diff --check
```

These checks validate source configuration selection; they do not compile ZMK.
Use `.github/workflows/build.yml` on the target branch for firmware build verification.
Hardware checks require the matching physical keyboard and sensor.
