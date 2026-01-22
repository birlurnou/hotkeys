import os
import winreg
import subprocess
import json


def find_installed_browsers():
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

# browsers = find_installed_browsers()
# print("Найдены браузеры:")
# for name, path in browsers.items():
#     print(f"  {name}: {path}")