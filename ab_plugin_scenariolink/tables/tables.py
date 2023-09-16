from activity_browser.ui.tables.views import ABDataFrameView
from .models import FoldsModel
from ..signals import signals
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Slot


class FoldsTable(ABDataFrameView):
    """ Displays metadata for the databases found within the selected project.

    Databases can be read-only or writable, with users preference persisted
    in settings file.
    - User double-clicks to see the activities and flows within a db
    - A context menu (right click) provides further functionality
    """
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

    @Slot(QtCore.QModelIndex, name="getdoi")
    def row_selected(self, index):
        row = index.row()
        last_column_index = self.model.columnCount() - 1
        last_item_in_row = self.model.index(row, last_column_index)
        doi = self.model.get_doi(last_item_in_row)
        signals.get_fold_from_doi.emit(doi)

