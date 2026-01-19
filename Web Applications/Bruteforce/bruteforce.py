import requests
import threading
import queue
from colorama import Fore, Style, init

init(autoreset=True)


threads = 10
target = ""
wordlist = "./common.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def build_wordlist(wordlist):
    # read the wordlist file
    data = open(wordlist, "r")
    raw_words = data.readlines()
    data.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        word = word.strip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print(f"Resuming wordlist from {resume}")
        else:
            words.put(word)
    
    return words


def dir_bruter(word_queue, extensions = None):
    headers = {
            "User-Agent": user_agent
        }
    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []

        # check to see if there is a file extension;
        # if not, then it's a directory path that we're bruting
        if "." not in attempt:
            attempt_list.append(f"/{attempt}/")
        else:
            attempt_list.append(f"/{attempt}")

        # if we want to bruteforce extensions
        if extensions:
            for ext in extensions:
                attempt_list.append(f"/{attempt}{ext}")
        
        # iterate over our list of attempts
        for brute in attempt_list:
            try:
                url = f"{target.rstrip('/')}{brute}"
                response = requests.get(url, headers=headers, timeout=10)

                status = response.status_code

                if status == 200 and (response.text.strip() != ""):
                    color = Fore.GREEN
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

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {url} -> {e}")


def main():
    global target
    target = input("Enter the target: ").strip()
    word_queue = build_wordlist(wordlist)
    extensions = [".php", ".bak", ".orig", ".inc"]
    threads_list = []

    for i in range(threads):
        t = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()


if __name__ == "__main__":
    main()