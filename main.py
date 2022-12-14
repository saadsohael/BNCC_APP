import io
import time
import webbrowser
from random import randint
import mysql.connector
import admin
import dataHandler
import mail_handler
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFloatingActionButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.filemanager import MDFileManager
from kivy.metrics import sp
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.uix.image import CoreImage
from kivy.core.window import Window
from kivy import platform

if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

under_login_screen = ["AdminDash", "CadetDash", "ApplyCadetScreen", "PasswordRecoveryWindow"]
under_admin_dash = ["ApplicationFormWindow"]
under_cadet_dash = []
common_screens = ["NoticeScreen", "AboutScreen", "SettingsScreen", "AdminProfile"]


class WindowManager(ScreenManager):
    pass


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)  # bind screen with keyboard or touch input

        self.auto_complete_admin = MDDialog(title="Do You Want To Autofill ID and Password?",
                                            size_hint=(None, None),
                                            _spacer_top=15,
                                            width=(self.width - 80),
                                            buttons=[MDFlatButton(text='Yes',
                                                                  on_release=self.admin_autofill),
                                                     MDFlatButton(text='No',
                                                                  on_release=self.close_autofill)]
                                            )

        self.auto_complete_cadet = MDDialog(title="Do You Want To Autofill ID and Password?",
                                            size_hint=(None, None),
                                            _spacer_top=15,
                                            width=(self.width - 80),
                                            buttons=[MDFlatButton(text='Yes', on_release=self.cadet_autofill),
                                                     MDFlatButton(text='No',
                                                                  on_release=self.close_autofill)]
                                            )

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

            elif self.manager.current == "ViewApplicantScreen":
                self.manager.current = "AdminDash"

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

            if self.ids.login_label.text == "Admin Login":
                self.manager.get_screen("ShowNoticeScreen").remove_del_btn()

            if self.manager.current == "ApplyCadetScreen":  # clear form widgets otherwise it will keep multiplying!!!
                self.manager.get_screen("ApplyCadetScreen").ids.application_form.clear_widgets()

            elif self.manager.current == "CadetDash":
                self.manager.get_screen("CadetDash").ids.cadet_info.clear_widgets()

            self.manager.current = "LoginScreen"
            self.manager.transition.direction = 'right'

    def open_dialog(self, title):  # opens dialog box to confirm action

        self.dialog = MDDialog(title=title,
                               size_hint=(None, None),
                               _spacer_top=15,
                               width=(self.width - 80),
                               buttons=[MDFlatButton(text='Yes', on_release=self.confirm_yes),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def log_in_btn(self):
        try:
            if self.ids.login_label.text == "Admin Login":
                if dataHandler.is_admin(self.ids.username_textfield.text, self.ids.password_textfield.text):
                    if self.ids.remember_check.state == 'down':
                        dataHandler.create_offline_datatable('admin_offline_data', 'admin_id', 'admin_password')
                        dataHandler.remember_user("admin_offline_data", self.ids.username_textfield.text,
                                                  self.ids.password_textfield.text, "admin_id")
                        dataHandler.update_app_data('static_app_data', 'remember_admin', True)
                    self.manager.get_screen("ShowNoticeScreen").add_del_btn()
                    self.manager.current = "AdminDash"
                    self.ids.username_textfield.text = ''
                    self.ids.password_textfield.text = ''
                    self.ids.remember_check.state = 'normal'
                else:
                    toast("Wrong Username or Password!")
            else:
                if dataHandler.is_cadet(self.ids.username_textfield.text,
                                        self.ids.password_textfield.text) != 'Not Cadet':
                    if dataHandler.is_cadet(self.ids.username_textfield.text, self.ids.password_textfield.text):
                        if self.ids.remember_check.state == 'down':
                            dataHandler.remember_user("cadet_offline_data", self.ids.username_textfield.text,
                                                      self.ids.password_textfield.text, "cadet_id")
                            dataHandler.update_app_data('static_app_data', 'remember_cadet', True)
                        self.manager.get_screen("CadetDash").cadet_pass = self.ids.password_textfield.text
                        self.manager.get_screen("CadetDash").show_cadet()
                        self.manager.current = "CadetDash"
                        self.ids.username_textfield.text = ''
                        self.ids.password_textfield.text = ''
                        self.ids.remember_check.state = 'normal'
                    else:
                        toast("Wrong Id or Password!")
                else:
                    toast("Wrong Id or Password!")

            self.manager.get_screen("AdminDash").ids.nav_drawer.set_state("closed")

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def auto_complete(self):
        if self.ids.login_label.text == "Admin Login":
            if dataHandler.query_app_data('remember_admin', 'static_app_data')[0][0]:
                if self.ids.username_textfield.text == '':
                    self.auto_complete_admin.open()
        elif self.ids.login_label.text == "Cadet Login":
            if dataHandler.query_app_data('remember_cadet', 'static_app_data')[0][0]:
                if self.ids.username_textfield.text == '':
                    self.auto_complete_cadet.open()

    def admin_autofill(self, instance):
        try:
            cadet_id = dataHandler.query_app_data("admin_id", "admin_offline_data")[0][0]
            cadet_password = dataHandler.query_app_data("admin_password", "admin_offline_data")[0][0]
            self.ids.username_textfield.text = cadet_id
            self.ids.password_textfield.text = cadet_password
            self.auto_complete_admin.dismiss()
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def cadet_autofill(self, instance):
        try:
            cadet_id = dataHandler.query_app_data("cadet_id", "cadet_offline_data")[0][0]
            cadet_password = dataHandler.query_app_data("cadet_password", "cadet_offline_data")[0][0]
            self.ids.username_textfield.text = cadet_id
            self.ids.password_textfield.text = cadet_password
            self.auto_complete_cadet.dismiss()
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def close_autofill(self, instance):
        self.auto_complete_admin.dismiss()
        self.auto_complete_cadet.dismiss()

    def go_back(self):
        # fetch previous_screens
        if self.manager.current in under_login_screen:
            if self.ids.login_label.text == "Admin Login":
                self.manager.get_screen("ShowNoticeScreen").remove_del_btn()
            self.manager.current = "LoginScreen"
        elif self.manager.current in under_admin_dash:
            if self.manager.current == "AdminProfile":
                self.manager.get_screen("AdminProfile").info_dic.clear()
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

        elif self.manager.current in ["ShowNoticeScreen", "CreateNoticeScreen"]:
            self.manager.get_screen("NoticeScreen").clear_widgets()
            self.manager.get_screen("NoticeScreen").notice_dic = {}
            self.manager.get_screen("NoticeScreen").show_notices()
            self.manager.current = "NoticeScreen"

        elif self.manager.current == "ShowApplicantInfoScreen":
            if self.manager.get_screen("ShowApplicantInfoScreen").ids.floating_btn.state == 'close':
                self.manager.get_screen("ViewApplicantScreen").applicants_dic = {}
                self.manager.get_screen('ShowApplicantInfoScreen').ids.cadet_info.clear_widgets()
                self.manager.get_screen("ViewApplicantScreen").show_applicant_list()
                self.manager.current = "ViewApplicantScreen"
            else:
                self.manager.get_screen("ShowApplicantInfoScreen").ids.floating_btn.close_stack()

        self.manager.transition.direction = 'right'


class PasswordRecoveryWindow(Screen):

    def __init__(self, **kwargs):
        super(PasswordRecoveryWindow, self).__init__(**kwargs)

    def send_otp(self):

        if dataHandler.has_internet():

            if dataHandler.query_app_data("otp_manager_1", "dynamic_app_data")[0][0] < 20 and \
                    dataHandler.query_app_data("otp_manager_2", "dynamic_app_data")[0][0] < 20:

                if not dataHandler.otp_recently_sent([v for v in time.asctime().split(" ") if v != '']):
                    confirm_otp_btn = MDRaisedButton(text="Confirm OTP")
                    if self.manager.get_screen("LoginScreen").ids.login_label.text == "Admin Login":
                        if self.ids.mail_address.text == dataHandler.query_admin('admin_email'):
                            mail_handler.mail_by_thread("admin", self.ids.mail_address.text,
                                                        mail_handler.send_pass_recovery_otp)
                            confirm_otp_btn.bind(on_release=self.confirm_otp)

                            dataHandler.mark_otp()
                            dataHandler.update_otp_counter("increase")
                            self.open_dialog("OTP has been sent to your email account\nCheck Spam if you can't see..\n"
                                             "Or try again after 2 minutes.")
                            self.ids.send_otp_btn.disabled = True
                            self.start_countdown()

                            otp_label = MDLabel(text='type otp : ', size_hint_x=0.2)
                            self.otp_textfield = MDTextField(hint_text='enter otp here...', size_hint_x=0.8)
                            blank_space_ = MDLabel(text='')

                            self.ids.reset_items.clear_widgets()
                            self.ids.reset_items.add_widget(otp_label)
                            self.ids.reset_items.add_widget(self.otp_textfield)
                            self.ids.reset_items.add_widget(confirm_otp_btn)
                            self.ids.reset_items.add_widget(blank_space_)

                        else:
                            toast("Wrong Email Address")
                    else:
                        if self.ids.mail_address.text in [v[0] for v in
                                                          dataHandler.query_app_data("Email", "cadet_application_data",
                                                                                     "Status", "Cadet")]:
                            mail_handler.mail_by_thread("cadet", self.ids.mail_address.text,
                                                        mail_handler.send_pass_recovery_otp)
                            confirm_otp_btn.bind(on_release=self.confirm_otp)

                            dataHandler.mark_otp()
                            dataHandler.update_otp_counter("increase")
                            self.open_dialog("OTP has been sent to your email account\nCheck Spam if you can't see..\n"
                                             "Or try again after 2 minutes.")
                            self.ids.send_otp_btn.disabled = True
                            self.start_countdown()

                            otp_label = MDLabel(text='type otp : ')
                            self.otp_textfield = MDTextField(hint_text='enter otp here...')
                            blank_space_ = MDLabel(text='')

                            self.ids.reset_items.clear_widgets()
                            self.ids.reset_items.add_widget(otp_label)
                            self.ids.reset_items.add_widget(self.otp_textfield)
                            self.ids.reset_items.add_widget(confirm_otp_btn)
                            self.ids.reset_items.add_widget(blank_space_)

                        else:
                            toast("Wrong Email Address")
                else:
                    self.open_dialog("You cannot change otp more than once a day.\nPlease try again Tomorrow!")

            else:
                self.open_dialog("Oops! Something went wrong.\nPlease Try Again Tomorrow!")

        else:
            toast("Please Check Your Internet Connection!")

    def open_dialog(self, title):  # opens dialog box to confirm action

        self.dialog = MDDialog(title=title,
                               size_hint=(None, None),
                               _spacer_top=15,
                               width=(self.width - 50),
                               buttons=[MDFlatButton(text='Dismiss', on_release=self.close_dialog)])
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def confirm_otp(self, instance):  # when confirm otp button is pressed!
        if dataHandler.has_internet():
            new_pass_label = MDLabel(text='Type new password : ')
            self.new_pass_textfield = MDTextField(hint_text='enter new pass...')
            confirm_pass_btn = MDRaisedButton(text="Confirm Password")
            if self.manager.get_screen("LoginScreen").ids.login_label.text == "Admin Login":
                if dataHandler.otp_matched("admin", self.otp_textfield.text):
                    confirm_pass_btn.bind(on_release=self.confirm_admin_pass)
                    dataHandler.drop_column('admin_data', 'otp')
                    dataHandler.drop_column('admin_data', 'otp_salt')
                    blank_space_ = MDLabel(text='')
                    self.ids.reset_items.clear_widgets()
                    self.ids.reset_items.add_widget(new_pass_label)
                    self.ids.reset_items.add_widget(self.new_pass_textfield)
                    self.ids.reset_items.add_widget(confirm_pass_btn)
                    self.ids.reset_items.add_widget(blank_space_)
                else:
                    toast("Wrong OTP!")

            elif self.manager.get_screen("LoginScreen").ids.login_label.text == "Cadet Login":
                if dataHandler.otp_matched("cadet", self.otp_textfield.text):
                    confirm_pass_btn.bind(on_release=self.confirm_cadet_pass)
                    dataHandler.drop_column('cadet_offline_data', 'otp')
                    dataHandler.drop_column('cadet_offline_data', 'otp_salt')
                    dataHandler.drop_column('cadet_offline_data', 'cadet_email')
                    blank_space_ = MDLabel(text='')
                    self.ids.reset_items.clear_widgets()
                    self.ids.reset_items.add_widget(new_pass_label)
                    self.ids.reset_items.add_widget(self.new_pass_textfield)
                    self.ids.reset_items.add_widget(confirm_pass_btn)
                    self.ids.reset_items.add_widget(blank_space_)
                else:
                    toast("Wrong OTP!")
        else:
            toast("Please Check Your Internet Connection!")

    def confirm_admin_pass(self, instance):  # when the change password button is pressed!

        admin.update_password(self.new_pass_textfield.text)  # update password on server

        self.manager.current = "LoginScreen"
        toast("Your password has been changed!")
        self.ids.mail_address.text = ''
        self.ids.reset_items.clear_widgets()  # clear new password input textfield!

    def confirm_cadet_pass(self, instance):  # when the change password button is pressed!

        dataHandler.update_app_data('cadet_application_data', 'Cadet_Password', self.new_pass_textfield.text, 'Email',
                                    self.ids.mail_address.text)  # update password on server

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
        self.form_inputs = []
        self.correct_dob_input = False
        self.image_path = ''
        self.file_explorer = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.exit_file_explorer,
            preview=False,
        )

    # create an application form window with the items in the dynamic (online) database

    def create_form(self):
        try:
            form_items = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])
            self.textfields = []
            hintText = ''
            for v in form_items:
                if v == 'Date Of Birth':
                    hintText = 'DD/MM/YYYY'
                if v == 'Height':
                    hintText = 'in inch'
                if v == 'Weight':
                    hintText = 'in kg'
                if v == 'Cadet Id':
                    hintText = 'auto generated'
                if v == 'Cadet Password':
                    hintText = 'auto generated'

                label = MDLabel(text=f'{v} : ', size_hint_x=0.55)
                if v in ['Cadet Id', 'Cadet Password']:
                    textfield = MDTextField(mode="rectangle", size_hint_x=0.45, hint_text=hintText, disabled=True)
                elif v == "Profile Photo":
                    textfield = MDRaisedButton(text="Choose Image", size_hint_x=0.45)
                    textfield.bind(on_release=self.open_file_explorer)
                else:
                    textfield = MDTextField(mode="rectangle", size_hint_x=0.45, hint_text=hintText)
                self.textfields.append(textfield)
                self.ids.application_form.add_widget(label)
                self.ids.application_form.add_widget(textfield)
                self.form_inputs.append(textfield)
                hintText = ''
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def open_file_explorer(self, instance):
        self.file_explorer.show('/')

    def select_path(self, path):
        try:
            if dataHandler.is_image(path):
                if len(dataHandler.img_binary_data(path)) <= 60000:
                    self.image_path = path
                    for v in self.textfields:
                        if type(v) == MDRaisedButton:
                            v.text = f'.../{self.image_path.split("/")[-1][:-10:-1][::-1]}'
                    self.file_explorer.close()
                else:
                    toast("Please Choose An Image less than or equal 60kb")
            else:
                toast("Please Choose An Image less than or equal 60kb")
        except IsADirectoryError:
            toast('Please Select A Correct Image less than or equal 60kb')
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def exit_file_explorer(self, instance):
        self.file_explorer.close()

    def form_filled(self):
        if self.correct_dob_input:
            for input_box in self.textfields:
                if type(input_box) == MDRaisedButton:
                    if input_box.text == 'Choose Image':
                        return False
                else:
                    if input_box.hint_text != 'auto generated':
                        if input_box.text == '' or input_box.text.isspace():
                            return False
                    if input_box.hint_text in ["in inch", "in kg"]:
                        try:
                            int(input_box.text)
                        except:
                            return False
            return True
        else:
            return False

    def confirm_apply_btn(self):

        for v in self.textfields:
            if type(v) != MDRaisedButton:
                if v.hint_text == "DD/MM/YYYY":
                    dob = v.text.split("/")
                    try:
                        if int(time.asctime().split(" ")[-1]) - int(dob[2]) >= 14:
                            if len(dob[0]) == 2 and len(dob[1]) == 2 and len(dob[2]) == 4:
                                if dob[1] in ["01", "03", "05", "07", "08", "10", "12"] and 1 <= int(dob[0]) <= 31:
                                    self.correct_dob_input = True
                                elif dob[1] in ["04", "06", "09", "11"] and 1 <= int(dob[0]) <= 30:
                                    self.correct_dob_input = True
                                elif 1 <= int(dob[0]) <= 28 and dob[1] == "02" and int(dob[2]) % 4 != 0:
                                    self.correct_dob_input = True
                                elif 1 <= int(dob[0]) <= 29 and dob[1] == "02" and int(dob[2]) % 4 == 0:
                                    self.correct_dob_input = True
                                else:
                                    self.correct_dob_input = False
                            else:
                                self.correct_dob_input = False
                        else:
                            self.correct_dob_input = False
                    except ValueError and IndexError:
                        self.correct_dob_input = False

        new_label = []
        cadet_info_list = []
        temp_list = []
        try:
            if dataHandler.query_app_data('Cadet_Id', 'cadet_application_data'):
                temp_list = [v[0] for v in dataHandler.query_app_data('Cadet_Id', 'cadet_application_data')]
            unique_id = randint(100001, 199999)
            if unique_id in temp_list:
                while unique_id in temp_list:
                    unique_id = randint(100001, 199999)
            temp_list.append(unique_id)
            cadet_unique_id = str(temp_list[-1])
            if self.form_filled():
                form_items = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])
                cadet_cols = [v for v in dataHandler.query_cadet_col_name()]
                for i in form_items:
                    if i.count("'") > 0:
                        temp_list = []
                        for j in i.split(" "):
                            if j.count("'") > 0:
                                temp_list.append(j.split("'")[0])
                            else:
                                temp_list.append(j)
                        form_items.insert(form_items.index(i), '_'.join(temp_list))
                        form_items.remove(i)
                    else:
                        if i.count(" "):
                            form_items.insert(form_items.index(i), '_'.join(i.split(" ")))
                            form_items.remove(i)
                for v in range(len(cadet_cols)):
                    new_label.insert(v, form_items[form_items.index(cadet_cols[v])])
                    if cadet_cols[v] != "Profile_Photo":
                        if cadet_cols[v] not in ['Cadet_Id', 'Cadet_Password']:
                            if cadet_cols[v] not in ['Email', 'Facebook_Id']:
                                cadet_info_list.insert(v, ' '.join(
                                    [v.capitalize() for v in
                                     self.textfields[form_items.index(cadet_cols[v])].text.split(" ")]))
                            else:
                                cadet_info_list.insert(v, self.textfields[form_items.index(cadet_cols[v])].text)
                        else:
                            cadet_info_list.insert(v, cadet_unique_id) if cadet_cols[v] == 'Cadet_Id' \
                                else cadet_info_list.insert(v, "N/A")
                    else:
                        cadet_info_list.insert(v, dataHandler.img_binary_data(self.image_path))

                if dataHandler.has_internet():
                    if mail_handler.isValidEmail(self.textfields[cadet_cols.index('Email')].text):
                        if dataHandler.query_app_data("*", "cadet_application_data"):
                            existing_emails = [v[0] for v in
                                               dataHandler.query_app_data("Email", "cadet_application_data")]
                            if self.textfields[cadet_cols.index('Email')].text not in existing_emails:
                                dataHandler.add_cadet_info(cadet_info_list)
                                toast("Application Form Submitted Successfully!\nYou will get an email once approved.",
                                      duration=5)
                            else:
                                toast("Email already registered!")
                        else:
                            dataHandler.add_cadet_info(cadet_info_list)
                            toast("Application Form Submitted Successfully!\nYou will get an email once approved.",
                                  duration=5)
                    else:
                        toast("Email doesn't exist!")
                else:
                    toast("Please Check Your Internet Connection!")
            else:
                toast("Please fill up the form correctly!")

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")


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
        try:
            form_items = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])
            for v in form_items:
                label = MDLabel(text=v,
                                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                adaptive_height=True)
                self.ids.edit_application_form.add_widget(label)
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")


class EditFormItemWindow(Screen):

    def __init__(self, **kwargs):
        super(EditFormItemWindow, self).__init__(**kwargs)
        Window.bind(on_keyboard=self._key_handler)  # bind screen with keyboard or touch input
        self.item_dropdown_menu = MDDropdownMenu()
        try:
            self.form_items_names = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    # handles keyboard/ touch input!
    def _key_handler(self, instance, key, *args):

        if key == 27:
            self.ids.add_toggle_btn.disabled = False
            self.ids.add_toggle_btn.state = 'normal'
            self.ids.edit_toggle_btn.disabled = False
            self.ids.edit_toggle_btn.state = 'normal'
            self.ids.item_name_input.disabled = False
            self.ids.item_place_label.text = 'Place at : '
            try:
                self.ids.drop_item.text = self.form_items_names[0]
            except AttributeError:
                pass
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
        try:

            form_items = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])

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
                        item_dropdown_list.append(f'After {v}')
                    else:
                        item_dropdown_list.append(v)

                # if user is editing or removing items or doing nothing
                else:
                    if self.ids.add_or_edit_btn.text == "Remove Item":
                        if v not in dataHandler.primary_form_items():
                            item_dropdown_list.append(v)
                    else:
                        item_dropdown_list.append(v)

            item_dropdown_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": v,
                    "height": 40,
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
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def selected_item(self, item_name):
        self.ids.drop_item.text = item_name
        self.item_dropdown_menu.dismiss()

    def add_item(self):  # add form item to database
        try:
            form_items = eval(dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])
            input_text = self.ids.item_name_input.text.split(" ")

            # bottom lines format item input text to capitalize first letter of every word and stores in item_name variable!
            item_name = ' '.join(list(map(lambda x: x.capitalize(), input_text)))

            if not self.empty_textField(item_name):  # if textfield is not empty!
                if item_name not in form_items:  # if item is not already in the application form

                    if self.ids.drop_item.text == "At Top":
                        form_items.insert(0, item_name)  # inserts new item at index 0

                    elif self.ids.drop_item.text == "At Bottom":
                        form_items.append(item_name)  # inserts new item at the last index

                    else:
                        place_item = ' '.join([v for v in self.ids.drop_item.text.split(" ") if v != "After"])
                        index_ = form_items.index(place_item) + 1
                        form_items.insert(index_, item_name)  # inserts new item after the selected dropdown item

                    dataHandler.update_app_data("dynamic_app_data", "application_form", repr(form_items))
                    dataHandler.add_column('cadet_application_data', item_name, 'No Data To Show')
                    toast("Item Successfully Added To Application Form!")

                    self.ids.item_name_input.text = ''
                    self.ids.drop_item.text = 'At Top'

                    # this following code clears the self.form_items_name list to update with the newly added item in form
                    self.form_items_names.clear()
                    self.form_items_names = eval(
                        dataHandler.query_app_data("application_form", "dynamic_app_data")[0][0])

                else:
                    toast(f'{item_name} is already in the form!')
            else:
                toast("Enter a valid item name please!")
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def edit_item(self):
        try:
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

                        new_form_items = [v for v in self.form_items_names]  # looping through list to format with a ':'
                        dataHandler.update_app_data("dynamic_app_data", "application_form", repr(new_form_items))
                        old_col_name = ''
                        new_col_name = ''
                        if self.ids.drop_item.text.count("'") > 0:
                            temp_list = []
                            for i in self.ids.drop_item.text.split(" "):
                                if i.count("'") > 0:
                                    temp_list.append(i.split("'")[0])
                                else:
                                    temp_list.append(i)
                            old_col_name = '_'.join(temp_list)
                        else:
                            old_col_name = '_'.join(self.ids.drop_item.text.split(" "))
                        if self.ids.item_name_input.text.count("'") > 0:
                            temp_list = []
                            for i in self.ids.item_name_input.text.split(" "):
                                if i.count("'") > 0:
                                    temp_list.append(i.split("'")[0].capitalize())
                                else:
                                    temp_list.append(i.capitalize())
                            new_col_name = '_'.join(temp_list)
                        else:
                            new_col_name = '_'.join([v.capitalize() for v in self.ids.item_name_input.text.split(" ")])
                        dataHandler.change_col_name('cadet_application_data', old_col_name, new_col_name)
                        toast("Item Name Updated!")
                        self.ids.item_name_input.text = ''

                    else:
                        toast("item is not in the list!")
                else:
                    toast(f'{item_new_name} is already in the list')

            else:
                toast("Enter a valid item name please!")
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def empty_textField(self, textField_text):  # if user did not put anything in textfield it returns True

        if textField_text == '' or textField_text.isspace():
            return True

    def remove_confirmation(self):

        self.dialog = MDDialog(title="Are You Sure You Want To Remove"
                                     f"\n{self.ids.drop_item.text} from Application Form?",
                               size_hint=(None, None),
                               _spacer_top=15,
                               width=(self.width - 50),
                               buttons=[MDFlatButton(text='Yes', on_release=self.remove_item),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )
        self.dialog.open()

    def remove_item(self, instance):
        try:
            if self.ids.drop_item.text not in dataHandler.primary_form_items():
                if self.ids.drop_item.text.count("'") > 0:
                    temp_list = []
                    for i in self.ids.drop_item.text.split(" "):
                        if i.count("'") > 0:
                            temp_list.append(i.split("'")[0])
                        else:
                            temp_list.append(i)
                    dataHandler.drop_column('cadet_application_data', '_'.join(temp_list))

                else:
                    dataHandler.drop_column('cadet_application_data', '_'.join(self.ids.drop_item.text.split(" ")))

                self.form_items_names.remove(self.ids.drop_item.text)
                updated_form_items_list = [v for v in self.form_items_names]
                dataHandler.update_app_data("dynamic_app_data", "application_form", repr(updated_form_items_list))
                toast(f"{self.ids.drop_item.text} removed from Application Form")
                self.ids.drop_item.text = self.form_items_names[0]
                self.dialog.dismiss()
            else:
                toast("Cannot Delete Primary Form Item!")
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

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

    def set_navigation(self):
        if self.manager.get_screen("LoginScreen").ids.login_label.text == "Admin Login":
            self.ids.nav_label.text = "Admin Dash"
            self.ids.nav_user_info.text = "Cadets Info"
            self.ids.nav_dash.text = "Dash"
            self.ids.nav_dash.disabled = False
        else:
            self.ids.nav_label.text = "Cadet Dash"
            self.ids.nav_user_info.text = "Admin Info"
            self.ids.nav_dash.text = ""
            self.ids.nav_dash.disabled = True

    def show_admin(self):
        try:
            self.adm_info = admin.admin_info()
            admin_data = admin.fetch_admin_data()  # get admin data from database

            # showing profile photo on app
            image = dataHandler.query_admin('profile_photo')
            data = io.BytesIO(image)
            img = CoreImage(data, ext="png").texture
            self.ids.admin_profile_photo.texture = img
            self.info_dic = {}

            for v in range(len(self.adm_info)):
                self.item = TwoLineListItem(text=self.adm_info[v], secondary_text=admin_data[v + 4],
                                            on_press=lambda x: self.show_data())
                self.item.id = self.item.text
                self.info_dic[self.item.id] = self.item
                self.ids.admin_info.add_widget(self.item)
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def show_data(self):
        for v in self.info_dic.values():
            if v.state == 'down':
                toast(f'{v.text} : {v.secondary_text}', duration=3)


class ViewApplicantScreen(Screen):

    def __init__(self, **kwargs):
        super(ViewApplicantScreen, self).__init__(**kwargs)
        self.applicant_type = "Pending"
        self.applicants_dic = {}

    def show_applicant_list(self):
        try:
            scroll_view = ScrollView()
            md_list = MDList()
            applicants = dataHandler.query_app_data("*", "cadet_application_data", "Status", self.applicant_type)
            if applicants:
                for applicant in applicants:
                    applicant_item = TwoLineListItem(
                        text=
                        dataHandler.query_app_data('Name', 'cadet_application_data', "Status", self.applicant_type)[
                            applicants.index(applicant)][0],
                        secondary_text=
                        dataHandler.query_app_data('Email', 'cadet_application_data', "Status", self.applicant_type)[
                            applicants.index(applicant)][0], on_release=lambda x: self.view_applicant())
                    applicant_item.id = applicant_item.text
                    self.applicants_dic[applicant_item.id] = applicant_item
                    md_list.add_widget(applicant_item)
            else:
                if self.applicant_type == "Pending":
                    md_list.add_widget(TwoLineListItem(text="No Applicants To Show", secondary_text=''))
                elif self.applicant_type == "Approved":
                    md_list.add_widget(TwoLineListItem(text="No Applicants To Review", secondary_text=''))
                else:
                    md_list.add_widget(TwoLineListItem(text="No Cadets To Show", secondary_text=''))

            scroll_view.add_widget(md_list)
            self.add_widget(scroll_view)
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def view_applicant(self):
        for applicant in self.applicants_dic.values():
            if applicant.state == 'down':
                if self.applicant_type == "Pending":
                    self.manager.get_screen('ShowApplicantInfoScreen').data = {
                        'Approve Application': 'check',
                        'Remove Application': 'delete',
                        'Cancel': 'close',
                    }
                elif self.applicant_type == "Approved":
                    self.manager.get_screen('ShowApplicantInfoScreen').data = {
                        'Make Cadet': 'check',
                        'Remove Cadet': 'delete',
                        'Cancel': 'close',
                    }
                else:
                    self.manager.get_screen('ShowApplicantInfoScreen').data = {
                        'Chat': 'facebook-messenger',
                        'Remove Cadet': 'delete',
                        'Cancel': 'close',
                    }

                self.manager.get_screen('ShowApplicantInfoScreen').ids.floating_btn.data = self.manager.get_screen(
                    'ShowApplicantInfoScreen').data
                self.manager.get_screen('ShowApplicantInfoScreen').cadet_email_address = applicant.secondary_text
                self.manager.get_screen('ShowApplicantInfoScreen').show_applicant()
                self.manager.get_screen('ShowApplicantInfoScreen').ids.floating_btn.close_stack()
                self.manager.current = 'ShowApplicantInfoScreen'
                self.clear_widgets()


class ShowApplicantInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(ShowApplicantInfoScreen, self).__init__(**kwargs)

        self.cadet_email_address = ''
        self.dialog = MDDialog(title="Are You Sure You Want To Remove This Applicant?",
                               size_hint=(None, None),
                               _spacer_top=15,
                               width=(self.width - 50),
                               buttons=[MDFlatButton(text='Yes', on_release=self.remove_item),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )
        self.data = {
            'Approve Application': 'check',
            'Remove Application': 'delete',
            'Cancel': 'close',
        }

    def show_applicant(self):
        try:
            self.cadet_cols = [(' '.join(v.split("_"))) for v in dataHandler.query_cadet_col_name()]
            self.cadet_cols.insert(0, "Status")
            cadet_data = [i for i in
                          [v for v in dataHandler.query_app_data("*", "cadet_application_data") if
                           (self.cadet_email_address in v)][0]]
            cadet_data.remove(cadet_data[self.cadet_cols.index("Profile Photo")])
            self.cadet_cols.remove("Profile Photo")

            # showing profile photo on app
            image = \
                dataHandler.query_app_data('Profile_Photo', 'cadet_application_data', 'Email',
                                           self.cadet_email_address)[0][
                    0]
            data = io.BytesIO(image)
            img = CoreImage(data, ext="png").texture
            self.ids.cadet_profile_photo.texture = img
            self.info_dic = {}

            for v in range(len(self.cadet_cols)):
                if self.cadet_cols[v] == "Facebook Id":
                    self.item = TwoLineListItem(text=self.cadet_cols[v], secondary_text=f'facebook.com/{cadet_data[v]}',
                                                on_press=lambda x: self.show_cadet_data())
                else:
                    self.item = TwoLineListItem(text=self.cadet_cols[v], secondary_text=cadet_data[v],
                                                on_press=lambda x: self.show_cadet_data())
                self.item.id = self.item.text
                self.info_dic[self.item.id] = self.item
                self.ids.cadet_info.add_widget(self.item)
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def show_cadet_data(self):
        for v in self.info_dic.values():
            if v.state == 'down':
                toast(f'{v.text} : {v.secondary_text}', duration=3)

    def callback(self, instance):
        try:
            if instance.icon == 'check':
                if self.manager.get_screen("ViewApplicantScreen").applicant_type == "Pending":
                    dataHandler.update_app_data('cadet_application_data', 'Status', 'Approved', 'Email',
                                                self.cadet_email_address)
                    toast("Cadet Application Approved!")

                else:
                    if dataHandler.has_internet():
                        if dataHandler.query_app_data('otp_manager_1', 'dynamic_app_data')[0][0] < 20 or \
                                dataHandler.query_app_data('otp_manager_2', 'dynamic_app_data')[0][0] < 20:
                            dataHandler.update_app_data('cadet_application_data', 'Status', 'Cadet', 'Email',
                                                        self.cadet_email_address)
                            mail_handler.mail_by_thread("cadet", self.cadet_email_address,
                                                        mail_handler.send_cadet_id_pass)
                            dataHandler.update_otp_counter('increase')
                            toast("Cadet Status Updated!")
                        else:
                            toast("Cadet Adding Limit Ended. Please try again after 24 hours")
                    else:
                        toast("Please Check Your Internet Connection!")
                self.manager.current = "ViewApplicantScreen"
                self.manager.get_screen("ViewApplicantScreen").applicants_dic = {}
                self.manager.get_screen("ViewApplicantScreen").show_applicant_list()

            elif instance.icon == 'delete':
                self.dialog.open()

            elif instance.icon == 'facebook-messenger':
                webbrowser.open(
                    f'https://www.m.me/{dataHandler.query_app_data("Facebook_Id", "cadet_application_data", "Email", self.cadet_email_address)[0][0].split("/")[-1]}')

            else:
                self.ids.floating_btn.close_stack()

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def remove_item(self, instance):
        try:
            dataHandler.delete_query('cadet_application_data', 'Email', self.cadet_email_address)
            self.manager.get_screen("ViewApplicantScreen").applicants_dic = {}
            self.manager.get_screen("ViewApplicantScreen").show_applicant_list()
            self.manager.current = "ViewApplicantScreen"
            toast("Cadet Application Approved!")
            self.dialog.dismiss()

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def open(self):
        self.ids.floating_btn.size_hint_y = 1.2

    def close(self):
        self.ids.floating_btn.size_hint_y = 0.2


class CadetDash(Screen):
    def __init__(self, **kwargs):
        super(CadetDash, self).__init__(**kwargs)
        self.cadet_pass = ''

    def show_cadet(self):
        try:
            self.cadet_cols = [' '.join(v.split("_")) for v in dataHandler.query_cadet_col_name() if
                               v != "Cadet_Password"]
            cadet_data = [v for v in
                          dataHandler.query_app_data('*', "cadet_application_data", "Cadet_Password", self.cadet_pass)[
                              0] if
                          v not in [self.cadet_pass, 'Cadet']]
            cadet_data.remove(cadet_data[self.cadet_cols.index("Profile Photo")])
            self.cadet_cols.remove("Profile Photo")

            # showing profile photo on app
            image = \
                dataHandler.query_app_data('Profile_Photo', 'cadet_application_data', 'Cadet_Password',
                                           self.cadet_pass)[0][
                    0]
            data = io.BytesIO(image)
            img = CoreImage(data, ext="png").texture
            self.ids.cadet_profile_photo.texture = img
            self.info_dic = {}

            for v in range(len(self.cadet_cols)):
                if self.cadet_cols[v] == "Facebook Id":
                    self.item = TwoLineListItem(text=self.cadet_cols[v], secondary_text=f'facebook.com/{cadet_data[v]}',
                                                on_press=lambda x: self.show_cadet_data())
                else:
                    self.item = TwoLineListItem(text=self.cadet_cols[v], secondary_text=cadet_data[v],
                                                on_press=lambda x: self.show_cadet_data())
                self.item.id = self.item.text
                self.info_dic[self.item.id] = self.item
                self.ids.cadet_info.add_widget(self.item)

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def show_cadet_data(self):
        for v in self.info_dic.values():
            if v.state == 'down':
                toast(f'{v.text} : {v.secondary_text}', duration=3)


class NoticeScreen(Screen):

    def __init__(self, **kwargs):
        super(NoticeScreen, self).__init__(**kwargs)
        self.notice_dic = {}

    def show_notices(self):
        scroll_view = ScrollView()
        md_list = MDList()
        action_button = MDFloatingActionButton(icon='plus', pos_hint={'center_x': 0.8, 'center_y': 0.1})
        action_button.bind(on_release=self.create_notice)
        try:
            notices = dataHandler.fetch_notices()
            for notice in notices:
                notice_item = TwoLineListItem(text=notice[0], secondary_text=notice[1],
                                              on_release=lambda x: self.view_notice())
                notice_item.id = notice_item.text
                self.notice_dic[notice_item.id] = notice_item
                md_list.add_widget(notice_item)

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

        scroll_view.add_widget(md_list)
        self.add_widget(scroll_view)
        if self.manager.get_screen("LoginScreen").ids.login_label.text == "Admin Login":
            self.add_widget(action_button)

    def create_notice(self, instance):
        self.manager.current = 'CreateNoticeScreen'

    def view_notice(self):
        for notice in self.notice_dic.values():
            if notice.state == 'down':
                self.manager.get_screen("ShowNoticeScreen").title = notice.text
                self.manager.get_screen("ShowNoticeScreen").text = notice.secondary_text
                notice.state = 'normal'
        self.manager.get_screen("ShowNoticeScreen").view_notice()
        if self.manager.get_screen("ShowNoticeScreen").title != 'No Notices':
            self.manager.current = 'ShowNoticeScreen'


class ShowNoticeScreen(Screen):

    def __init__(self, **kwargs):
        super(ShowNoticeScreen, self).__init__(**kwargs)

        self.title = ''
        self.text = ''
        self.delete_btn = MDIconButton(icon="delete", pos_hint={'center_x': 0.9, 'center_y': 0.92})
        self.delete_btn.bind(on_release=self.open_del_dialog)
        self.dialog = MDDialog(title="Are You Sure You Want To Delete This Notice?",
                               size_hint=(None, None),
                               _spacer_top=15,
                               width=(self.width - 50),
                               buttons=[MDFlatButton(text='Yes', on_release=self.delete_notice),
                                        MDFlatButton(text='No', on_release=self.close_dialog)]
                               )

    def open_del_dialog(self, instance):
        self.dialog.open()

    def add_del_btn(self):
        self.add_widget(self.delete_btn)

    def remove_del_btn(self):
        self.remove_widget(self.delete_btn)

    def view_notice(self):
        self.ids.notice_title.text = self.title
        self.ids.notice_text.text = self.text

    def delete_notice(self, instance):
        try:
            dataHandler.delete_query('notice_board', 'Notice_Title', self.ids.notice_title.text)
            self.title = dataHandler.fetch_notices()[-1][0]
            self.text = dataHandler.fetch_notices()[-1][1]
            self.manager.get_screen("NoticeScreen").notice_dic = {}
            self.manager.get_screen("NoticeScreen").clear_widgets()
            self.manager.get_screen("NoticeScreen").notice_dic = {}
            self.manager.get_screen("NoticeScreen").show_notices()
            self.manager.current = "NoticeScreen"
            toast("Notice Deleted Successfully")
            self.dialog.dismiss()

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def close_dialog(self, instance):
        self.dialog.dismiss()


class CreateNoticeScreen(Screen):

    def __init__(self, **kwargs):
        super(CreateNoticeScreen, self).__init__(**kwargs)

    def create_notice(self, notice_title, notice_text):
        try:
            notice_title = notice_title.capitalize()
            if not notice_title.isspace() and not notice_text.isspace() and notice_title != '' and notice_text != '':
                if len(notice_title) < self.ids.notice_title.max_text_length and len(
                        notice_text) < self.ids.notice_textfield.max_text_length:
                    dataHandler.add_notice(notice_title, notice_text)
                    self.ids.notice_title.text = ''
                    self.ids.notice_textfield.text = ''
                    toast('Notice Successfully Added!')
                else:
                    toast('Title should not exceed than 250 letters') if len(
                        notice_title) >= self.ids.notice_title.max_text_length else toast(
                        'Notice should not exceed than 990 letters')
            else:
                if notice_title.isspace():
                    toast('Title cannot be empty!')
                else:
                    toast('Notice cannot be empty!')

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")


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
    pass


class MainApp(MDApp):
    def build(self):
        self.title = "App By SIS"
        theme_color = dataHandler.query_app_data("theme_color", "static_app_data")[0][0]
        primary_palette = dataHandler.query_app_data("primary_palette", "static_app_data")[0][0]
        self.theme_cls.theme_style = theme_color
        self.theme_cls.primary_palette = primary_palette

        kvFile = Builder.load_file("app_design.kv")

        return kvFile

    def on_start(self):
        try:
            dataHandler.create_app_data()  # create static (on device memory) and dynamic (online ) app data
            dataHandler.set_database()
        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def change_theme_style(self):
        try:
            self.theme_cls.theme_style = (
                "Dark" if self.theme_cls.theme_style == "Light" else "Light"
            )
            dataHandler.update_app_data("static_app_data", 'theme_color', self.theme_cls.theme_style)

        except mysql.connector.errors.DatabaseError:
            toast("Please check your internet connection")

    def change_primary_palette(self, palette_color):
        self.theme_cls.primary_palette = palette_color
        dataHandler.update_app_data("static_app_data", 'primary_palette', palette_color)


MainApp().run()
