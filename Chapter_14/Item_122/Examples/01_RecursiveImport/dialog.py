# dialog.py
import app


class Dialog:
    def __init__(self, save_dir):
        self.save_dir = save_dir


save_dialog = Dialog(app.prefs.get("save_dir"))


def show():
    print(f"Dialog: saving to {save_dialog.save_dir}")
