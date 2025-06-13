import time
from pywinauto.application import Application
from os import listdir
from os.path import isfile, join



folder_list = [f"\DATA{i}" for i in range (1, 28)]
f = open("log.txt", "a+")

def open_program():
    app = Application(backend='uia').start(r"C:\\Program Files (x86)\Micromeritics\MicroActive\microactive.exe")
    window = app.window(best_match='MicroActive')
    return app, window

app, window = open_program()

for folder in folder_list:
    SMP_FOLDER_PATH = r"C:\Users\user\Downloads\2400"
    SMP_FOLDER_PATH += folder

    SMP_files = [f for f in listdir(SMP_FOLDER_PATH) if isfile(join(SMP_FOLDER_PATH, f)) and f[-3:] == "SMP"]
    for file in SMP_files:
        try:
            window.menu_select("Reports->StartReport")
            file_dlg = app.window(best_match='Dialog')
            file_dlg.child_window(best_match="Имя файла:Edit").type_keys(SMP_FOLDER_PATH+'\\'+file)
            file_dlg.child_window(best_match="Report", control_type="Button").click()
            report_settings = app.window(best_match="Dialog")
            report_settings.child_window(best_match="OK", control_type="Button").click()
            report_settings2 = app.window(best_match="Dialog")
            report_settings.child_window(best_match="OK", control_type="Button").click()
        except Exception as e:
            print(e)
            time.sleep(5)
            app.kill()
            time.sleep(5)
            app, window = open_program()
            time.sleep(5)
            f.write(SMP_FOLDER_PATH + file + "\n")
            continue
f.close()