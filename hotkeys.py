import json
import webbrowser
import keyboard
import os
import subprocess
import threading
import time
import find_browsers as fb

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
    for hotkey in hotkeys:
        keyboard.add_hotkey(hotkey['key'], run(hotkey))

    def wait_for_keys():
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            pass

    wait_thread = threading.Thread(target=wait_for_keys, daemon=True)
    wait_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()