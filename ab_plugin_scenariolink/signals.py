from PySide2.QtCore import QObject, Signal

class Signals(QObject):
    get_datapackage_from_record = Signal(str)  # Get this datapackage from a record (Zenodo or cache)
    get_datapackage_from_disk = Signal(str)  # Get a datapackage from disk (sends path)
    record_ready = Signal(bool)  # datapackage extraction is complete and scenarios table should be shown

    generate_db = Signal(list, dict, bool, object, object)  # Generate database from selected scenario data

    no_or_1_scenario_selected = Signal(bool)  # True when no or one scenarios are selected
    no_scenario_selected = Signal(bool)  # True when no scenario is selected

signals = Signals()
