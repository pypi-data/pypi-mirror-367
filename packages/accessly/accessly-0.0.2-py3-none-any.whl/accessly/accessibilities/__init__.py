# Dynamically imports all Python modules in accessibilities/

import importlib
import pkgutil

def load_all_accessibility_features():
    package = __name__  # 'accessly.accessibilities'
    for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
        if not is_pkg:
            importlib.import_module(f"{package}.{module_name}")
