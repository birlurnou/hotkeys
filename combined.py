import os
import winreg
import subprocess
import json
import webbrowser
import keyboard
import threading
import time

def get_installed_browsers():
    browsers = {}

    # Поиск в реестре (программы из установщика Windows)
    try:
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
        ]

        for reg_path in reg_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if subkey_name.lower().endswith('.exe'):
                                browser_name = subkey_name[:-4].lower()

                                subkey_path = f"{reg_path}\\{subkey_name}"
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                                    try:
                                        exe_path, _ = winreg.QueryValueEx(subkey, "")
                                        if exe_path and os.path.exists(exe_path):
                                            if any(browser in browser_name for browser in
                                                   ['chrome', 'firefox', 'edge', 'opera', 'brave', 'vivaldi',
                                                    'safari']):
                                                browsers[browser_name] = exe_path
                                    except:
                                        pass
                            i += 1
                        except OSError:
                            break
            except:
                pass
    except Exception as e:
        print(f"Ошибка при чтении реестра: {e}")

    # Проверка стандартных путей установки
    standard_paths = [
        # Chrome
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # Firefox
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        # Edge
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        # Opera
        r"C:\Program Files\Opera\launcher.exe",
        r"C:\Users\{}\AppData\Local\Programs\Opera\launcher.exe".format(os.environ.get('USERNAME', '')),
        # Brave
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        # Vivaldi
        r"C:\Users\{}\AppData\Local\Vivaldi\Application\vivaldi.exe".format(os.environ.get('USERNAME', '')),
        # Яндекс.Браузер
        r"C:\Users\{}\AppData\Local\Yandex\YandexBrowser\Application\browser.exe".format(
            os.environ.get('USERNAME', '')),
    ]

    for path in standard_paths:
        if os.path.exists(path):
            browser_name = os.path.basename(path).replace('.exe', '').lower()
            browsers[browser_name] = path

    # Поиск через where (если браузер в PATH)
    browser_names = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe']
    for browser_exe in browser_names:
        try:
            result = subprocess.run(['where', browser_exe],
                                    capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and os.path.exists(line):
                        browser_name = os.path.basename(line).replace('.exe', '').lower()
                        browsers[browser_name] = line
        except:
            pass

    return browsers


def get_default_browser():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                            rf"{prog_id}\shell\open\command") as key:
            command, _ = winreg.QueryValueEx(key, "")

            path = command.strip('"').split('"')[0] if '"' in command else command.split()[0]

            path = path.strip('"')

            if '%' in path:
                for env_var in ['ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA', 'APPDATA']:
                    if f'%{env_var}%' in path:
                        path = path.replace(f'%{env_var}%', os.environ.get(env_var, ''))

            return path
    except Exception as e:
        print(f"Ошибка при получении браузера по умолчанию: {e}")
        return None


# чтение данных из json
with open('data.json', 'r', encoding='utf-8') as f:
    hotkeys = json.load(f)

browsers = {}
default_browser = ''
default_browser_name = ''

try:
    # все установленные браузеры
    browsers = fb.get_installed_browsers()
    # браузер, который выбран по умолчанию
    default_browser = fb.get_default_browser()
    # имя браузера по умолчанию
    default_browser_name = default_browser.split('\\')[-1].split('.')[0]

except Exception as e:
    print(f'Ошибка при проверке браузеров: {e}')

# print(f'{browsers}\n{default_browser}\n{default_browser_name}\n')

# функция открытия папки/программы/ссылки
def run(hotkey):

    hotkey_type = hotkey.get('type')
    # print(hotkey)

    if hotkey_type == 'url':

        def open_url():
            url = hotkey.get('url', [])
            if isinstance(url, str):
                url = [url]
            hotkey_browser = hotkey.get('browser', '')

            for site_url in url:
                if not hotkey_browser or hotkey_browser.lower() == default_browser_name.lower():
                    webbrowser.open(site_url)
                    print(f'Открываем {site_url} {f"в {default_browser_name}" if default_browser_name != '' else ''}')
                else:
                    browser_path = browsers.get(hotkey_browser)
                    if browser_path and os.path.exists(browser_path):
                        try:
                            new_browser = webbrowser.get(browser_path)
                            new_browser.open(site_url)
                            print(f'Открываем {site_url} в {hotkey_browser}')
                        except Exception as e:
                            print(f'Ошибка при открытии браузера {hotkey_browser}: {e}')
                            webbrowser.open(site_url)
                    else:
                        print(f'Ошибка при получении браузера {hotkey_browser}')
                        webbrowser.open(site_url)
                        print(f'Открываем {site_url} {f"в {default_browser_name}" if default_browser_name != '' else ''}')

        return open_url

    if hotkey_type == 'program':

        def open_program():
            path = hotkey.get('path', [])
            args = hotkey.get('arg', [])
            if isinstance(path, str):
                path = [path]
            if isinstance(args, str):
                args = [args]
            for program_path in path:
                if not os.path.exists(program_path):
                    print(f'Файл не найден: {program_path}')
                    continue
                # if program_path.split('.')[-1] in ['docx', 'xls', 'xlsx', 'pdf', 'jpeg', 'jpg', 'png']:
                extension = os.path.splitext(program_path)[1].lower()
                if extension in ['.docx', '.xls', '.xlsx', '.pdf', '.jpeg', '.jpg', '.png']:
                    try:
                        os.startfile(program_path)
                        print(f'Открываем {program_path}')
                    except Exception as e:
                        print(f'Ошибка при открытии {program_path}:\n{e}')
                else:
                    full_path = [program_path] + args
                    try:
                        subprocess.Popen(full_path)
                        print(f'Открываем {program_path} {f"с аргументами {[arg for arg in args]}" if args != [''] else ''}')
                    except Exception as e:
                        print(f'Ошибка при открытии {program_path}:\n{e}')

        return open_program

    if hotkey_type == 'folder':

        def open_folder():
            path = hotkey.get('path', [])
            if isinstance(path, str):
                path = [path]
            for folder_path in path:
                if os.path.exists(folder_path):
                    try:
                        subprocess.Popen(f'explorer "{folder_path}"', shell=True)
                        print(f'Открываем папку {folder_path}')
                    except Exception as e:
                        print(f'Ошибка при открытии файла:\n{e}')
        return open_folder

# основная функция, которая перебирает значения из json
def main():
    def register_hotkeys():
        try:
            keyboard.unhook_all()
            for hotkey in hotkeys:
                keyboard.add_hotkey(hotkey['key'], run(hotkey))
            print(f"[{time.strftime('%H:%M:%S')}] Хоткеи перерегистрированы")
        except Exception as e:
            print(f"Ошибка при регистрации: {e}")

    register_hotkeys()

    def auto_reload():
        while True:
            time.sleep(600)
            register_hotkeys()

    reload_thread = threading.Thread(target=auto_reload, daemon=True)
    reload_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()