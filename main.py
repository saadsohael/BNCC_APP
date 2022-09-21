from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.metrics import sp

import dataHandler
from kivy.core.window import Window

Window.size = (300, 500)

dataHandler.create_app_data()  # create static (on device memory) and dynamic (online ) app data

under_login_screen = ["AdminDash", "CadetDash", "ApplicationWindow"]
under_admin_dash = ["CadetsInfoScreen", "AdminProfile"]
under_cadet_dash = []
common_screens = ["NoticeScreen", "AboutScreen", "SettingsScreen"]


class WindowManager(ScreenManager):
    pass


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)  # bind screen with keyboard or touch input

    # handles keyboard/ touch input!
    def _key_handler(self, instance, key, *args):

        if key is 27:
            # if current screen is login screen or any screen under login screen the confirmation window will be shown!
            if self.manager.current == "LoginScreen":
                self.open_dialog('Are you sure you want to exit?')

            elif self.manager.current in under_login_screen:

                if self.manager.current == "ApplicationWindow":
                    self.open_dialog('All input info will be empty if you go back!\n  Are you sure?')

                else:
                    self.open_dialog('Are you sure you want to go back?\n  You will be logged out!')

            # otherwise current screen will be replaced with previous screen
            else:
                self.go_back()

            return True

    # if user confirms to go back or exit!
    def confirm_yes(self, instance):

        if self.manager.current == "LoginScreen":
            exit()

        elif self.manager.current in under_login_screen:
            self.manager.current = "LoginScreen"
            self.dialog.dismiss()

    def open_dialog(self, title):  # opens dialog box to confirm action

        self.dialog = MDDialog(title=title,
                               size_hint=(None, None),
                               width=(self.width - sp(50)),
                               buttons=[MDFlatButton(text='Yes', on_release=self.confirm_yes),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def log_in_btn(self):

        if self.ids.login_label.text == "Admin Login":
            if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
                self.manager.current = "AdminDash"
                self.ids.username_textfield.text = ''
                self.ids.password_textfield.text = ''

    def go_back(self):

        # fetch previous_screens
        if self.manager.current in under_admin_dash:
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

    def __init__(self, **kwargs):
        super(ApplicationWindow, self).__init__(**kwargs)

    # create an application form window with the items in the dynamic (online) database

    def create_form(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])

        for v in form_items:
            label = MDLabel(text=v, size_hint_x=0.55)
            textfield = MDTextField(mode="rectangle")

            self.ids.application_form.add_widget(label)
            self.ids.application_form.add_widget(textfield)


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

    # change app theme when button is pressed!

    def change_theme(self):

        app = MainApp()
        theme_color = dataHandler.query_app_data("static_app_data")[0]

        if theme_color == "Light":
            dataHandler.update_app_data("static_app_data", 'theme_color', 'Dark')
            app.update_theme()

        else:
            dataHandler.update_app_data("static_app_data", 'theme_color', 'Light')
            app.update_theme()


class MainApp(MDApp):

    def build(self):
        self.title = "App By SIS"
        self.theme_cls.primary_palette = "Green"
        theme_color = dataHandler.query_app_data("static_app_data")[0]
        self.theme_cls.theme_style = theme_color
        kvFile = Builder.load_file("app_design.kv")
        return kvFile

    def update_theme(self):
        theme_color = dataHandler.query_app_data("static_app_data")[0]
        self.theme_cls.theme_style = theme_color


MainApp().run()
