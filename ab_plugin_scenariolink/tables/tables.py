from activity_browser.ui.tables.views import ABDataFrameView
from activity_browser.ui.tables.delegates import CheckboxDelegate
from .models import FoldsModel, DataPackageModel
from ..signals import signals
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Slot


class FoldsTable(ABDataFrameView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum
        ))

        self.model = FoldsModel(parent=self)
        self._connect_signals()
        self.model.sync()

    def _connect_signals(self):
        self.doubleClicked.connect(self.row_selected)
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)

    @Slot(QtCore.QModelIndex, name="row_selected")
    def row_selected(self, index):
        doi = self.model.get_record(index)
        signals.get_datapackage_from_record.emit(doi)

class DataPackageTable(ABDataFrameView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.include_col = 0
        self.setItemDelegateForColumn(self.include_col, CheckboxDelegate(self))

        self.model = DataPackageModel(parent=self)
        self._connect_signals()
        self.model.sync()

    def _connect_signals(self):
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)
        signals.get_datapackage_from_record.connect(self.model.get_datapackage)

    def mousePressEvent(self, e):
        """ A single mouseclick should trigger the 'include' column to alter
        its value.
        """
        if e.button() == QtCore.Qt.LeftButton:
            proxy = self.indexAt(e.pos())
            if proxy.column() == self.include_col:
                # Flip the read-only value for the database
                new_value = not bool(proxy.data())
                self.model.include[proxy.row()] = new_value
                self.model.sync()
        super().mousePressEvent(e)

