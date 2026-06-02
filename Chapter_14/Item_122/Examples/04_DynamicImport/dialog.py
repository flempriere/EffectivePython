# dialog.py
class Dialog:
    def __init__(self):
        self.save_dir = None


save_dialog = Dialog()


def show():
    # move configuration into `show` as a dynamic import
    import app

    save_dialog.save_dir = app.prefs.get("save_dir")
    print(f"Dialog: saving to {save_dialog.save_dir}")
