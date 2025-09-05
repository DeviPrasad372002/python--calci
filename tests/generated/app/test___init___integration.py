import importlib, importlib.util, pathlib, sys
_MODULE_PATH = pathlib.Path(r'/home/runner/work/tech-demo/tech-demo/target-repo/app/__init__.py').resolve()
# Discover package root by walking up while __init__.py exists
_pkg_parts = []
_p = _MODULE_PATH.parent
while (_p / '__init__.py').exists():
    _pkg_parts.insert(0, _p.name)
    _parent = _p.parent
    if _parent == _p:
        break
    _p = _parent
_root_dir = _p
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_module_name = '.'.join(_pkg_parts + [_MODULE_PATH.stem]) if _pkg_parts else _MODULE_PATH.stem

def _load_target():
    try:
        return importlib.import_module(_module_name)
    except Exception:
        spec = importlib.util.spec_from_file_location('target_module', _MODULE_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

def test_import_target_module():
    mod = _load_target()
    assert mod is not None
