import os
import sys
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import setupLogging
import window

# def SaveFigureAsImage(fileName,fig=None,**kwargs):
#     fig_size = fig.get_size_inches()
#     w,h = fig_size[0], fig_size[1]
#     fig.patch.set_alpha(0)
#     if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
#         w,h = kwargs['orig_size']
#         w2,h2 = fig_size[0],fig_size[1]
#         fig.set_size_inches([(w2/w)*w,(w2/w)*h])
#         fig.set_dpi((w2/w)*fig.get_dpi())
#     a=fig.gca()
#     a.set_frame_on(False)
#     a.set_xticks([]); a.set_yticks([])
#     plt.axis('off')
#     plt.xlim(0,h); plt.ylim(w,0)
#     fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)

# def SaveFigureAsImage(fileName,fig=None):
#     fig_size = fig.get_size_inches()
#     w,h = fig_size[0], fig_size[1]
#     fig.patch.set_alpha(0)
#     a=fig.gca()
#     a.set_frame_on(False)
#     a.set_xticks([]); a.set_yticks([])
#     plt.axis('off')
#     plt.xlim(0,h); plt.ylim(w,0)
#     fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)

def run():
    setupLogging.setupLogging()
    app = window.QtGui.QApplication(sys.argv)
    sshFile="./stylesheet/darkOrange.stylesheet"
    with open(sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    app.setStyleSheet(window.qdarkstyle.load_stylesheet_pyqt())
    _GUI = window.Window()
    sys.exit(app.exec_())

run()
