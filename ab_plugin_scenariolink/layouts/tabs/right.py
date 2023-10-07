from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt
import brightway2 as bw
from typing import List, Tuple
from unfold import Unfold

from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header
from activity_browser.ui.widgets.dialog import DatabaseLinkingDialog
from activity_browser.signals import signals as ab_signals

from ...tables.tables import FoldsTable, DataPackageTable
from ...signals import signals
from ...utils import unfold_databases, UpdateManager

class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)

        self.layout = QtWidgets.QVBoxLayout()

        self.fold_chooser = FoldChooserWidget()
        self.scenario_chooser = ScenarioChooserWidget()

        self.version_label = QtWidgets.QLabel('')

        self.construct_layout()
        self.version_check()
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

        # Scenario Chooser
        self.layout.addWidget(self.scenario_chooser)
        self.scenario_chooser.setVisible(False)

        self.layout.addStretch()

        self.layout.addWidget(self.version_label)

        self.setLayout(self.layout)

    def record_selected(self, state):
        self.scenario_chooser.setVisible(state)

    def generate_database(self, include_scenarios, dependencies, as_superstructure, superstructure_db_name):
        if self.fold_chooser.use_table:
            record = self.fold_chooser.folds_table.model.selected_record

        # generate
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        unfold_databases(record, include_scenarios, dependencies, as_superstructure, superstructure_db_name)
        ab_signals.databases_changed.emit()
        QtWidgets.QApplication.restoreOverrideCursor()

    def version_check(self) -> None:
        newer, current, latest = UpdateManager.get_versions()
        if newer:
            label = 'A newer version of ScenarioLink is available (your version: {}, the newest version: {})'\
                .format(current, latest)
            self.version_label.setText(label)


class FoldChooserWidget(QtWidgets.QWidget):
    def __init__(self):
        super(FoldChooserWidget, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()

        # label
        self.label = QtWidgets.QLabel('Select the datapackage you want to use')
        self.layout.addWidget(self.label)

        # Radio buttons to choose where to get Fold from
        self.radio_default = QtWidgets.QRadioButton('Online datapackages')
        self.radio_default.setChecked(True)
        self.radio_custom = QtWidgets.QRadioButton('Local datapackages')
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.radio_layout.addWidget(self.radio_default)
        self.radio_layout.addWidget(self.radio_custom)
        self.radio_layout.addStretch()
        self.radio_widget = QtWidgets.QWidget()
        self.radio_widget.setLayout(self.radio_layout)
        self.layout.addWidget(self.radio_widget)

        # Folds table
        self.table_label = QtWidgets.QLabel('Doubleclick to open a datapackage (if not present locally, it will be downloaded - this may take a while).')
        self.layout.addWidget(self.table_label)

        self.folds_table = FoldsTable(self)
        self.use_table = True  # bool to see if we need to read this table or instead read the local import
        if self.folds_table.model.df_columns.get('link', False):
            self.folds_table.setToolTip('Doubleclick to open a datapackage\n'
                                        'Right click to open a dashboard with more information')
        else:
            self.folds_table.setToolTip('Doubleclick to open a datapackage')
        self.layout.addWidget(self.folds_table)

        # Fold custom importer
        self.custom_layout = QtWidgets.QHBoxLayout()
        self.custom = QtWidgets.QPushButton('Browse computer')
        self.custom.setVisible(False)
        self.custom_layout.addWidget(self.custom)
        self.custom_layout.addStretch()
        self.custom_widg = QtWidgets.QWidget()
        self.custom_widg.setLayout(self.custom_layout)
        self.layout.addWidget(self.custom_widg)

        self.layout.addWidget(horizontal_line())
        self.setLayout(self.layout)

        self.radio_custom.toggled.connect(self.radio_toggled)
        self.custom.clicked.connect(lambda: signals.get_datapackage_from_disk.emit())

    def radio_toggled(self, toggled: bool) -> None:
        self.use_table = not toggled
        self.folds_table.setVisible(not toggled)
        self.table_label.setVisible(not toggled)

        self.custom.setVisible(toggled)
        signals.record_ready.emit(False)


class ScenarioChooserWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ScenarioChooserWidget, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()

        # Label
        self.label = QtWidgets.QLabel('Choose the scenarios you want to install')
        self.layout.addWidget(self.label)

        # Datapackage table
        self.data_package_table = DataPackageTable(self)
        self.layout.addWidget(self.data_package_table)

        # SDF checker
        self.sdf_check = QtWidgets.QCheckBox('Produce Superstructure database')
        self.sdf_check.setChecked(False)
        self.sdf_check.setEnabled(False)
        self.sdf_name_field = QtWidgets.QLineEdit()
        self.sdf_name_field.setPlaceholderText('Superstructure database name (optional)')
        self.sdf_name_field.setEnabled(False)
        self.sdf_layout = QtWidgets.QHBoxLayout()
        self.sdf_layout.addWidget(self.sdf_check)
        self.sdf_layout.addWidget(self.sdf_name_field)
        self.sdf_layout.addStretch()
        self.sdf_widget = QtWidgets.QWidget()
        self.sdf_widget.setToolTip('Instead of writing multiple databases per scenario,\n'
                                   'write one database and a scenario difference file')
        self.sdf_widget.setLayout(self.sdf_layout)
        self.layout.addWidget(self.sdf_widget)

        # Import button
        self.import_b = QtWidgets.QPushButton('Import')
        self.import_b.setEnabled(False)
        self.import_layout = QtWidgets.QHBoxLayout()
        self.import_layout.addWidget(self.import_b)
        self.import_layout.addStretch()
        self.clear_cache = QtWidgets.QPushButton('Clear unfold cache')
        self.clear_cache.setToolTip('Unfold caches some data to work faster, though sometimes this can store old data\n'
                                    'that should be renewed, clearing the cache allows new data to be cached.')
        self.import_layout.addWidget(self.clear_cache)
        self.import_b_widg = QtWidgets.QWidget()
        self.import_b_widg.setLayout(self.import_layout)
        self.layout.addWidget(self.import_b_widg)
        self.import_b.clicked.connect(self.import_state)
        self.clear_cache.clicked.connect(self.clear_unfold_cache)

        self.layout.addWidget(horizontal_line())
        self.setLayout(self.layout)

        signals.no_or_1_scenario_selected.connect(self.manage_sdf_state)
        signals.no_scenario_selected.connect(self.manage_import_button_state)

    def clear_unfold_cache(self):
        print('Clearing the unfold cache')
        Unfold.clear_existing_cache()

    def import_state(self):

        # convert the binary list to a list of indices that were selected
        include_scenarios = [i for i, state in enumerate(self.data_package_table.model.include) if state]

        dependencies = []
        for dependency in self.data_package_table.model.data_package.descriptor['dependencies']:
            dependencies.append(dependency['name'])
        dependencies = self.relink_database(dependencies)
        if not dependencies:
            return

        sdf_db = self.sdf_name_field.text()
        if sdf_db == '':
            sdf_db = None
        signals.generate_db.emit(
            include_scenarios,  # List of scenario indices to include
            dependencies,  # dict of dependency names (translated between datapackage and current bw project
            self.sdf_check.isChecked(),  # whether to make this into superstructure format
            sdf_db  # superstructure database name (str or None)
        )

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
        """Change SDF UI elements depending on whether >1 scenarios are selected."""
        if state:
            # block the SDF state
            self.sdf_check.setChecked(False)
        self.sdf_check.setEnabled(not state)
        self.sdf_name_field.setEnabled(not state)

    def manage_import_button_state(self, state: bool) -> None:
        """Change import button UI elements depending on whether >=1 scenarios are selected."""
        self.import_b.setEnabled(not state)


class RelinkDialog(DatabaseLinkingDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    @classmethod
    def relink_scenario_link(cls, options: List[Tuple[str, List[str]]],
                     parent=None) -> 'RelinkDialog':
        label = "Choose the ScenarioLink databases.\nBy clicking 'OK', you start the import."
        return cls.construct_dialog(label, options, parent)

