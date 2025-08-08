from accessly import register_feature
from accessly import config
import matplotlib.pyplot as plt

def apply(params):
    """
    Adds 'L' and 'R' labels to plots for distinguishing between the left and right side of the plot.
    Parameters:
        position (str): 'top' or 'bottom'
        alpha (float): label transparency (default: 1.0)
        color (str): label color (default: black)
        fontsize (int): font size (default: 14)
    """
    position = params if isinstance(params, str) else params.get("position", "top")
    alpha = params.get("alpha", 1.0)
    color = params.get("color", "black")
    fontsize = params.get("fontsize", 14)

    def add_lr_labels(*args, **kwargs):
        fig = plt.gcf()
        for ax in fig.axes:

            y_pos = 0.96 if position == "top" else 0.04
            va = "top" if position == "top" else "bottom"

            ax.text(0.01, y_pos, "L",
                    fontsize=fontsize, fontweight="bold", fontname="Arial",
                    color=color, alpha=alpha, ha="left", va=va,
                    transform=ax.transAxes, clip_on=False)

            ax.text(0.99, y_pos, "R",
                    fontsize=fontsize, fontweight="bold", fontname="Arial",
                    color=color, alpha=alpha, ha="right", va=va,
                    transform=ax.transAxes, clip_on=False)



    config.show_hooks.append(add_lr_labels)


register_feature("leftright", apply)
