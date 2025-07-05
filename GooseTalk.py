import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog, END
from PIL import Image

set_appearance_mode("light")
set_default_color_theme("blue")


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title("Chat Client")
        self.username = "Artem"
        self.configure(fg_color="#e0f0ff")

        self.menu_icon = CTkImage(Image.open("9ec4d7bdf3498ad7f07d0d0dc6584d05.jpg"), size=(23, 23))

        # Змінні для меню
        self.is_show_menu = False
        self.menu_animation_speed = 5  # Швидкість анімації

        self.setup_ui()
        self.connect_to_server()

        try:
            self.add_message("Демонстрація відображення зображення:",
                             CTkImage(Image.open('Logika.png'), size=(100, 100)))
        except FileNotFoundError:
            self.add_message("Не вдалося завантажити демонстраційне зображення")

    def setup_ui(self):
        self.menu_frame = CTkFrame(self, width=60, height=300, fg_color="#cce6ff")  # Початкова ширина 60
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.btn = CTkButton(self, image=self.menu_icon, text='', command=self.toggle_show_menu,
                             width=30, fg_color="#99ccff")
        self.btn.place(x=0, y=0)

        self.chat_field = CTkScrollableFrame(self, fg_color="#e0f0ff")
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40,
                                      fg_color="white", border_color="#66b2ff", border_width=2)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message,
                                     fg_color="#3399ff", text_color="white")
        self.send_button.place(x=0, y=0)
        self.open_img_button = CTkButton(self, text='📷', width=50, height=40, command=self.open_image,
                                         fg_color="#3399ff", text_color="white")
        self.open_img_button.place(x=0, y=0)

        self.after(50, self.adaptive_ui)

    def toggle_show_menu(self):
        """Перемикає стан меню при натисканні кнопки"""
        self.is_show_menu = not self.is_show_menu

        if self.is_show_menu:
            # Створюємо елементи меню при першому відкритті
            if not hasattr(self, "label"):
                self.label = CTkLabel(self.menu_frame, text="Ім'я:", text_color="black")
                self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...",
                                      fg_color="white", border_color="#66b2ff")
                self.save_button = CTkButton(self.menu_frame, text="Зберегти",
                                             command=self.save_name,
                                             fg_color="#3399ff", text_color="white")

            # Показуємо елементи
            self.label.pack(pady=30)
            self.entry.pack()
            self.save_button.pack()

        # Запускаємо анімацію
        self.animate_menu()

    def animate_menu(self):
        """Анімує зміну ширини меню"""
        current_width = self.menu_frame.winfo_width()

        if self.is_show_menu and current_width < 200:  # Відкриваємо
            new_width = min(current_width + self.menu_animation_speed, 200)
            self.menu_frame.configure(width=new_width)
            self.after(10, self.animate_menu)
        elif not self.is_show_menu and current_width > 60:  # Закриваємо
            new_width = max(current_width - self.menu_animation_speed, 60)
            self.menu_frame.configure(width=new_width)
            if new_width == 60 and hasattr(self, "label"):
                # Ховаємо елементи при повному закритті
                self.label.pack_forget()
                self.entry.pack_forget()
                self.save_button.pack_forget()
            self.after(10, self.animate_menu)

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.after(50, self.adaptive_ui)

    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='#b3d9ff')
        message_frame.pack(pady=5, anchor='w')
        wraplength_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        if not img:
            CTkLabel(message_frame, text=message, wraplength=wraplength_size,
                     text_color='black', justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wraplength_size,
                     text_color='black', image=img, compound='top', justify='left').pack(padx=10, pady=5)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("Помилка відправки повідомлення")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{author}: відправив зображення: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
        else:
            self.add_message(line)

    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()