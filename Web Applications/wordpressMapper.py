"""
- Code Mapping Wordpress endpoints to identify sensitive files
- Applicable for platforms like Joomla, WordPress, Drupal, etc
"""

import queue
import os
import threading
import requests
from colorama import Fore, Style, init

init(autoreset=True)

threads = 10

target = ""
directory = "./Wordpress"
filters = [".jpg", ".gif", ".png", ".css"]
wordlist = "./Wordpress/wpJuicy.txt"
sensitive_files = []

sensitive_endpoints = []
if os.path.exists(wordlist):
    with open(wordlist, 'r') as f:
        sensitive_endpoints = [line.strip() for line in f.readlines()]

os.chdir(directory)

web_paths = queue.Queue()

for root,subdir,files in os.walk("."):
    for file in files:
        remote_path = os.path.join(root, file)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(file)[1].lower() not in filters:
            web_paths.put(remote_path.replace("\\", "/"))

def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = f"{target}{path}"

        try:
            response = requests.get(url, timeout = 10)
            status = response.status_code

            if status == 200:
                color = Fore.GREEN
                if (path in sensitive_endpoints) and (response.text.strip() != ""):
                    sensitive_files.append(url)
            elif status in (301, 302):
                color = Fore.CYAN
            elif status == 401:
                color = Fore.YELLOW
            elif status == 403:
                color = Fore.RED
            elif status == 404:
                color = Fore.BLUE
            elif status >= 500:
                color = Fore.MAGENTA
            else:
                color = Fore.WHITE

            print(
                    f"{color}"
                    f"{status:<3} => "
                    f"{url:<60} => "
                    f"Size: {len(response.content):>10}"
                    f"{Style.RESET_ALL}"
                )

            response.close()
        
        except requests.RequestException as e:
            print("[-] Failed due to: %s" % e)
            pass

        finally:
            web_paths.task_done()


def main():
    global target
    target = input("Enter the target: ").strip()
    for i in range(threads):
        print(f"Spawning thread: {i}")
        t = threading.Thread(target=test_remote)
        t.start()

    web_paths.join()
    print("+---------------------------------------------------------------------+")
    print("[*] Possible sensitive file found: ")
    for sensitive in sensitive_files:
        print(f"{Fore.RED}{sensitive}{Style.RESET_ALL}")
    print("+---------------------------------------------------------------------+")
    print("Scan complete!")


if __name__ == "__main__":
    main()