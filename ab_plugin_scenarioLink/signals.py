
from PySide2.QtCore import QObject, Signal


class Signals(QObject):
    get_fold_from_doi = Signal(str)


signals = Signals()