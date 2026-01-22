import webbrowser
import keyboard
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
hotkeys_dict  = {
    f'{config['settings']['hotkey']} + num {i}' : config['links'][f'num_{i}']
    for i in range(1, len(config['links']) + 1)
}

def create_open_function(url):
    def opener():
        webbrowser.open(url)
    return opener

def main():
    for key, url in hotkeys_dict.items():
        print(key, url)
        keyboard.add_hotkey(key, create_open_function(url))
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()