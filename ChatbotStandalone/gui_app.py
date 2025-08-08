import tkinter as tk
from tkinter import scrolledtext, font as tkfont
import pyttsx3
import threading
from main import initialize_chat, generate_response

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=25, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.radius = radius
        self.rect = None

    def draw_rounded_rect(self):
        width = self.winfo_width()
        height = self.winfo_height()
        self.delete("all")
        self.rect = self.create_rounded_rect(0, 0, width, height, self.radius, fill=self['bg'], outline="")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1, x1+r, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

class MusicBotGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.chat = initialize_chat()
        self.create_widgets()
        self.display_welcome()

        self.engine = pyttsx3.init()

    def setup_window(self):
        self.root.title("British Music Expert")
        self.root.geometry("800x600")
        self.root.configure(bg='#121212')

        self.bg_color = '#121212'
        self.text_color = '#e0e0e0'
        self.accent_color = '#bb86fc'
        self.input_bg = '#1e1e1e'
        self.chat_bg = '#1e1e1e'
        self.border_color = '#333333'

    def create_widgets(self):
        title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        text_font = tkfont.Font(family="Segoe UI", size=12)

        header = tk.Frame(self.root, bg=self.bg_color)
        tk.Label(header, text="BRITISH MUSIC EXPERT", font=title_font, bg=self.bg_color, fg=self.accent_color).pack(pady=10)
        header.pack(fill=tk.X)

        chat_frame = RoundedFrame(self.root, radius=15, bg=self.border_color)
        chat_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        chat_frame.bind("<Configure>", lambda e: chat_frame.draw_rounded_rect())

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=text_font, bg=self.chat_bg, fg=self.text_color, insertbackground=self.text_color, padx=15, pady=15, relief=tk.FLAT, highlightthickness=0)
        self.chat_display.pack(expand=True, fill=tk.BOTH)
        self.chat_display.config(state=tk.DISABLED)

        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        input_bg_frame = RoundedFrame(input_frame, radius=15, bg=self.border_color, height=50)
        input_bg_frame.pack(fill=tk.X)
        input_bg_frame.bind("<Configure>", lambda e: input_bg_frame.draw_rounded_rect())

        self.user_input = tk.Entry(input_bg_frame, font=text_font, bg=self.input_bg, fg=self.text_color, insertbackground=self.text_color, relief=tk.FLAT, highlightthickness=0, borderwidth=0)
        self.user_input.place(relx=0.01, rely=0.5, relwidth=0.85, relheight=0.8, anchor=tk.W)
        self.user_input.bind("<Return>", self.send_message)

        send_btn = tk.Button(input_bg_frame, text="Send", command=self.send_message, bg=self.accent_color, fg='black', activebackground='#9a67ea', activeforeground='white', relief=tk.FLAT, borderwidth=0, font=text_font)
        send_btn.place(relx=0.98, rely=0.5, relwidth=0.15, relheight=0.8, anchor=tk.E)

    def display_welcome(self):
        self.display_message("Bot", "Hello! Ask me about British music artists, genres, or city scenes.")

    def send_message(self, event=None):
        message = self.user_input.get().strip()
        if not message:
            return
        self.display_message("You", message)
        self.user_input.delete(0, tk.END)

        threading.Thread(target=self.handle_response, args=(message,)).start()

    def handle_response(self, message):
        response = generate_response(self.chat, message)
        self.display_message("Bot", response)

        self.engine.say(response)
        self.engine.runAndWait()

    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        if sender == "You":
            tag_name = "user_msg"
            self.chat_display.tag_config(tag_name, foreground=self.accent_color, font=('Segoe UI', 12, 'bold'))
        else:
            tag_name = "bot_msg"
            self.chat_display.tag_config(tag_name, foreground='#03dac6', font=('Segoe UI', 12))
        self.chat_display.insert(tk.END, f"{sender}: ", tag_name)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

# --- Main Application ---
if __name__ == "__main__":
    root = tk.Tk()
    root.tk_setPalette(background='#121212', foreground='#e0e0e0', activeBackground='#9a67ea', activeForeground='white')
    app = MusicBotGUI(root)
    root.mainloop()
