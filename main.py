import os
import json
import numpy as np
from PIL import Image as PILImage
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

class PlantApp(BoxLayout):
    def __init__(self, **kwargs):
        super(PlantApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        with open('labels.txt', 'r', encoding='utf-8') as f:
            self.labels = [l.strip() for l in f.readlines()]

        with open('care_guide.json', 'r', encoding='utf-8') as f:
            self.care_guide = json.load(f)

        self.interpreter = tflite.Interpreter(model_path='model.tflite')
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.img_widget = Image(source='', size_hint=(1, 0.45))
        self.add_widget(self.img_widget)

        self.btn_select = Button(text='Выбрать фото листа', size_hint=(1, 0.1),
                                  background_color=(0.1, 0.6, 0.3, 1))
        self.btn_select.bind(on_press=self.open_file_chooser)
        self.add_widget(self.btn_select)

        self.info_label = Label(
            text='Загрузите фото листа для анализа и рекомендаций по уходу',
            size_hint=(1, 0.45), halign='center', valign='middle'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.add_widget(self.info_label)

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path='/storage/emulated/0/', filters=['*.jpg', '*.jpeg', '*.png'])
        content.add_widget(filechooser)

        btn_layout = BoxLayout(size_hint_y=None, height=50)
        select_btn = Button(text='Выбрать')
        cancel_btn = Button(text='Отмена')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Выберите фотографию', content=content, size_hint=(0.9, 0.9))
        select_btn.bind(on_press=lambda x: self.load_image(filechooser.selection, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def load_image(self, selection, popup):
        popup.dismiss()
        if selection:
            img_path = selection[0]
            self.img_widget.source = img_path
            self.classify_image(img_path)

    def classify_image(self, img_path):
        try:
            img = PILImage.open(img_path).convert('RGB').resize((224, 224))
            arr = np.array(img, dtype=np.float32)
            arr = (arr / 127.5) - 1.0
            arr = np.expand_dims(arr, axis=0)

            self.interpreter.set_tensor(self.input_details[0]['index'], arr)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

            class_idx = int(np.argmax(output))
            confidence = float(output[class_idx]) * 100
            class_key = self.labels[class_idx]

            info = self.care_guide.get(class_key, {"name": class_key, "watering": "-", "care": "-"})

            result_text = f"Результат: {info[\'name\']} ({confidence:.1f}%)\n\n" \
                          f"Полив: {info[\'watering\']}\n" \
                          f"Уход: {info[\'care\']}"
            self.info_label.text = result_text
        except Exception as e:
            self.info_label.text = f"Ошибка анализа: {str(e)}"

class PlantCareApp(App):
    def build(self):
        return PlantApp()

if __name__ == '__main__':
    PlantCareApp().run()
