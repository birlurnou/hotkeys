import json
import webbrowser
import os
import subprocess
import find_browsers as fb
from pynput.keyboard import Key, GlobalHotKeys, Listener

# чтение данных из json
with open('data.json', 'r', encoding='utf-8') as f:
    hotkeys = json.load(f)

browsers = {}
default_browser = ''
default_browser_name = ''

try:
    browsers = fb.get_installed_browsers()
    default_browser = fb.get_default_browser()
    default_browser_name = default_browser.split('\\')[-1].split('.')[0]
except Exception as e:
    print(f'Ошибка при проверке браузеров: {e}')


# функция открытия папки/программы/ссылки
def run(hotkey):
    hotkey_type = hotkey.get('type')

    if hotkey_type == 'url':
        def open_url():
            url = hotkey.get('url', [])
            if isinstance(url, str):
                url = [url]
            hotkey_browser = hotkey.get('browser', '')

            for site_url in url:
                if not hotkey_browser or hotkey_browser.lower() == default_browser_name.lower():
                    webbrowser.open(site_url)
                    print(f'Открываем {site_url} {f"в {default_browser_name}" if default_browser_name != "" else ""}')
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
                        print(
                            f'Открываем {site_url} {f"в {default_browser_name}" if default_browser_name != "" else ""}')

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
                        print(
                            f'Открываем {program_path} {f"с аргументами {[arg for arg in args]}" if args != [""] else ""}')
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


# основная функция
def main():
    hotkey_map = {}

    key_conversion = {
        'ctrl': '<ctrl>',
        'alt': '<alt>',
        'shift': '<shift>',
        'win': '<cmd>',
        'windows': '<cmd>',
        'cmd': '<cmd>',

        'esc': '<esc>',
        'enter': '<enter>',
        'space': '<space>',
        'tab': '<tab>',
        'backspace': '<backspace>',
        'delete': '<delete>',
        'insert': '<insert>',
        'home': '<home>',
        'end': '<end>',
        'pageup': '<page_up>',
        'pagedown': '<page_down>',
        'up': '<up>',
        'down': '<down>',
        'left': '<left>',
        'right': '<right>',

        'f1': '<f1>', 'f2': '<f2>', 'f3': '<f3>', 'f4': '<f4>',
        'f5': '<f5>', 'f6': '<f6>', 'f7': '<f7>', 'f8': '<f8>',
        'f9': '<f9>', 'f10': '<f10>', 'f11': '<f11>', 'f12': '<f12>',
    }

    for hotkey in hotkeys:
        key_parts = hotkey['key'].replace(' ', '').lower().split('+')

        formatted_parts = []
        for part in key_parts:
            if part in key_conversion:
                formatted_parts.append(key_conversion[part])
            else:
                formatted_parts.append(part)

        key_combination = '+'.join(formatted_parts)
        print(f"Хоткей: {key_combination}")

        hotkey_map[key_combination] = run(hotkey)

    with GlobalHotKeys(hotkey_map) as listener:
        listener.join()


if __name__ == "__main__":
    main()