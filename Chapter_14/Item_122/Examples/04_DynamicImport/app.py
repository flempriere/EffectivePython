# app.py
import dialog


class Prefs:
    def get(self, name):
        return "Hello, World!"


prefs = Prefs()
dialog.show()
