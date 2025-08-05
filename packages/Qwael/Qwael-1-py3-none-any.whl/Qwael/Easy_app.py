from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

class Easy_App:
    def open(self, add=()):
        if add:
            def Labell(txt="", x=200, y=100, sizing=20):
                class Ekran(FloatLayout):
                    def _init_(self, **kwargs):
                        super(Ekran, self)._init_(**kwargs)
                        layout = BoxLayout(orientation="vertical", padding=(30), spacing=(20))
                        
                        label = Label(text=txt, pos_hint={"x": 0.0, "y": 0.0}, 
                                      size_hint=(None, None), size=(x, y), 
                                      font_size=f"{sizing}sp")
                        layout.add_widget(label)
                        self.add_widget(layout)

                return Ekran

    def start_app(self, ekran_class):
        
        class Uygulama(App):
            def build(self):
                return ekran_class()  

        if __name__ == "__main__":
            Uygulama().run()