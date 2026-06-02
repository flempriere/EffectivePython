# app.py
class Prefs:
    def get(self, name):
        return "Hello, World!"


prefs = Prefs()

import dialog  # noqa: E402

dialog.show()
