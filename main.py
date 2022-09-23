from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.metrics import sp

import dataHandler
from kivy.core.window import Window

Window.size = (300, 500)

dataHandler.create_app_data()  # create static (on device memory) and dynamic (online ) app data

under_login_screen = ["AdminDash", "CadetDash", "ApplyCadetScreen"]
under_admin_dash = ["ApplicationFormWindow", "CadetsInfoScreen", "AdminProfile", "EditFormWindow"]
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

        if key == 27:
            # if current screen is login screen or any screen under login screen the confirmation window will be shown!
            if self.manager.current == "LoginScreen":
                self.open_dialog('Are you sure you want to exit?')

            elif self.manager.current in under_login_screen:

                if self.manager.current == "ApplyCadetScreen":
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
            self.dialog.dismiss()
            self.manager.current = "LoginScreen"
            self.manager.transition.direction = 'right'

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

        # if self.ids.login_label.text == "Admin Login":
        #     if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
        #         self.manager.current = "AdminDash"
        #         self.ids.username_textfield.text = ''
        #         self.ids.password_textfield.text = ''
        if self.ids.login_label.text == "Admin Login":
            self.manager.current = "AdminDash"
        self.manager.get_screen("AdminDash").ids.nav_drawer.set_state("close")

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

        self.manager.transition.direction = 'right'


class ApplyCadetScreen(Screen):

    def __init__(self, **kwargs):
        super(ApplyCadetScreen, self).__init__(**kwargs)

    # create an application form window with the items in the dynamic (online) database

    def create_form(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])

        for v in form_items:
            label = MDLabel(text=v, size_hint_x=0.55)
            textfield = MDTextField(mode="rectangle")

            self.ids.application_form.add_widget(label)
            self.ids.application_form.add_widget(textfield)


class AdminDash(Screen):
    pass


class ApplicationFormWindow(Screen):

    def __init__(self, **kwargs):
        super(ApplicationFormWindow, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)  # bind screen with keyboard or touch input

    # handles keyboard/ touch input!
    def _key_handler(self, instance, key, *args):

        if key == 27:
            self.ids.edit_application_form.clear_widgets()

    def show_form(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])
        for v in form_items:
            text = ' '.join([i for i in v.split(" ") if i != ':'])
            label = MDLabel(text=text, size_hint_x=0.55, halign="center", valign='middle')
            self.ids.edit_application_form.add_widget(label)


class EditFormWindow(Screen):

    def __init__(self, **kwargs):
        super(EditFormWindow, self).__init__(**kwargs)
        self.form_items_names = []

        for v in eval(dataHandler.query_app_data("dynamic_app_data")[0]):
            self.form_items_names.append(' '.join([i for i in v.split(" ") if i != ':']))

    def change_texts(self):

        if self.ids.add_toggle_btn.state == 'down':

            self.ids.item_name_label.text = 'Item Name : '
            self.ids.item_name_input.hint_text = 'type item name...'
            self.ids.item_place_label.text = 'Place at : '
            self.ids.drop_item.text = "At Top"

        elif self.ids.edit_toggle_btn.state == 'down':

            self.ids.item_name_label.text = 'Item New Name : '
            self.ids.item_name_input.hint_text = 'type item new name...'
            self.ids.item_place_label.text = 'Choose Item To Edit : '
            self.ids.drop_item.text = self.form_items_names[0]

    def dropdown_(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])
        form_items.pop()
        form_items.insert(0, 'At Top')
        form_items.append('At Bottom')
        item_list = []
        for v in form_items:
            if form_items.index(v) != 0 and form_items.index(v) != (len(form_items) - 1):
                if self.ids.add_toggle_btn.state == 'down':
                    item_list.append('After ' + ' '.join([i for i in v.split(" ") if i != ':']))
                elif self.ids.edit_toggle_btn.state == 'down':
                    item_list.append(' '.join([i for i in v.split(" ") if i != ':']))
            else:
                item_list.append(' '.join([i for i in v.split(" ") if i != ':']))

        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": v,
                "height": sp(40),
                "on_release": lambda x=v: self.selected_item(x)
            } for v in item_list
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=self.menu_list,
            position="auto",
            width_mult=6
        )
        self.menu.open()

    def selected_item(self, item):
        self.ids.drop_item.text = item

    def add_item(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])
        input_text = self.ids.item_name_input.text.split(" ")
        item_name = ' '.join(list(map(lambda x: x.lower().capitalize(), input_text)))
        if not self.empty_textField(item_name):
            if (item_name + ' : ') not in form_items:
                if self.ids.drop_item.text == "At Top":
                    form_items.insert(0, item_name + ' : ')
                elif self.ids.drop_item.text == "At Bottom":
                    form_items.append(item_name + ' : ')
                else:
                    place_item = ' '.join([v for v in self.ids.drop_item.text.split(" ") if v != "After"])
                    index_ = form_items.index(place_item + ': ') + 1
                    form_items.insert(index_, f'{item_name} : ')
                dataHandler.update_app_data("dynamic_app_data", "application_form", repr(form_items))

                self.form_items_names.clear()
                for v in eval(dataHandler.query_app_data("dynamic_app_data")[0]):
                    self.form_items_names.append(' '.join([i for i in v.split(" ") if i != ':']))
                self.ids.item_name_input.text = ''
                self.ids.drop_item.text = 'At Top'

            else:
                print('item already in the form!')
        else:
            print("type a valid item name please!")

    def edit_item(self):
        if not self.empty_textField(self.ids.item_name_input.text):
            for v in self.form_items_names:
                if self.ids.drop_item.text == v:
                    index = self.form_items_names.index(v)
                    self.form_items_names.insert(index, self.ids.item_name_input.text)
                    self.form_items_names.remove(self.form_items_names[index + 1])
            new_form_items = [f'{v} : ' for v in self.form_items_names]
            dataHandler.update_app_data("dynamic_app_data", "application_form", repr(new_form_items))
        else:
            print("enter a valid name!")

    def empty_textField(self, textField_text):

        textField = textField_text.split(' ')

        if not ''.join(textField).isalpha():
            return True


class AdminProfile(Screen):
    pass


class CadetsInfoScreen(Screen):
    pass


class CadetDash(Screen):
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
        # return ApplicationFormWindow()

    def update_theme(self):
        theme_color = dataHandler.query_app_data("static_app_data")[0]
        self.theme_cls.theme_style = theme_color


MainApp().run()
