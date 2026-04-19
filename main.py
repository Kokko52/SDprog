import pyautogui
import numpy as np
import threading
import time
import winsound
import tkinter as tk
from datetime import datetime

import sys
import os


def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


# === НАСТРОЙКИ ===
REGION = (0, 160, 200, 110)
CHECK_INTERVAL = 5

MIN_PIXELS = 1  # сколько пикселей синего нужно для срабатывания

stop_sound_flag = False
next_check_in = CHECK_INTERVAL
sound_playing = False


def play_sound():
    global stop_sound_flag, sound_playing

    if sound_playing:
        return

    sound_playing = True
    stop_sound_flag = False

    winsound.PlaySound(
        resource_path("alert.wav"),
        winsound.SND_FILENAME | winsound.SND_ASYNC
    )

    while not stop_sound_flag:
        time.sleep(0.05)

    winsound.PlaySound(None, winsound.SND_PURGE)
    sound_playing = False


def stop_sound():
    global stop_sound_flag
    stop_sound_flag = True
    winsound.PlaySound(None, winsound.SND_PURGE)
    log("🔇 Звук остановлен")


# === ГЛАВНАЯ ЛОГИКА (СИНИЙ ДЕТЕКТОР) ===
def check_screen():
    screenshot = pyautogui.screenshot(region=REGION)
    img = np.array(screenshot)

    # RGB каналы
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2] 

    # стабильный фильтр синего
    mask = (b > 200) & (b > r + 70) & (b > g + 70)

    pixels = np.sum(mask)

    if pixels > MIN_PIXELS:
        log(f"⚠️ СИНИЙ сигнал: {pixels} пикселей")
        threading.Thread(target=play_sound, daemon=True).start()
    else:
        log("✅ Новое сообщение")


def update_timer():
    global next_check_in

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

root.resizable(False, False)
root.geometry("360x200")

timer_label = tk.Label(root, text="До проверки: 5 сек", font=("Arial", 12))
timer_label.pack(pady=5)

stop_btn = tk.Button(root, text="Стоп звук", command=stop_sound, width=20)
stop_btn.pack(pady=5)

log_box = tk.Text(root, height=10, width=42)
log_box.pack(pady=5)

log("▶️ Программа запущена")

update_timer()
root.mainloop()