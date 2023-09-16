import activity_browser as ab

from .layouts.tabs import LeftTab, RightTab

class Plugin(ab.Plugin):

    def __init__(self):
        infos = {
            'name': "Template",
        }
        ab.Plugin.__init__(self, infos)

    def load(self):
        self.rightTab = RightTab(self)
        self.leftTab = LeftTab(self)
        self.tabs = [self.rightTab, self.leftTab]

    def close(self):
        return

    def remove(self):
        return