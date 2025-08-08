from accessly import register_feature, config
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, to_hex, to_rgba
from matplotlib import cm
import colorsys
from matplotlib.colors import Colormap
import hashlib
import numpy as np

def apply(cb_options):
    """
    Apply colorblind-safe remapping using specified colormaps.
    """
    cb_types = cb_options.get("types", []) if isinstance(cb_options, dict) else []
    if isinstance(cb_types, str):
        cb_types = [cb_types]

    colormap = _get_colormap(cb_types)
    print(f"[Colorblind] Using colormap: {colormap.name}")

    def recolor_current_figure(*args, **kwargs):
        fig = plt.gcf()
        for ax in fig.axes:
            # Lines
            for line in ax.get_lines():
                _try_recolor(line.set_color, line.get_color(), colormap)

            # Scatter: facecolors and edgecolors
            for col in ax.collections:
                try:
                    if hasattr(col, "get_facecolors"):
                        fc = col.get_facecolors()
                        if fc is not None and len(fc) > 0:
                            col.set_facecolors([
                                to_rgba(_map_to_colormap(c[:3], colormap), alpha=c[3]) for c in fc
                            ])
                    if hasattr(col, "get_edgecolors"):
                        ec = col.get_edgecolors()
                        if ec is not None and len(ec) > 0:
                            col.set_edgecolors([
                                to_rgba(_map_to_colormap(c[:3], colormap), alpha=c[3]) for c in ec
                            ])
                except Exception as e:
                    print(f"[Colorblind] Scatter recolor failed: {e}")

            # Bars / patches
            for patch in ax.patches:
                _try_recolor(patch.set_facecolor, patch.get_facecolor(), colormap)

            # Error bars, containers
            if hasattr(ax, "containers"):
                for container in ax.containers:
                    for artist in container:
                        if hasattr(artist, "get_facecolor"):
                            _try_recolor(artist.set_facecolor, artist.get_facecolor(), colormap)

            # Legend
            legend = ax.get_legend()
            if legend:
                try:
                    handles, labels = ax.get_legend_handles_labels()
                    for handle in handles:
                        if hasattr(handle, "get_color"):
                            _try_recolor(handle.set_color, handle.get_color(), colormap)
                        elif hasattr(handle, "get_facecolor"):
                            _try_recolor(handle.set_facecolor, handle.get_facecolor(), colormap)
                    
                    legend.remove()
                    ax.legend(handles, labels)
                except Exception as e:
                    print(f"[Colorblind] Legend recolor failed: {e}")

    config.show_hooks.append(recolor_current_figure)

# Truncate colormap helper
def _truncate_colormap(cmap: Colormap, minval=0.0, maxval=1.0, n=256):
    new_colors = cmap(np.linspace(minval, maxval, n))
    return cm.colors.ListedColormap(new_colors)

# Helper to determine the appropriate colormap
def _get_colormap(cb_types):
    if "redgreen" in cb_types:
        return cm.get_cmap("plasma")
    elif "blueyellow" in cb_types:
        return _truncate_colormap(cm.get_cmap("brg"), 0.5, 1.0)  # Right half only
    return cm.get_cmap("plasma")  # default

def _try_recolor(setter_func, color, colormap):
    try:
        hex_color = to_hex(color)

        if hex_color in _seen_colors:
            return

        rgb = to_rgb(color)
        new_hex = _map_to_colormap(rgb, colormap)
        _seen_colors.add(new_hex)

        if hex_color != new_hex:
            print(f"[Colorblind] Adjusted {hex_color} → {new_hex}")
        setter_func(new_hex)

    except Exception as e:
        print(f"[Colorblind] Recolor failed: {e}")


_seen_colors = set()

def _map_to_colormap(rgb, colormap):
    r, g, b = rgb
    hex_code = to_hex((r, g, b))

    # Hash RGB to a consistent scalar between 0–1
    hash_digest = hashlib.md5(hex_code.encode()).hexdigest()
    hash_int = int(hash_digest[:8], 16)
    norm = (hash_int % 1000000) / 1_000_000.0

    # Get RGB from colormap
    r_new, g_new, b_new, _ = colormap(norm)
    return to_hex((r_new, g_new, b_new))  # no prefix

# Register with accessly
register_feature("colorblind", apply)
