from PySide2 import QtCore, QtWidgets

from ...tables.tables import FoldsTable
from ...signals import signals

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header

from .utils import download_files_from_zenodo

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)

        self.folds_table = FoldsTable(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addWidget(header(plugin.infos['name']))
        self.layout.addWidget(horizontal_line())
        self.layout.addWidget(self.folds_table)
        self.setLayout(self.layout)

        self._connect_signals()

    def _connect_signals(self):
        signals.get_datapackage_from_record.connect(self.get_datapackage)

    def get_datapackage(self, doi: str):

        dp = download_files_from_zenodo(doi)

        print(type(dp))

        return dp