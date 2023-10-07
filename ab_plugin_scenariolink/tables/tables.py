"""
This module contains the table classes used in the ScenarioLink plugin.
"""
import webbrowser

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Slot
from PySide2.QtGui import QContextMenuEvent

from activity_browser.ui.tables.views import ABDataFrameView
from activity_browser.ui.tables.delegates import CheckboxDelegate

from .models import FoldsModel, DataPackageModel
from ..signals import signals

class FoldsTable(ABDataFrameView):
    """
    A table view class for displaying the Folds model data.

    This table allows for the selection of different scenarios
    and emits signals when a row is double-clicked.
    """

    def __init__(self, parent=None):
        """Initialize the FoldsTable."""
        super().__init__(parent)
        self.vis_columns = ['generator', 'generator version', 'creation date', 'scope',
                            'model', 'scenario', 'source database', 'downloaded']

        # Hide the vertical header and set the selection mode
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Set the size policy for the table
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum
        ))

        self.model = FoldsModel(parent=self)
        self._connect_signals()
        self.model.sync()

        # Specify the column index for the 'cached column' checkbox
        self.cached_col = self.model.df_columns['downloaded']
        self.setItemDelegateForColumn(self.cached_col, CheckboxDelegate(self))

        # only show the columns in self.vis_columns and present in the dataframe
        hide_cols = list(set(self.model.df_columns.keys()) - set(self.vis_columns))
        for col in hide_cols:
            self.setColumnHidden(self.model.df_columns[col], True)

    def _connect_signals(self):
        """Connect signals to slots."""
        self.doubleClicked.connect(self.row_selected)
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)
        self.model.updated.connect(self.update_col_width)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """ Have the parameter test to see if it can be deleted safely.
        """
        if self.indexAt(event.pos()).row() == -1:
            return
        if not self.model.df_columns.get('link', False):
            # the CSV with scenarios does not have a link
            return

        action = QtWidgets.QAction("Open dashboard in browser")
        action.triggered.connect(self.open_link)
        action.setToolTip('Open a dashboard with more information about this scenario in the browser')
        menu = QtWidgets.QMenu(self)
        menu.addAction(action)
        menu.exec_(event.globalPos())

    def update_col_width(self):
        self.resizeColumnsToContents()

    @Slot(QtCore.QModelIndex, name="row_selected")
    def row_selected(self, index) -> None:
        """Handle row selection and emit a signal with the selected record."""
        record = self.model.get_record(index)
        signals.get_datapackage_from_record.emit(record)

    def open_link(self):
        index = self.selectedIndexes()[0]
        webbrowser.open(self.model.get_link(index.row()))


class DataPackageTable(ABDataFrameView):
    """
    A table view class for displaying the DataPackage model data.

    This table shows the details of datapackages and allows for
    selection to include them in further operations.
    """

    def __init__(self, parent=None):
        """Initialize the DataPackageTable."""
        super().__init__(parent)

        # Hide the vertical header and set the selection mode
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Specify the column index for the 'include' checkbox
        self.include_col = 0
        self.setItemDelegateForColumn(self.include_col, CheckboxDelegate(self))

        self.model = DataPackageModel(parent=self)
        self._connect_signals()
        self.model.sync()

    def _connect_signals(self):
        """Connect signals to slots."""
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)
        self.model.updated.connect(lambda: signals.record_ready.emit(True))
        self.model.updated.connect(self.update_col_width)

    def update_col_width(self):
        self.resizeColumnsToContents()

    def contextMenuEvent(self, event) -> None:
        if self.indexAt(event.pos()).row() == -1:
            return

        menu = QtWidgets.QMenu(self)
        if all(self.model.include):
            menu.addAction("Uncheck all", lambda: self.un_check_all(False))
        elif not all(self.model.include):
            menu.addAction("Check all", lambda: self.un_check_all(True))
        if any(self.model.include) and not all(self.model.include):
            # this includes check all
            menu.addAction("Uncheck all", lambda: self.un_check_all(False))
        menu.exec_(event.globalPos())

    def un_check_all(self, state):
        """Check or uncheck all scenario checkboxes.

        State True represents check all scenarios
        State False represents uncheck all scenarios"""
        self.model.include = [state for _ in self.model.include]
        self.model.sync()

        # manage the state of the import button and SDF checkbox
        signals.no_or_1_scenario_selected.emit(not state)
        signals.no_scenario_selected.emit(not state)

    def mousePressEvent(self, e):
        """
        Handle mouse click events.

        A single left mouse click in the 'include' column will toggle the checkbox value.
        """
        if e.button() == QtCore.Qt.LeftButton:
            proxy = self.indexAt(e.pos())
            if proxy.column() == self.include_col:
                # Flip the value for the 'include' checkbox
                new_value = not bool(proxy.data())

                new_includes = self.model.include[:]
                new_includes[proxy.row()] = new_value
                include_count = 0
                for truthy in new_includes:
                    if truthy:
                        include_count += 1
                if include_count == 0:
                    signals.no_scenario_selected.emit(True)
                elif include_count == 1:
                    signals.no_or_1_scenario_selected.emit(True)
                    signals.no_scenario_selected.emit(False)
                else:
                    signals.no_or_1_scenario_selected.emit(False)
                    signals.no_scenario_selected.emit(False)

                self.model.include = new_includes
                self.model.sync()

        super().mousePressEvent(e)
