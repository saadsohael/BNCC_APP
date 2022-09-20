from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import dataHandler
from kivy.core.window import Window

Window.size = (300, 500)

dataHandler.create_primary_app_data()

under_login_screen = ["AdminDash", "CadetDash", "ApplicationWindow"]
under_admin_dash = ["CadetsInfoScreen", "AdminProfile"]
under_cadet_dash = []
common_screens = ["NoticeScreen", "AboutScreen", "SettingsScreen"]


class WindowManager(ScreenManager):
    pass


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)

    def _key_handler(self, instance, key, *args):
        if key is 27:
            if self.manager.current != "LoginScreen":
                self.go_back()
            else:
                exit()
            return True

    def log_in_btn(self):
        if self.ids.login_label.text == "Admin Login":
            if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
                self.manager.current = "AdminDash"
                self.ids.username_textfield.text = ''
                self.ids.password_textfield.text = ''

    def go_back(self):
        if self.manager.current in under_login_screen:
            self.manager.current = "LoginScreen"
        elif self.manager.current in under_admin_dash:
            self.manager.current = "AdminDash"
        elif self.manager.current in under_cadet_dash:
            self.manager.current = "CadetDash"
        elif self.manager.current in common_screens:
            if self.ids.login_label.text == "Admin Login":
                self.manager.current = "AdminDash"
            else:
                self.manager.current = "CadetDash"


class AdminDash(Screen):
    pass


class CadetDash(Screen):
    pass


class ApplicationWindow(Screen):
    pass


class AdminProfile(Screen):
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
        content = dataHandler.query_primary_app_data()[0]
        if content == "Light":
            dataHandler.update_primary_app_data('theme_color', 'Dark')
            app.update_theme()
        else:
            dataHandler.update_primary_app_data('theme_color', 'Light')
            app.update_theme()


class MainApp(MDApp):

    def build(self):
        self.title = "App By SIS"
        self.theme_cls.primary_palette = "Green"
        content = dataHandler.query_primary_app_data()[0]
        self.theme_cls.theme_style = content
        kvFile = Builder.load_file("app_design.kv")
        return kvFile

    def update_theme(self):
        content = dataHandler.query_primary_app_data()[0]
        self.theme_cls.theme_style = content


MainApp().run()
