import importlib.util, pathlib
_MODULE_PATH = pathlib.Path(r'/home/runner/work/tech-demo/tech-demo/target-repo/app/calculador.py').resolve()

def _load_target():
    spec = importlib.util.spec_from_file_location('target_module', _MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_import_target_module():
    mod = _load_target()
    assert mod is not None
