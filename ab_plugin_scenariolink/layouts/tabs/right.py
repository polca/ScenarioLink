from PySide2 import QtCore, QtWidgets
from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addWidget(header(plugin.infos['name']))
        self.layout.addWidget(horizontal_line())
        self.setLayout(self.layout)