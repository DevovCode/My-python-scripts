import customtkinter as ctk
import ollama
from focus_song import start_music_service
from focus_song import change_volume, save_music_volume, MUSIC_VOLUME

def Robbie_Ai(user_text):
    instructions = """
        Ты — программный роутер команд. Тебе ЗАПРЕЩЕНО общаться как человек.
        На любой запрос ты должен вернуть строго один из тегов:

        Если просят смонтировать, обрезать или склеить видео — "[INSTALLATION]"
        Если просят включить или выключить музыку — "[MUSIC]"
        Во всех остальных случаях (приветствия, вопросы, болтовня, то, чего нет в списке) — "[NEW]"
        
        Выводи ТОЛЬКО тег в квадратных скобках. Никаких других символов. Не выдумывай теги, пиши только то, что есть в списке».
    """
    try:
        if user_text:
            response = ollama.chat(model='qwen2.5:1.5b', messages=[{'role': 'system', 'content': instructions}, {'role': 'user', 'content': user_text}], options={'temperature': 0} )     # Отпровляем Robbie наш запрос.
            Robbie_response = response['message']['content'].strip()        # Достаем из ответа Robbie чистый текст ответа.
            return Robbie_response
    except Exception as e:
        return ["ERROR"]

def send_message(teg):
    user_text = chat_box.get() # Берем 
    if user_text.strip():      # Проверяем, что пользователь не отправил пустую строку
        robbie_response = Robbie_Ai(user_text)  # Передаем робби наш текст и получаем ответ
        print(f"Ответ: {robbie_response}")
        chat_box.delete(0, "end") # Очищаем поле ввода от 0-го символа до самого конца ("end")
        if "[MUSIC]" in robbie_response:
            music_window.pack(pady=20)
            start_music_service()

app = ctk.CTk()                 # Создаем переменную (например, app) и присваиваем ей сам объект окна ctk.CTk().
app.title("Robbie AI")          # У переменной app вызываем метод .title(...) и в кавычках передаем название окна
app.geometry("470x510")         # У app вызываем метод .geometry(...) и в кавычках передаем ширину и высоту через латинскую букву x
app.resizable(False,False)      # Делаем так что бы окно нельзя было растянуть, где Первый False — изменение по ширине (width).Второй False — изменение по высоте (height).

chat_box = ctk.CTkEntry(app, width=430, height=40, placeholder_text="Спросить у Robbie AI")
chat_box.pack(side="bottom", pady=20)       # pady=10 — это отступ по вертикали
chat_box.bind("<Return>", send_message)

music_window = ctk.CTkFrame(app, width=430 , height=40)
volume_slider = ctk.CTkSlider(music_window, from_=0.0, to=1.0, command=change_volume)
volume_slider.set(MUSIC_VOLUME)
volume_slider.pack(pady=10)

text_lable_value = MUSIC_VOLUME
text_lable = ctk.CTkLabel(music_window, text= MUSIC_VOLUME)
text_lable.pack(pady=10)    # Что бы элемент отображался (но пока родитель не отоброжается то и этот элемент тоже не отобразится).

app.mainloop()              # В самом конце вызываем у app метод .mainloop(), чтобы окно не закрывалось сразу, а ждало наших действий.
