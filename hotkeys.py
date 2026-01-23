import json
import webbrowser
import keyboard
import os
import subprocess
import find_browsers as fb

'''

формат словаря

"key": "hotkey",
"type": "url/program",
"url": "ссылка на сайт/программу",
"args": "для url: msedge, chrome, ...; для program: '-windowed', '-fullscreen', ..."

пример data.json в репозитории

hotkey клавиши

(space, enter, ctrl, shift, alt, windows, letters)
например, shift + space + s

'''

with open('data.json', 'r', encoding='utf-8') as f:
    hotkeys = json.load(f)

browsers = fb.get_installed_browsers()
default_browser = fb.get_default_browser()
default_browser_name = default_browser.split('\\')[-1].split('.')[0]

def run(url, type, arg):

    if type == 'url' or url.startswith('http'):

        def open_url():

            if arg == '' or browsers[f'{arg}'] == default_browser:
                webbrowser.open(url)

            elif default_browser_name == arg:
                browser = webbrowser.get(browsers[f'{arg}'])
                browser.open(url)

            elif arg and os.path.exists(browsers[f'{arg}']):
                print('chrome in browsers')
                browser = webbrowser.get(browsers[f'{arg}'])
                browser.open(url)

        return open_url

    if type == 'program':

        def open_program():
            subprocess.Popen([url, arg])
        return open_program


def main():

    for hotkey in hotkeys:
        keyboard.add_hotkey(hotkey['key'], run(hotkey['url'], hotkey['type'], hotkey['arg']))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()