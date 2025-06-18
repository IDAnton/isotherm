import time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import TimeoutError
from os import listdir
from os.path import isfile, join


class App:
    def __init__(self):
        self.app = Application(backend='uia').start(r"C:\\Program Files (x86)\VersaWin\VersaWin.exe")
        time.sleep(0.3)
        self.window = self.app.window(best_match='Quantachrome')

    def process_file(self, name):
        time.sleep(0.3)
        try:
            self.window.wait("ready")
        except Exception as e:
            time.sleep(1)
            self.window.wait("ready")
        time.sleep(0.3)
        self.window.menu_select("0")
        self.window.menu_select("0")
        time.sleep(0.3)
        send_keys('{DOWN}')

        time.sleep(0.1)
        send_keys('{ENTER}')
        file_dlg = self.app.window(best_match="Открыть", found_index=0)
        file_dlg.wait("ready")
        time.sleep(0.3)
        file_dlg.child_window(best_match="Имя файла:Edit").type_keys(name)
        time.sleep(0.3)
        file_dlg.child_window(best_match="Открыть4", control_type="Button").click()
        isotherm_window = self.app.window(best_match='Dialog')
        isotherm_window.click_input(button='right')
        time.sleep(0.1)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        # for i in range(13): DFT
        #     time.sleep(0.3)
        #     send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        time.sleep(0.1)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        # windows = app.windows()
        # print([w.window_text() for w in windows])
        # confirmWin = app.window(best_match=u'Quantachrome® VersaWin™ Confirmation')  # Check your window header object name.
        # # Use timeout based on average pop up time in your application.
        # if confirmWin.exists(timeout=10, retry_interval=1):
        #     confirmWin.set_focus()
        #     yesBtn = confirmWin[u'&Да']
        #     # Check the object name of the Yes button. You can use Swapy tool(It is deprecated but it works, else you can use inspect.exe)
        #     yesBtn.click()

        ######################
        isotherm_window.click_input(button='right')
        for i in range(10):
            send_keys('{DOWN}')
            time.sleep(0.1)
        send_keys('{ENTER}')

        save_dlg = self.app.window(best_match="Name file", found_index=0)
        save_dlg.child_window(best_match="Сохранить4", control_type="Button").click()

        report_dlg = self.app.window(best_match="Dialog", found_index=0)
        report_dlg.child_window(best_match="Закрыть", control_type="Button").click()
        isotherm_window.child_window(best_match="Закрыть").click()
        time.sleep(0.3)


def get_unprocessed(files, redy_files):
    files_ = set([f.replace(".QPS", "").replace(".qps", "") for f in files])
    redy_files_ = set([f.replace(".txt", "").replace(" (Isotherm)", "") for f in redy_files])
    rest = files_ - redy_files_
    rest_files = [f + ".QPS" for f in rest]
    return rest_files


if __name__ == "__main__":
    QPS_path = r"C:\QCdata\Physisorb"
    files = [f for f in listdir(QPS_path) if isfile(join(QPS_path, f)) and (f[-3:]).lower()=="qps"]
    path_to_ready_files = r"C:\QCdata\Export"
    redy_files = [f for f in listdir(path_to_ready_files) if isfile(join(path_to_ready_files, f))]
    files_to_process = get_unprocessed(files, redy_files)
    print("files_to_process: ", len(files_to_process))
    print(files_to_process)
    #quit()
    app = App()
    i = 0
    while i < len(files_to_process):
        try:
            app.process_file(files_to_process[i])
            i += 1
            print(i)
        except Exception as e:
            print("error:", e)
            i += 1
            try:
                app.app.kill()
                app = App()
                files_to_process = get_unprocessed(files, redy_files)
            except Exception as e:
                print("error while kill", e)