import matplotlib.pyplot as plt
from . import config
from .accessibilities import load_all_accessibility_features

_original_show = plt.show
_loaded_accessibilities = False

def configure(**kwargs):
    """
    Called by the user to enable accessibility features.

    Example:
        configure(colorblind="deuteranopia")
    """
    global _loaded_accessibilities

    if not _loaded_accessibilities:
        load_all_accessibility_features()  # auto-import modules
        _loaded_accessibilities = True
        
    # make sure we can run accessly.configure() to reset/disable accessibility features in ipynb notebooks
    config.show_hooks.clear() # removes all previously registered draw/save hooks
    config.settings.clear() # clears old flags
    # reapplying only features in kwargs ensures: 1. features you want are applied but 2. features you omit are disabled.

    config.settings.update(kwargs)

    for name, handler in config.registered_features.items():
        if name in kwargs and kwargs[name]:
            handler(kwargs[name])  # call apply function
            print(f"Calling handler for {name} with value: {kwargs[name]}")

    _monkey_patch_matplotlib()


def register_feature(name, handler_func):
    """
    Used by feature modules to register themselves.
    Example: register_feature("colorblind", apply)
    """
    config.registered_features[name] = handler_func

def _monkey_patch_matplotlib():
    def run_show_hooks(*args, **kwargs):
        for hook in config.show_hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                print(f"[accessly] Warning: show hook failed: {e}")

    # Patch plt.show()
    def patched_show(*args, **kwargs):
        run_show_hooks(*args, **kwargs)
        _original_show(*args, **kwargs)

    plt.show = patched_show

    # Patch plt.savefig()
    original_savefig = plt.savefig

    def patched_savefig(*args, **kwargs):
        run_show_hooks(*args, **kwargs)
        return original_savefig(*args, **kwargs)

    plt.savefig = patched_savefig
