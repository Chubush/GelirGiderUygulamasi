from PyQt5 import uic
with open("panel.py","w",encoding="utf8") as fout:
    uic.compileUi("panel.ui",fout)
    