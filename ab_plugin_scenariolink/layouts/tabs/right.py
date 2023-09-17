from PySide2 import QtCore, QtWidgets

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header

from ...tables.tables import FoldsTable, DataPackageTable
from ...signals import signals

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

        self.layout = QtWidgets.QVBoxLayout()

        # Radio buttons to choose where to get Fold from
        self.radio_default = QtWidgets.QRadioButton('Default Folds')
        self.radio_default.setChecked(True)
        self.radio_custom = QtWidgets.QRadioButton('Custom Fold import')
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.radio_layout.addWidget(self.radio_default)
        self.radio_layout.addWidget(self.radio_custom)
        self.radio_layout.addStretch()
        self.radio_widget = QtWidgets.QWidget()
        self.radio_widget.setLayout(self.radio_layout)
        self.layout.addWidget(self.radio_widget)

        # Folds table
        self.table_label = QtWidgets.QLabel('Doubleclick to open a Fold dataset (If not present locally, it will be downloaded)')
        self.layout.addWidget(self.table_label)

        self.folds_table = FoldsTable(self)
        self.use_table = True  # bool to see if we need to read this table or instead read the local import
        self.folds_table.setToolTip('Doubleclick to open a Fold dataset')
        self.layout.addWidget(self.folds_table)

        # Fold custom importer
        self.custom = QtWidgets.QLabel('PLACEHOLDER')
        self.custom.setVisible(False)
        self.layout.addWidget(self.custom)

        self.setLayout(self.layout)

        self.radio_custom.toggled.connect(self.radio_toggled)

    def radio_toggled(self, toggled: bool) -> None:
        self.use_table = not toggled
        self.folds_table.setVisible(not toggled)
        self.table_label.setVisible(not toggled)

        self.custom.setVisible(toggled)

class ScenarioChooserWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ScenarioChooserWidget, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()

        # Datapackage table
        self.data_package_table = DataPackageTable(self)
        self.layout.addWidget(self.data_package_table)

        # SDF checker
        self.sdf_check = QtWidgets.QCheckBox('Produce Superstructure database')
        self.sdf_check.setToolTip('TODO explain what SDF is here')
        self.sdf_check.setChecked(False)
        self.layout.addWidget(self.sdf_check)

        # Import button
        self.import_b = QtWidgets.QPushButton('Import')
        self.import_layout = QtWidgets.QHBoxLayout()
        self.import_layout.addWidget(self.import_b)
        self.import_layout.addStretch()
        self.import_b_widg = QtWidgets.QWidget()
        self.import_b_widg.setLayout(self.import_layout)
        self.layout.addWidget(self.import_b_widg)
        self.import_b.clicked.connect(self.import_state)

        self.setLayout(self.layout)

    def import_state(self):

        # convert the binary list to a list of indices that were selected
        include_scenarios = [i for i, state in enumerate(self.data_package_table.model.include) if state]

        dependencies = {}
        for dependency in self.data_package_table.model.data_package.descriptor['dependencies']:




        print('++ include', include_scenarios)
        print('++ depends', dependencies)


        signals.import_state.emit(include_scenarios, self.sdf_check.isChecked())
