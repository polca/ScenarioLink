from PySide2 import QtCore, QtWidgets

from ...tables.tables import FoldsTable
from ...signals import signals

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header

from .utils import download_files_from_zenodo

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.folds_table = FoldsTable(self)

        self.construct_layout()
        self._connect_signals()

    def _connect_signals(self):
        signals.get_datapackage_from_record.connect(self.get_datapackage)
        signals.downloading_label.connect(self.update_dl_label)

    def construct_layout(self) -> None:
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        # Header
        self.layout.addWidget(header(self.plugin.infos['name']))
        self.layout.addWidget(horizontal_line())

        # Folds table
        self.layout.addWidget(QtWidgets.QLabel('Doubleclick to open a Fold dataset (If not present locally, it will be downloaded)'))
        self.folds_table.setToolTip('Doubleclick to open a Fold dataset')
        self.layout.addWidget(self.folds_table)
        self.download_label = QtWidgets.QLabel('')
        self.layout.addWidget(self.download_label)
        self.layout.addWidget(horizontal_line())

        self.setLayout(self.layout)

    def get_datapackage(self, doi: str):
        dp = download_files_from_zenodo(doi)
        self.download_label.setText('')

        print(type(dp))

        return dp

    def update_dl_label(self):
        self.download_label.setText('Downloading Datapackage, this may take a while')