import pyautogui
import numpy as np
import threading
import time

import tkinter as tk
from datetime import datetime
import platform
import subprocess

import sys
import os

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)
# === НАСТРОЙКИ ===
REGION = (0, 175, 105, 70)
CHECK_INTERVAL = 5  # 5 сек

running = True
stop_sound_flag = False
next_check_in = CHECK_INTERVAL


def is_colorful(pixel, threshold=15):
    r, g, b = map(int, pixel[:3])
    return not (abs(r - g) < threshold and abs(r - b) < threshold and abs(g - b) < threshold)


def play_sound():
    global stop_sound_flag

    stop_sound_flag = False
    if(platform.system() == 'Windows'):
        import winsound
        winsound.PlaySound(resource_path("alert.wav"), winsound.SND_FILENAME | winsound.SND_ASYNC)
        while not stop_sound_flag:
            time.sleep(0.05)
    else:
        sound_path = resource_path("alert.wav")
        print(sound_path)
        print(os.path.exists(sound_path))
        process = subprocess.Popen(["afplay", sound_path])
        while not stop_sound_flag and process.poll() is None:
            time.sleep(0.05)
        process.terminate()
    while not stop_sound_flag:
        time.sleep(0.05)

    winsound.PlaySound(None, winsound.SND_PURGE)


def stop_sound():
    global stop_sound_flag
    stop_sound_flag = True
    winsound.PlaySound(None, winsound.SND_PURGE)
    log("🔇 Звук остановлен")


def check_screen():
    screenshot = pyautogui.screenshot(region=REGION)
    img = np.array(screenshot)

    for row in img:
        for pixel in row:
            if is_colorful(pixel):
                log("⚠️ Есть сообщение!")
                threading.Thread(target=play_sound, daemon=True).start()
                return

    log("✅ Нет сообщений")


def update_timer():
    global next_check_in, running

    if not running:
        return

    if next_check_in <= 0:
        check_screen()
        next_check_in = CHECK_INTERVAL

    timer_label.config(text=f"До проверки: {next_check_in} сек")
    next_check_in -= 1

    root.after(1000, update_timer)


def log(text):
    now = datetime.now().strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{now}] {text}\n")
    log_box.see(tk.END)


# === GUI ===
root = tk.Tk()
root.title("Мониторинг SD")

# ❗️ запрещаем разворот на весь экран
root.resizable(False, False)
root.attributes("-fullscreen", False)

# уменьшаем окно
root.geometry("360x200")

timer_label = tk.Label(root, text="До проверки: 180 сек", font=("Arial", 12))
timer_label.pack(pady=5)

stop_btn = tk.Button(root, text="Стоп звук", command=stop_sound, width=20)
stop_btn.pack(pady=5)

log_box = tk.Text(root, height=10, width=42)
log_box.pack(pady=5)

log("▶️ Программа запущена")

update_timer()
root.mainloop()