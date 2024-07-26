import fileinput
import platform
import webbrowser

import speech_recognition as sr
import pyttsx3
import datetime
from fuzzywuzzy import fuzz
import random
from os import system
import sys
from psutil import virtual_memory as memoru
import psutil
from os import system
from PyQt5 import QtWidgets, QtCore
import threading
import interface


class Assistant(QtWidgets.QMainWindow, interface.Ui_MainWindow, threading.Thread):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_thread)
        self.pushButton_2.clicked.connect(self.stop)
        self.working=False

        self.rec = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self.assistantVoice = "Vitaliy-ng"

        self.names = ["помoщник", "рабик", "бро", "даров", "денни"]
        # self.timeCMDE = ["скок время", "че по чем", "который час"]
        self.ndels = ["лан", "пожалуста", "пж", "спс"]

        self.cmds = {("который час", "че по чем", "который час"): self.time,
                     ("ку", "очнись", "хей", "привет"): self.hello,
                     ("поки", "свали", "до завтра", "пока"): self.quite,
                     ("отруби себя", "выключи комп", "смена кончилась давай домой", "розетка сломалась"): self.shut,
                     ("добавить задачу",): self.task_planner,
                     ("список задач",): self.task_list,
                     ("че по местам", "скок места", "система какая", "системные компоненты"): self.system_info}

    def start_thread(self):
        try:
            self.hello()
            self.working = True
            self.thread = threading.Thread(target=self.main)
            self.thread.start()

        except Exception as e:
            print('error: ', e)
            print('Type: ', type(e))

    def listen(self):

        # return "бро пока"
        text = ''
        # return "бро который час"
        with sr.Microphone() as sourse:

            print("говори, я готов...")
            self.rec.adjust_for_ambient_noise(sourse)
            audio = self.rec.listen(sourse)
            try:
                text = self.rec.recognize_google(audio, language="ru-RU")
                text = text.lower()
            except sr.UnknownValueError:
                pass

            print(text)
            return text

    def time(self):
        now = datetime.datetime.now()
        text = "сейчас " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
        print(text)
        self.talk(text)

    def talk(self, speech):
        self.engine.setProperty("voice", "ru")
        self.engine.setProperty("rate", 175)
        self.engine.setProperty("volume", 0.7)
        self.engine.setProperty("stress_maker", True)

        for voice in self.voices:
            if voice.name == self.assistantVoice:
                self.engine.setProperty("voice", voice.id)

        if speech != '':
            item = QtWidgets.QListWidgetItem()
            # item.setTextAlignment(QtCore.Qt.Alignment)
            item.setText("помощник: " + speech)
            self.listWidget.addItem()
            self.listWidget.scrollToBottom()

        self.engine.say(speech)
        self.engine.runAndWait()
        print(speech)

    def cleaner(self, text):
        # print("text = ", text)
        cmd = ''
        for name in self.names:
            # print(name)
            if text.startswith(name):
                # print("111111111111")
                cmd = text.replace(name, "").strip()
        # print("cmd = " ,cmd)

        for i in self.ndels:
            cmd = cmd.replace(i, "").strip()
            cmd = cmd.replace(" ", " ").strip()
        # print("cmd = " ,cmd)
        return cmd

    def recognizer(self):
        text = self.listen()
        # print("text___ = ", text)
        cmd = self.cleaner(text)

        if cmd.startswith(("открой", "перенеси в", "запусти")):
            self.opener(text)

        for tasks in self.cmds:
            for task in tasks:
                if fuzz.ratio(task, cmd) >= 85:
                    self.cmds[tasks]()

    def hello(self):
        text = ["здравия желаю, мой господин", "ку", "а теперь выйди, и зайди нормально", "прив", "хай кент",
                "отстань, я сплю"]
        say = random.choice(text)
        self.talk(say)

    def quite(self):
        text = ["ааапока", "ааа ок пок", " ааада вали ты уже я сплю", "ааадо завтра мой господин"]
        say = random.choice(text)
        self.talk(say)
        self.engine.stop()
        exit(0)

    def shut(self):
        self.talk("ты уверен маленький подлец")
        text = self.listen()
        print(text)
        if fuzz.ratio(text, "да") > 70:
            self.talk("ну лан поки")
            system("shutdown /s /f /t 10 /c  у тя комп завис лошок")
        else:
            self.talk("действие завершено")

    def opener(self, task):
        link = {("кинопоиск"): "https://www.kinopoisk.ru/",
                ("труба", "машина времени", "ютубчик", "youtube"): "https://www.youtube.com/?app=desktop&hl=ru"}
        task = task.split()
        for t in task:
            for vals in link:
                for word in vals:
                    if fuzz.ratio(word, t) > 70:
                        webbrowser.open(link[vals])
                        self.talk("открываю" + t)
                        break

    def task_planner(self):
        self.talk("что добавить в список задач?")
        task = self.listen()

        file = open("TODO.txt", "a", encoding='utf-8')
        task = task + '\n'
        file.write(task)
        file.close()
        self.talk(f"задача{task}добавлена")

    def task_list(self):
        try:
            file = open("TODO.tpx", "r", encoding='utf-8')
            tasks = file.read()
            file.close()

            if tasks == '':
                self.talk("у вас нет задач")







            else:
                text = "список задач:\n" + tasks
                self.talk(text)



        except:
            self.talk("у вас нет задач")

    def task_cleaner(self):
        # file = open("TODO.txt,w")
        pass

    def disk_usage(self):
        total, used, free, percent = psutil.disk_usage("/")
        total = total // (10 ** 9)
        used = used // (10 ** 9)
        free = used // (10 ** 9)
        percent = round(percent)
        text = f"всего{total} места, занято - {used},свободно - {free},это {percent} процентов"

    def system_info(self):
        text = ''
        os_name = platform.system() + " " + platform.release()
        text += 'опера на комп: ' + os_name + '\n'

        processor_name = platform.processor()
        processor_cores = psutil.cpu_count(logical=False)
        processor_freq = psutil.cpu_freq().current

        text += "процессор" + processor_name + "\n"
        text += "колличество ядер" + str(processor_freq) + "\n"

        mem_info = psutil.virtual_memory()
        mem_total = mem_info.total // 10 ** 6
        mem_used = mem_info.used // 10 ** 6
        text += f"оперативная память: {mem_total} используется: {mem_used}\n"

        print(text)
        self.talk(text)

    def main(self):
        while self.working:
            try:
                self.recognizer()
            except Exception as ex:
                print(ex)
    def stop(self):
        self.working = False
        self.quite()



if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = Assistant()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        print(e)

# # ass = Assistant()
# # ass.system_info()
#
# while True:
#     ass = Assistant()
#     ass.recognizer()
