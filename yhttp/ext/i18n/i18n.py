import os
import uuid


class I18n:
    def configure(self, settings):
        self.settings = settings
        if not os.path.exists(settings.physical):
            os.mkdir(settings.physical)
