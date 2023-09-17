from PySide2.QtCore import QObject, Signal

class Signals(QObject):
    get_datapackage_from_record = Signal(str)

    generate_db = Signal(list, dict, bool)

signals = Signals()
