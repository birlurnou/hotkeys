import json
import webbrowser
import keyboard
import os
import subprocess
import find_browsers as fb

'''

формат словаря

"key": "hotkey из модуля keyboard",
"type": "url/program",
"url": "ссылка на сайт/программу",
"args": "указание браузера, например msedge, chrome для url, и указание аргументов для program"

'''

with open('data.json', 'r', encoding='utf-8') as f:
    hotkeys = json.load(f)

browsers = fb.get_installed_browsers()
default_browser = fb.get_default_browser()
default_browser_name = default_browser.split('\\')[-1].split('.')[0]

def run(url, type, arg):

    if type == 'url':

        def open_url():

            if browsers[f'{arg}'] == default_browser:
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
            subprocess.Popen([url])
        return open_program


def main():

    arg = 'chrome'
    for hotkey in hotkeys:
        keyboard.add_hotkey(hotkey['key'], run(hotkey['url'], hotkey['type'], arg))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()