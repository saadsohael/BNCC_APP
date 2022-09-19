from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import dataHandler
from kivy.core.window import Window

Window.size = (300, 500)


class WindowManager(ScreenManager):
    pass


class LoginScreen(Screen):
    def log_in_btn(self):
        if self.ids.login_label.text == "Admin Login":
            if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
                self.manager.current = "AdminDash"
                self.ids.username_textfield.text = ''
                self.ids.password_textfield.text = ''


class AdminDash(Screen):
    pass


class CadetDash(Screen):
    pass


class CadetsInfoScreen(Screen):
    pass


class NoticeScreen(Screen):
    pass


class AboutScreen(Screen):
    pass


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def change_theme(self):
        app = MainApp()
        # theme_style = app.theme_cls.theme_style
        # if theme_style == "Dark":
        #     theme_style = "Light"
        # else:
        #     theme_style = "Dark"
        with open("color.txt", "r") as clr_file:
            content = clr_file.read()
        if content == "Light":
            with open("color.txt", "w") as clr_file:
                clr_file.write("Dark")
            app.update_theme()
        else:
            with open("color.txt", "w") as clr_file:
                clr_file.write("Light")
            app.update_theme()


class MainApp(MDApp):

    def build(self):
        self.title = "App By SIS"
        self.theme_cls.primary_palette = "Green"
        with open("color.txt", "r") as clr_file:
            content = clr_file.read()
        self.theme_cls.theme_style = content
        kvFile = Builder.load_file("app_design.kv")
        return kvFile

    def update_theme(self):
        with open("color.txt", "r") as clr_file:
            content = clr_file.read()
        self.theme_cls.theme_style = content


MainApp().run()
