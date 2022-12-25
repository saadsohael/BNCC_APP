from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.lang import Builder

Builder.load_string("""
<Base>:
    Button:
        background_normal: 'normal.png'
        background_down: 'down.png'
        border: 30,30,30,30
""")


class Base(FloatLayout):
    pass

class ButtonsApp(App):
    def build(self):
        return Base()

if __name__ == "__main__":
    ButtonsApp().run()