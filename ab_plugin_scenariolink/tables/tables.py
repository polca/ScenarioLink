"""
This module contains the table classes used in the ScenarioLink plugin.
"""

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Slot

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

        # Hide the vertical header and set the selection mode
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        # Set the size policy for the table
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum
        ))

        self.model = FoldsModel(parent=self)
        self._connect_signals()
        self.model.sync()

    def _connect_signals(self):
        """Connect signals to slots."""
        self.doubleClicked.connect(self.row_selected)
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)

    @Slot(QtCore.QModelIndex, name="row_selected")
    def row_selected(self, index) -> None:
        """Handle row selection and emit a signal with the selected record."""
        record = self.model.get_record(index)
        signals.get_datapackage_from_record.emit(record)


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
        self.model.updated.connect(lambda: signals.record_ready.emit)

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
                    # If user tries to disable last remaining scenario, block them
                    return
                elif include_count == 1:
                    signals.block_sdf.emit(True)
                else:
                    signals.block_sdf.emit(False)

                self.model.include = new_includes
                self.model.sync()

        super().mousePressEvent(e)
