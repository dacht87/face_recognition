import csv
import os.path
import subprocess
import tkinter as tk
from datetime import datetime

import cv2
import util
from PIL import Image, ImageTk


def gstreamer_pipeline():
    return "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=640, height=480, format=NV12, framerate=30/1 ! nvvidconv flip-method=0 ! video/x-raw, width=640, height=480, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=300)
        self.login_new_user_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                     self.register_new_user, fg='black')
        self.login_new_user_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        # Cargar el clasificador Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            print("Error: No se pudo cargar el clasificador Haarcascade")
            raise Exception("No se pudo cargar el clasificador Haarcascade")

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 750)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Guardamos la imagen más reciente
        self.most_recent_capture_arr = frame.copy()
        img_ = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convertir imagen a escala de grises para detección de rostros
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Guardar temporalmente la imagen para el reconocimiento facial
        unknown_img_path = './.tmp.jpg'
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        # Ejecutar el reconocimiento facial
        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
        name = output.split(',')[1][:-5]

        # Dibujar rectángulos y nombres
        for (x, y, w, h) in faces:
            cv2.rectangle(img_, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_, name if name not in ['unknown_person', 'no_persons_found'] else "Unknown", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Convertimos a formato PIL y actualizamos la imagen en la interfaz
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)
        self._label.after(20, self.process_webcam)

    def login(self):
        # Este método ahora solo muestra un mensaje de bienvenida
        util.msg_box('Welcome back!', 'You are already logged in.')

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")
        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)
        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)
        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)
        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, input username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")
        cv2.imwrite(os.path.join(self.db_dir, f'{name}.jpg'), self.most_recent_capture_arr)
        util.msg_box('Success', 'User was registered')
        self.register_new_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()