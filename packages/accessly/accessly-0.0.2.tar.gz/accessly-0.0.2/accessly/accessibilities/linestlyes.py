from accessly import register_feature, config
import matplotlib.pyplot as plt
import numpy as np
import colorsys
from matplotlib.colors import to_hex


def apply(line_options):
    """
    Registers a linestlye accessibility hook that restyles problematic
    plot elements before rendering.

    Args:
        line_options (dict): {
            "types": str or list of str
            Options:
                     'diff': changes all lines to different linestyles 
                            Important! Maximum of 14 styles used; otherwise throws error
                     'bold': changes all lines to bold
                     'recolor': changes all lines to uniform gradient of different colors 
                            Important! Do not combine with colorblind feature; will probably break the universe
                     'mono': changes all lines to black (use in conjunction w/diff option)
                            Important! Do not combine with colorblind feature; this is stupid.
        }
    """
    if not isinstance(line_options, dict):
        print("[Linestyles] WARNING: Expected dict, got", type(line_options))
        return

    line_type = line_options.get("types", [])

    def restyle_current_figure():
        fig = plt.gcf()
        for ax in fig.axes:
            # Lines
            lines = ax.get_lines()
            if len(lines) == 0:
                raise Exception("[Linestyles] No lines found")

            # Set the different linestyles depending on # of lines (max 14 styles)           
            if 'diff' in line_type:
                if len(lines) > 14:
                    raise Exception("[Linestyles] More than 14 lines found, unable to sufficiently differentiate using linestyles")
                elif len(lines) <= 4:
                    styles = ['solid', 'dotted', 'dashed', 'dashdot']
                else:
                    styles = [ 
                        'solid',
                        (0, (1, 10)),
                        (0, (1, 5)),
                        (0, (1, 1)),
                        (5, (10, 3)),
                        (0, (5, 10)),
                        (0, (5, 5)),
                        (0, (5, 1)),
                        (0, (3, 10, 1, 10)),
                        (0, (3, 5, 1, 5)),
                        (0, (3, 1, 1, 1)),
                        (0, (3, 5, 1, 5, 1, 5)),
                        (0, (3, 10, 1, 10, 1, 10)),
                        (0, (3, 1, 1, 1, 1, 1)),
                        ]

            # Make appropriate adjustments
            for line in lines:
                if 'bold' in line_type:
                    line.set_linewidth( 3 )
                if 'diff' in line_type:
                    idx = lines.index(line)
                    line.set_linestyle( styles[idx] )
                if 'mono' in line_type:
                    line.set_color( 'black' )
                if 'recolor' in line_type:
                    # Make a gradient of colors based on # of lines
                    idx = lines.index(line)
                    num_lines = len(lines)
                    hue = float(idx / num_lines)
                    r,g,b = colorsys.hls_to_rgb(hue, 0.5, 1.0)
                    hex_color = to_hex((r,g,b))
                    line.set_color( hex_color )
                
            # Legend
            legend = ax.get_legend()
            if legend:
                try:
                    handles, _ = ax.get_legend_handles_labels()
                    
                    props = {
                        "loc": getattr(legend, "_loc", "best"),
                        "frameon": legend.get_frame_on(),
                        "title": legend.get_title().get_text(),
                        "ncol": getattr(legend, "_ncol", 1),
                        "fontsize": legend.prop.get_size() if hasattr(legend, "prop") else None,
                    }
                    
                    legend.remove()
                    ax.legend(handles=handles, handlelength=7.5, **{k: v for k, v in props.items() if v is not None}, )
                    

                except Exception as e:
                    print(f"[Linestyles] Legend adjustment failed: {e}")
            

    config.show_hooks.append(restyle_current_figure)


# Register the colorblind feature with Accessly
register_feature("linestyles", apply)
