# Patch FigureManagerBase.show to save figure to file
import matplotlib.pyplot as plt
from matplotlib.backend_bases import FigureManagerBase
FigureManagerBase.show = lambda self: plt.savefig("output.png")
