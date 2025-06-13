import time
from pywinauto.application import Application
import os

app = Application(backend='uia').start(r"C:\\Program Files (x86)\Micromeritics\MicroActive\microactive.exe")
dlg = app.window(best_match='MicroActive Version 7.00')
error_file = open("error.txt", "a+")

directory = r'C:\Users\user\Downloads\2400\\'
folders = sorted([name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))])[1:]
folders = [f"\DATA{i}" for i in range(28, 41)]
for folder in folders:
    folder_path = r'C:\Users\user\Downloads\2400' + folder
    smp_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".smp")]
    for file in smp_files:
        try:
            dlg.menu_select("Reports->Start reports")
            time.sleep(1)
            file_dlg = app.window(best_match="Dialog", found_index=0)
            file_dlg.child_window(best_match="Имя файла:Edit").type_keys(folder_path+"\\"+file)
            file_dlg.child_window(best_match="Report", control_type="Button").click()
            time.sleep(1)
            file_dlg = app.window(best_match="Dialog", found_index=0)
            file_dlg.child_window(best_match="OK", control_type="Button").click()
            time.sleep(1)
            file_dlg = app.window(best_match="Dialog", found_index=0)
            file_dlg.child_window(best_match="OK", control_type="Button").click()
            time.sleep(1)
        except Exception as e:
            try:
                app.kill()
            except Exception as e:
                pass
            time.sleep(5)
            app = Application(backend='uia').start(r"C:\\Program Files (x86)\Micromeritics\MicroActive\microactive.exe")
            dlg = app.window(best_match='MicroActive Version 7.00')
            error_file.write(f"{folder} - {file}\n")
            continue
error_file.close()