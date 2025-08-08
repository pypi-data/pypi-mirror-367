from accessly import register_feature, config
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pyfonts import load_google_font
import os

def apply(params):
    """
    Registers a font style accessibility hook that changes  plot
    text options, that may be useful for dyslexic or low-vision users.
    Parameters:
        font (str): selected font (default: "Atkinson Hyperlegible")
        weight (str): set font weight (default: bold)
    """

    lf_font = params if isinstance(params, str) else params.get("font", "Atkinson Hyperlegible")
    lf_weight = params.get("weight", "bold")
    if lf_weight not in ["normal", "bold"]:
        print("[LegibleFont] WARNING: Invalid text weight selected. Use normal or bold.")

    # color = params.get("color", "black")
    # fontsize = params.get("fontsize", 14)

    if isinstance(lf_font, list):
        lf_font = lf_font[0]
        print("[LegibleFont] WARNING: Expected single font. Only using first list entry")

    available_fonts_ext = [os.path.splitext(os.path.basename(i)) for i in fm.findSystemFonts(fontpaths=None, fontext='ttf')]
    available_fonts = [i[0] for i in available_fonts_ext]

    if lf_font not in available_fonts:
        try:
            #maybe it's a google font?
            g_font = load_google_font(lf_font, weight=lf_weight)
            fm.fontManager.addfont(g_font.get_file())
        except:
            #(it wasn't)
            print("[LegibleFont] WARNING: Selected ",lf_font, " but this font is not available!")

    def font_update_current_figure(*args, **kwargs):
        fig = plt.gcf()
        #use rcParams to set font of ALL text
        plt.rcParams["font.weight"] = lf_weight
        plt.rcParams["axes.labelweight"] = lf_weight

        #set font last, in case there are issues
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = lf_font

        print("[LegibleFont] Using font:",lf_font)
        print("[LegibleFont] Using weight:",lf_weight)

    config.show_hooks.append(font_update_current_figure)


# Register the feature with Accessly
register_feature("legiblefont", apply)