from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt
import brightway2 as bw
from typing import List, Tuple

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header
from activity_browser.ui.widgets.dialog import DatabaseLinkingDialog
from activity_browser.signals import signals as ab_signals

from ...tables.tables import FoldsTable, DataPackageTable
from ...signals import signals
from ...utils import unfold_databases

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)

        self.layout = QtWidgets.QVBoxLayout()

        self.fold_chooser = FoldChooserWidget()
        self.scenario_chooser = ScenarioChooserWidget()

        self.construct_layout()
        self._connect_signals()

    def _connect_signals(self):
        signals.generate_db.connect(self.generate_database)
        signals.record_ready.connect(self.record_selected)

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

    def record_selected(self):
        print('RECORD SELECTED')

    def generate_database(self, include_scenarios, dependencies, as_sdf):
        if self.fold_chooser.use_table:
            record = self.fold_chooser.folds_table.model.selected_record

        # generate
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        unfold_databases(record, include_scenarios, dependencies, as_sdf)
        ab_signals.databases_changed.emit()
        QtWidgets.QApplication.restoreOverrideCursor()


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

        signals.block_sdf.connect(self.manage_sdf_state)

    def import_state(self):

        # convert the binary list to a list of indices that were selected
        include_scenarios = [i for i, state in enumerate(self.data_package_table.model.include) if state]

        dependencies = []
        for dependency in self.data_package_table.model.data_package.descriptor['dependencies']:
            dependencies.append(dependency['name'])
        dependencies = self.relink_database(dependencies)

        signals.generate_db.emit(include_scenarios, dependencies, self.sdf_check.isChecked())

    def relink_database(self, depends: list) -> dict:
        """Relink technosphere exchanges within the given Fold."""

        options = [(depend, bw.databases.list) for depend in depends]
        dialog = RelinkDialog.relink_scenario_link(options)
        relinked = {}
        if dialog.exec_() == RelinkDialog.Accepted:
            for old, new in dialog.relink.items():
                # Add the relinks
                relinked[old] = new
            for dep in depends:
                # Add any remaining DBs with the same name
                if dep not in relinked.keys():
                    relinked[dep] = dep
            return relinked

    def manage_sdf_state(self, state: bool) -> None:
        if state:
            # block the SDF state
            self.sdf_check.setChecked(False)
            self.sdf_check.setEnabled(False)
        else:
            self.sdf_check.setEnabled(True)


class RelinkDialog(DatabaseLinkingDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    @classmethod
    def relink_scenario_link(cls, options: List[Tuple[str, List[str]]],
                     parent=None) -> 'RelinkDialog':
        label = "Choose the ScenarioLink databases."
        return cls.construct_dialog(label, options, parent)

