from PySide2.QtCore import QObject, Signal

class Signals(QObject):
    get_datapackage_from_record = Signal(str)

    import_state = Signal(list, bool)

signals = Signals()
