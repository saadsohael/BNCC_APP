from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder


class WindowManager(ScreenManager):
    pass


class LogInScreen(Screen):
    def buttonClick(self):
        number = int(self.ids.number.text)
        number += 1
        self.ids.number.text = str(number)


class AdminLogScreen(Screen):
    pass


class CadetDash(Screen):
    pass


class AdminDash(Screen):
    pass


kvFile = Builder.load_file("app_kvFile.kv")


class BNCCAPP(App):
    def build(self):
        return AdminLogScreen()
        # return kvFile


BNCCAPP().run()
