import time
import win32gui
import pygame
import random
import os
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
import threading # Второй поток (потому что 2 вечных цикла: app.mainloop() и while True:)
import pythoncom # Без нее выдаст ошибку.
import json

MUSIC_VOLUME = 0.08  # из 1.0
SMOOTHNESS_START = 0.1
SMOOTHNESS_FINISH = 0.2
FALL_ASLEEP = 10
IGNORED_PROCESSES = ["obs64.exe", "obs32.exe", "code.exe"] # Список процессов, которые скрипт должен ИГНОРИРОВАТЬ (не считать за чужую музыку)
BASE_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(BASE_DIR, "robbie_settings.json")

def is_system_audio_playing():
    my_id = os.getpid()  # Возвращает число например 12480
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            if session.Process and session.ProcessId != my_id:
                proc_name = session.Process.name().lower()
                if proc_name in IGNORED_PROCESSES:
                    continue
                meter = session._ctl.QueryInterface(IAudioMeterInformation)
                get_meter = meter.GetPeakValue()
                if get_meter >= 0.001:
                    print("Шумит процесс:", session.Process.name(), "с громкостью:", get_meter)
                    return True
        except:
            pass # # Пропускаем сбойную сессию и работаем дальше
    return False

my_id = os.getpid()

target_app = [
    # --- Движки и разработка игр ---
    "Unity",
    "Studio",
    "Godot",
    "Unreal Engine",
    
    # --- Кодинг и среда разработки (IDE) ---
    "Visual Studio Code",
    "Code::Blocks",
    "Visual Studio",
    "PyCharm",
    
    # --- 3D-моделирование и арт ---
    "Blender",
    "Blockbench",
    "Photoshop",
    "Krita",
    "Substance 3D",
    
    # --- Монтаж видео (для девлогов) ---
    "CapCut",
    "DaVinci Resolve",
    "Premiere Pro",
    
    # --- Браузер: Поиск, документация и ИИ ---
    "Google",
    "GitHub",
    "Stack Overflow",
    "ChatGPT",
    "Claude",
    "DeepSeek",
    "Roblox Creator Hub",
    "Unity Documentation",
    "Habr",
    
    # --- Публикация игр ---
    "itch.io",

    "Этот ПК",          # Русское название "This PC"
    "This PC",          # Английское название
    "Проводник",        # Сам системный процесс File Explorer
    "File Explorer",
    "(C:)",             # Системный диск C
    "(D:)",             # Твой локальный диск D (Новый том)
    "Загрузки",         # Папка Downloads
    "Downloads",
    "Рабочий стол",     # Desktop
    "Desktop",

    "Task Manager",      # Английское название (как на твоём скриншоте)
    "Диспетчер задач",   # Русское название
    "zapret-discord-youtube-main",

    # --- Системные утилиты и терминалы ---
    "Run",               # Окно Win+R (Run)
    "Выполнить",
    "cmd",               # Командная строка
    "cmd.exe",
    "Administrator",     # Когда CMD запущен от админа
    "Командная строка",
    "AdGuard VPN",
    "OBS",
    "Robbie",
    ]

music_list = [
    os.path.join(BASE_DIR, "Aria_math.mp3"),
    os.path.join(BASE_DIR, "Comfort Chain.mp3"),
    os.path.join(BASE_DIR, "Golden_Brown.mp3"),
    os.path.join(BASE_DIR, "Roi_instrumental.mp3"),
    os.path.join(BASE_DIR, "Volume_Alpha.mp3"),
]

losing_music = [

]

def save_music_volume():
    global MUSIC_VOLUME
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file_object:
            all_setings = json.load(file_object)
            return all_setings.get("Music_Valume", 0.08)
    return 0.08
    

is_playing = False
time_control = 0
real_fall_sleep = FALL_ASLEEP * 2

save_music_volume()
pygame.mixer.init() # готовим к музыке. 

def generate_random_music():
    global music_list, losing_music # без этого скрипт думает что music_list, losing_music это локальные переменные.

    if len(music_list) <= 0:
        music_list = losing_music.copy()
        losing_music.clear()

    random_music = random.choice(music_list)

    losing_music.append(random_music)
    music_list.remove(random_music)

    pygame.mixer.music.load(random_music)
    pygame.mixer.music.play()

def start_focus_music():
    global is_playing, time_control
    save_music_volume()
    pythoncom.CoInitialize() # Без нее выдаст ошибку.
    while True:
        
        has_other_audio = is_system_audio_playing() # Нам нужно знать, проигрывается ли сейчас сторонний звук

        get_lose_music = pygame.mixer.music.get_busy() # Тут хрониться состояние звука (закончился или нет).

        if get_lose_music == False and is_playing == True:
            current_pause = random.randint(20, 30)
            time.sleep(current_pause)
            generate_random_music()
        
        found =  False
        active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())

        for app in target_app:
            if app in active_window:
                found = True
                break
        if found == True and not has_other_audio:
            time_control = 0
            if is_playing == False:
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.unpause()
                for step in range(0, 11): # генерирует числа в обратную сторону
                    volume = step / 10 * MUSIC_VOLUME # Превращает 10 в 1.0, 9 в 0.9, ... 0 в 0.0
                    pygame.mixer.music.set_volume(volume)
                    time.sleep(SMOOTHNESS_START)
                is_playing = True
        else:
            time_control += 1
            if has_other_audio:
                if is_playing == True:
                        pygame.mixer.music.set_volume(0)
                        time.sleep(SMOOTHNESS_FINISH)
                        pygame.mixer.music.pause()
                        is_playing = False
            if time_control >= real_fall_sleep:
                if is_playing == True:
                    for step in range(10, -1, -1): # генерирует числа в обратную сторону
                        volume = step / 10 * MUSIC_VOLUME # Превращает 10 в 1.0, 9 в 0.9, ... 0 в 0.0
                        pygame.mixer.music.set_volume(volume)
                        time.sleep(SMOOTHNESS_FINISH)
                    pygame.mixer.music.pause()
                    is_playing = False
        time.sleep(0.5)

is_music_running = False
def start_music_service():

    global is_music_running
    if not is_music_running:
        is_music_running = True
        music_thread = threading.Thread(target=start_focus_music, daemon=True) # Создаем поток и указываем, какую функцию ему выполнять. daemon=True: Если пользователь закроет главное окно программы на крестик, фоновый поток с музыкой автоматически выключится вместе с окном.
        music_thread.start()

def change_volume(val):
    global MUSIC_VOLUME
    MUSIC_VOLUME = float(val)
    if is_playing == True:
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
    save_format = {"Music_Valume": MUSIC_VOLUME}
    with open(SETTINGS_FILE, "w") as file_object:
        json.dump(save_format, file_object, indent=4)

def off_music():
    global is_playing
    is_playing = True

def on_music():
    global is_playing
    is_playing = False
