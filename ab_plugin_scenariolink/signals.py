from PySide2.QtCore import QObject, Signal


class Signals(QObject):
    get_datapackage_from_record = Signal(str)

    downloading_label = Signal()

signals = Signals()