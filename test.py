"""from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.screenmanager import ScreenManager, Screen


class WindowManager(ScreenManager):
    pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.file_explorer = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.exit_file_explorer,
            preview=True,
        )

    def select_path(self, path):
        print(path)
        self.exit_file_explorer()

    def exit_file_explorer(self):
        self.file_explorer.close()

    def open_file_explorer(self):
        self.file_explorer.show('/')


class TestApp(MDApp):
    def build(self):
        kvFile = Builder.load_file("test.kv")
        return kvFile


TestApp().run()
"""
import dataHandler

# print([v for v in dataHandler.query_app_data('*', "cadet_application_data", "Cadet_Password", "FI9XISqQ")[0] if v not in ["FI9XISqQ", 'Cadet']])
# print(dataHandler.query_app_data('Profile_Photo', 'cadet_application_data', 'Cadet_Password', "FI9XISqQ")[0][0])
print([' '.join(v.split("_")) for v in dataHandler.query_cadet_col_name() if v != "Cadet_Password"])