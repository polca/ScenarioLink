from PySide2.QtCore import QObject, Signal

class Signals(QObject):
    get_datapackage_from_record = Signal(str)
    record_ready = Signal(bool)

    generate_db = Signal(list, dict, bool)
    block_sdf = Signal(bool)

signals = Signals()
