from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager


class FileExplorer(MDApp):
    def __init__(self, **kwargs):
        super(FileExplorer, self).__init__(**kwargs)
        self.file
    def build(self):
        pass


if __name__ == "__main__":
    FileExplorer().run()
