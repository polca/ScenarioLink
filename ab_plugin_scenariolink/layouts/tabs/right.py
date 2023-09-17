from PySide2 import QtCore, QtWidgets

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header

from ...tables.tables import FoldsTable, DataPackageTable

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)

        self.layout = QtWidgets.QVBoxLayout()

        self.fold_chooser = FoldChooserWidget()
        self.scenario_chooser = ScenarioChooserWidget()

        self.construct_layout()
        self._connect_signals()

    def _connect_signals(self):
        pass

    def construct_layout(self) -> None:
        """Construct the panel layout"""
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        # Header
        self.layout.addWidget(header(self.plugin.infos['name']))
        self.layout.addWidget(horizontal_line())

        # Folds chooser
        self.layout.addWidget(self.fold_chooser)
        self.layout.addWidget(horizontal_line())

        # Scenario Chooser
        self.layout.addWidget(self.scenario_chooser)
        self.layout.addWidget(horizontal_line())

        self.layout.addStretch()

        self.setLayout(self.layout)


class FoldChooserWidget(QtWidgets.QWidget):
    def __init__(self):
        super(FoldChooserWidget, self).__init__()
        self.folds_table = FoldsTable(self)

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(QtWidgets.QLabel('Doubleclick to open a Fold dataset (If not present locally, it will be downloaded)'))
        self.folds_table.setToolTip('Doubleclick to open a Fold dataset')
        self.layout.addWidget(self.folds_table)

        self.setLayout(self.layout)

    def update_dl_label(self):
        print('++ DL label should be updated')
        self.download_label.setText('Downloading Datapackage, this may take a while')

    def reset_dl_label(self):
        self.download_label.setText('')


class ScenarioChooserWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ScenarioChooserWidget, self).__init__()

        self.data_package_table = DataPackageTable(self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.data_package_table)
        self.setLayout(self.layout)
