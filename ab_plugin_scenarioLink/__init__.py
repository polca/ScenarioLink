import activity_browser as ab

from .layouts.tabs import RightTab

class Plugin(ab.Plugin):

    def __init__(self):
        infos = {
            'name': "ScenarioLink",
        }
        ab.Plugin.__init__(self, infos)

    def load(self):
        self.rightTab = RightTab(self)
        self.tabs = [self.rightTab]

    def close(self):
        return

    def remove(self):
        return