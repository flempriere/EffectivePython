# dialog.py
import app


class Dialog:
    def __init__(self):  # Remove the save_dir argument
        self.save_dir = None


save_dialog = Dialog()  # Create the dialog instance, but no access to `prefs` yet`


def show():
    print(f"Dialog: saving to {save_dialog.save_dir}")


# new configure method, defers use of the `app` module until `app` has finished importing
def configure():
    save_dialog.save_dir = app.prefs.get("save_dir")
