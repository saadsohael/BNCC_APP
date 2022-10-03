import io
import time
import webbrowser
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.metrics import sp
import admin
import dataHandler
import mail_handler
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.uix.image import CoreImage
from kivy.core.window import Window

Window.size = (300, 500)

dataHandler.create_app_data()  # create static (on device memory) and dynamic (online ) app data
dataHandler.set_database()

under_login_screen = ["AdminDash", "CadetDash", "ApplyCadetScreen", "PasswordRecoveryWindow"]
under_admin_dash = ["ApplicationFormWindow", "CadetsInfoScreen", "AdminProfile"]
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

            elif self.manager.current in under_login_screen and self.manager.current != "PasswordRecoveryWindow":

                if self.manager.current == "ApplyCadetScreen":
                    self.open_dialog('All credentials will be lost!\n  Are you sure?')

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

            if self.manager.current == "ApplyCadetScreen":  # clear form widgets otherwise it will keep multiplying!!!
                self.manager.get_screen("ApplyCadetScreen").ids.application_form.clear_widgets()

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

        if self.ids.login_label.text == "Admin Login":
            self.manager.current = "AdminDash"
            # if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
            #     self.manager.current = "AdminDash"
            #     self.ids.username_textfield.text = ''
            #     self.ids.password_textfield.text = ''
            # else:
            #     self.show_wrong_credentials("Wrong Username or Password!")
        self.manager.get_screen("AdminDash").ids.nav_drawer.set_state("close")

    def show_wrong_credentials(self, text):
        self.dialog_box = MDDialog(title=text,
                                   size_hint=(None, None),
                                   width=(self.width - sp(50)),
                                   buttons=[MDFlatButton(text='Dismiss', on_release=self.DISMISS_DIALOG_BOX)])
        self.dialog_box.open()

    def DISMISS_DIALOG_BOX(self, instance):
        self.dialog_box.dismiss()

    def go_back(self):

        # fetch previous_screens
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
        elif self.manager.current == "EditFormItemWindow":
            self.manager.get_screen("ApplicationFormWindow").show_form()
            self.manager.current = "ApplicationFormWindow"

        self.manager.transition.direction = 'right'


class PasswordRecoveryWindow(Screen):

    def __init__(self, **kwargs):
        super(PasswordRecoveryWindow, self).__init__(**kwargs)

    def send_otp(self):

        if self.manager.get_screen("LoginScreen").ids.login_label.text == "Cadet Login":
            pass

        elif self.manager.get_screen("LoginScreen").ids.login_label.text == "Admin Login":

            if self.ids.mail_address.text == dataHandler.query_admin('admin_email'):

                if mail_handler.has_internet():

                    if dataHandler.query_app_data('dynamic_app_data')[1] < 20 and \
                            dataHandler.query_app_data('dynamic_app_data')[2] < 20:

                        if not dataHandler.otp_recently_sent([v for v in time.asctime().split(" ") if v != '']):

                            mail_handler.mail_by_thread(self.ids.mail_address.text)
                            dataHandler.mark_otp()
                            dataHandler.update_otp_counter("increase")
                            self.open_dialog("OTP has been sent to your email account\nCheck Spam if you can't see..\n"
                                             "Or try again after 2 minutes.")
                            self.ids.send_otp_btn.disabled = True
                            self.start_countdown()

                            otp_label = MDLabel(text='type otp : ')
                            self.otp_textfield = MDTextField(hint_text='enter otp here...')
                            confirm_otp_btn = MDRaisedButton(text="Confirm OTP")
                            confirm_otp_btn.bind(on_release=self.confirm_otp)
                            blank_space_ = MDLabel(text='')

                            self.ids.reset_items.clear_widgets()
                            self.ids.reset_items.add_widget(otp_label)
                            self.ids.reset_items.add_widget(self.otp_textfield)
                            self.ids.reset_items.add_widget(confirm_otp_btn)
                            self.ids.reset_items.add_widget(blank_space_)

                        else:
                            self.open_dialog("You cannot change otp more than everyday.\nPlease try again Tomorrow!")

                    else:
                        self.open_dialog("Oops! Something went wrong.\nPlease Try Again Tomorrow!")

                else:
                    toast("Could not connect to the internet!")

            else:
                toast("Wrong Email Address!")

    def open_dialog(self, title):  # opens dialog box to confirm action

        self.dialog = MDDialog(title=title,
                               size_hint=(None, None),
                               width=(self.width - sp(50)),
                               buttons=[MDFlatButton(text='Dismiss', on_release=self.close_dialog)])
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def confirm_otp(self, instance):  # when confirm otp button is pressed!

        if dataHandler.otp_matched(self.otp_textfield.text):
            new_pass_label = MDLabel(text='Type new password : ')
            self.new_pass_textfield = MDTextField(hint_text='enter new pass...')
            confirm_pass_btn = MDRaisedButton(text="Confirm Password")
            confirm_pass_btn.bind(on_release=self.confirm_pass)
            blank_space_ = MDLabel(text='')
            dataHandler.drop_column('admin_data', 'otp')

            self.ids.reset_items.clear_widgets()
            self.ids.reset_items.add_widget(new_pass_label)
            self.ids.reset_items.add_widget(self.new_pass_textfield)
            self.ids.reset_items.add_widget(confirm_pass_btn)
            self.ids.reset_items.add_widget(blank_space_)

        else:
            toast("Wrong OTP!")

    def confirm_pass(self, instance):  # when the change password button is pressed!

        admin.update_password(self.new_pass_textfield.text)  # update password on server

        self.manager.current = "LoginScreen"
        toast("Your password has been changed!")
        self.ids.mail_address.text = ''
        self.ids.reset_items.clear_widgets()  # clear new password input textfield!

    # this codes below generates and shows timer on app screen

    countdown_seconds = 120
    a = NumericProperty(countdown_seconds)  # because we want 120 seconds to pass before requesting another otp

    def start_countdown(self):

        Animation.cancel_all(self)  # stop any current animations
        self.anim = Animation(a=0, duration=self.a)

        def finish_callback(animation, incr_crude_clock):
            incr_crude_clock.text = ''
            self.ids.send_otp_btn.disabled = False
            self.a = 120

        self.anim.bind(on_complete=finish_callback)
        self.anim.start(self)

    def on_a(self, instance, value):
        if self.ids.send_otp_btn.disabled:
            self.ids.countdown.text = f'seconds left : {str(int(value))}'
        else:
            self.ids.countdown.text = ''


class ApplyCadetScreen(Screen):

    def __init__(self, **kwargs):
        super(ApplyCadetScreen, self).__init__(**kwargs)

    # create an application form window with the items in the dynamic (online) database

    def create_form(self):
        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])

        for v in form_items:
            label = MDLabel(text=v, size_hint_x=0.7)
            textfield = MDTextField(mode="rectangle", size_hint_x=0.3,
                                    hint_text="DD/MM/YYYY" if v == 'Date Of Birth : ' else '', )
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
            text = ''.join(v.split(":")).rstrip()
            label = MDLabel(text=text, size_hint_x=0.55, halign="center", valign='middle')
            self.ids.edit_application_form.add_widget(label)


class EditFormItemWindow(Screen):

    def __init__(self, **kwargs):
        super(EditFormItemWindow, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)  # bind screen with keyboard or touch input
        self.item_dropdown_menu = MDDropdownMenu()

        self.form_items_names = []  # <== contains only the form item names without ':'
        for v in eval(dataHandler.query_app_data("dynamic_app_data")[0]):
            # self.form_items_names.append(' '.join([i for i in v.split(" ") if i != ':']))
            self.form_items_names.append(''.join(v.split(":")).rstrip())

    # handles keyboard/ touch input!
    def _key_handler(self, instance, key, *args):

        if key == 27:
            self.ids.add_toggle_btn.disabled = False
            self.ids.add_toggle_btn.state = 'normal'
            self.ids.edit_toggle_btn.disabled = False
            self.ids.edit_toggle_btn.state = 'normal'
            self.ids.item_name_input.disabled = False
            self.ids.item_place_label.text = 'Place at : '
            self.ids.drop_item.text = self.form_items_names[0]
            self.ids.add_or_edit_btn.text = "Add Item To Form"
            self.item_dropdown_menu.dismiss()

    def change_texts(self):  # changes the label and textfield texts according to add/edit button!

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

    def item_dropdown_(self):  # dropdown menu for form items to select!

        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])

        if self.ids.add_toggle_btn.state == 'down':
            form_items.pop()
            form_items.insert(0, 'At Top')
            form_items.append('At Bottom')

        item_dropdown_list = []

        for v in form_items:  # looping through the items to add AFTER before every item name!

            # if user is adding items
            if self.ids.add_toggle_btn.state == 'down':

                # if form item is not the first or last item in the list! (first: at top, last: at bottom)
                if form_items.index(v) != 0 and form_items.index(v) != (len(form_items) - 1):
                    item_dropdown_list.append('After ' + ''.join(v.split(":")).rstrip())
                else:
                    item_dropdown_list.append(''.join(v.split(":")).rstrip())

            # if user is editing or removing items or doing nothing
            else:
                # elif self.ids.edit_toggle_btn.state == 'down':
                item_dropdown_list.append(''.join(v.split(":")).rstrip())

            # elif self.ids.edit_toggle_btn.disabled and self.ids.add_toggle_btn.disabled:
            #     item_dropdown_list.append(' '.join([i for i in v.split(" ") if i != ':']))
        item_dropdown_list = [
            {
                "viewclass": "OneLineListItem",
                "text": v,
                "height": sp(40),
                "on_release": lambda x=v: self.selected_item(x)
            } for v in item_dropdown_list
        ]  # this is just a linked list! like : [v for v in list]

        self.item_dropdown_menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=item_dropdown_list,
            position="auto",
            width_mult=6
        )
        self.item_dropdown_menu.open()

    def selected_item(self, item_name):
        self.ids.drop_item.text = item_name
        self.item_dropdown_menu.dismiss()

    def add_item(self):  # add form item to database

        form_items = eval(dataHandler.query_app_data("dynamic_app_data")[0])
        input_text = self.ids.item_name_input.text.split(" ")

        # bottom lines format item input text to capitalize first letter of every word and stores in item_name variable!
        item_name = ' '.join(list(map(lambda x: x.capitalize(), input_text)))

        if not self.empty_textField(item_name):  # if textfield is not empty!
            if (item_name + ' : ') not in form_items:  # if item is not already in the application form

                if self.ids.drop_item.text == "At Top":
                    form_items.insert(0, item_name + ' : ')  # inserts new item at index 0

                elif self.ids.drop_item.text == "At Bottom":
                    form_items.append(item_name + ' : ')  # inserts new item at the last index

                else:
                    place_item = ' '.join([v for v in self.ids.drop_item.text.split(" ") if v != "After"])
                    index_ = form_items.index(place_item + ' : ') + 1
                    form_items.insert(index_,
                                      f'{item_name} : ')  # inserts new item after the selected dropdown item

                dataHandler.update_app_data("dynamic_app_data", "application_form", repr(form_items))
                toast("Item Successfully Added To Application Form!")

                self.ids.item_name_input.text = ''
                self.ids.drop_item.text = 'At Top'

                # this following code clears the self.form_items_name list to update with the newly added item in form
                self.form_items_names.clear()
                for v in eval(dataHandler.query_app_data("dynamic_app_data")[0]):  # looping though new dynamic_app_data
                    self.form_items_names.append(''.join(v.split(":")).rstrip())

            else:
                toast(f'{item_name} is already in the form!')
        else:
            toast("Enter a valid item name please!")

    def edit_item(self):

        if not self.empty_textField(self.ids.item_name_input.text):  # if textfield is not empty!

            # this following code formats the textfield input to Capitalize every first word
            input_text = self.ids.item_name_input.text.split(" ")
            item_new_name = ' '.join(list(map(lambda x: x.capitalize(), input_text)))

            if item_new_name not in self.form_items_names:

                if self.ids.drop_item.text in self.form_items_names:  # proceed if what user trying to edit is in the list
                    index = self.form_items_names.index(
                        self.ids.drop_item.text)  # index of the item user is trying to edit
                    self.form_items_names.insert(index,
                                                 item_new_name)  # insert new edited name of item in that index
                    self.form_items_names.remove(
                        self.form_items_names[index + 1])  # remove prev item that's been edited

                    new_form_items = [f'{v} : ' for v in
                                      self.form_items_names]  # looping through list to format with a ':'
                    dataHandler.update_app_data("dynamic_app_data", "application_form", repr(new_form_items))

                    toast("Item Name Updated!")

                    self.ids.item_name_input.text = ''

                else:
                    toast("item is not in the list!")
            else:
                toast(f'{item_new_name} is already in the list')

        else:
            toast("Enter a valid item name please!")

    def empty_textField(self, textField_text):  # if user did not put anything in textfield it returns True

        if textField_text == '' or textField_text.isspace():
            return True

    def remove_confirmation(self):

        self.dialog = MDDialog(title="Are You Sure You Want To Remove"
                                     f"\n{self.ids.drop_item.text} from Application Form?",
                               size_hint=(None, None),
                               width=(self.width - sp(50)),
                               buttons=[MDFlatButton(text='Yes', on_release=self.remove_item),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )
        self.dialog.open()

    def remove_item(self, instance):

        self.form_items_names.remove(self.ids.drop_item.text)
        updated_form_items_list = [f'{v} : ' for v in self.form_items_names]
        dataHandler.update_app_data("dynamic_app_data", "application_form", repr(updated_form_items_list))
        toast(f"{self.ids.drop_item.text} removed from Application Form")
        self.ids.drop_item.text = self.form_items_names[0]
        self.dialog.dismiss()

    def do_stuffs(self):

        if self.ids.add_toggle_btn.disabled and self.ids.edit_toggle_btn.disabled:
            self.remove_confirmation()
        else:
            if self.ids.add_toggle_btn.state == 'down':
                self.add_item()
            elif self.ids.edit_toggle_btn.state == 'down':
                self.edit_item()

    def close_dialog(self, instance):
        self.dialog.dismiss()


class AdminProfile(Screen):

    def show_admin(self):
        self.adm_info = admin.admin_info()
        admin_data = admin.fetch_admin_data()  # get admin data from database

        # showing profile photo on app
        image = dataHandler.query_admin('profile_photo')
        data = io.BytesIO(image)
        img = CoreImage(data, ext="png").texture
        # self.ids.admin_profile_photo.source = 'a.jpg'
        self.ids.admin_profile_photo.texture = img
        self.info_dic = {}

        for v in range(len(self.adm_info)):
            self.item = TwoLineListItem(text=self.adm_info[v], secondary_text=admin_data[v + 4],
                                        on_press=lambda x: self.show_data())
            self.item.id = self.item.text
            self.info_dic[self.item.id] = self.item
            self.ids.admin_info.add_widget(self.item)

    def show_data(self):
        for v in self.info_dic.values():
            if v.state == 'down':
                toast(f'{v.text} : {v.secondary_text}', duration=3)


class CadetsInfoScreen(Screen):
    pass


class CadetDash(Screen):
    pass


class NoticeScreen(Screen):
    pass


class AboutScreen(Screen):
    def open_web(self, webname):
        if webname == 'gmail':
            toast("Email : saad.raj.bd@gmail.com")
        elif webname == 'facebook':
            toast("Facebook : Saad Sohael")
            webbrowser.open("https://www.facebook.com/isaadsohael")
        elif webname == 'instagram':
            toast("Instagram : isaadsohael")
            webbrowser.open("https://www.instagram.com/isaadsohael")


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
        # return AdminProfile()

    def update_theme(self):
        theme_color = dataHandler.query_app_data("static_app_data")[0]
        self.theme_cls.theme_style = theme_color


MainApp().run()
