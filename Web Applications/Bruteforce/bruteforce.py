import requests
import threading
import queue
import argparse
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)


default_threads = 10
default_wordlist = "./common.txt"
default_timeout = 10
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"

print_lock = threading.Lock()
file_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Directory Bruteforcer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-t", "--target", 
        required=True, 
        help="Target URL (e.g.: https://example.com)")
    
    parser.add_argument(
        "-w", "--wordlist",
        default=default_wordlist,
        help="Wordlist that you want to use for bruteforcing")
    
    parser.add_argument(
        "-T", "--threads", 
        type=int,
        default=default_threads,
        help="Specify the number of threads to use")
    
    parser.add_argument(
        "-e", "--extension", 
        default=".php,.bak,.orig,.inc", 
        help="Comma Separated list of extensions")
    
    parser.add_argument(
        "--timeout", 
        type=int,
        default=default_timeout,
        help="Timeout for every request to wait")
    
    parser.add_argument(
        "-s", "--status-filter", 
        help="Comma Separated HTTP status codes to focus on (e.g.: 200, 403)")
    
    parser.add_argument(
        "-o", "--output", 
        help="Output file")
    
    return parser, parser.parse_args()


def build_wordlist(wordlist):
    # read the wordlist file
    with open(wordlist, "r") as f:
        words = [w.strip() for w in f.readlines()]

    q = queue.Queue()
    for word in words:
        q.put(word)

    return q, len(words)


def dir_bruter(word_queue, target, extensions, timeout, status_filter, pbar, output):
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
        
        # iterate over our list of attempts
        for brute in attempt_list:
            try:
                url = f"{target.rstrip('/')}{brute}"
                response = requests.get(url, headers=headers, timeout = timeout)

                status = response.status_code

                if status_filter and (status not in status_filter):
                    continue
                
                # if extensions are specified, only show matching URLs
                if extensions:
                    if not any(url.endswith(f".{ext.lstrip('.')}") for ext in extensions):
                        continue

                if status == 200 and (response.text.strip()):
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

                with print_lock:
                    print(
                        f"{color}"
                        f"{status:<3} => "
                        f"{url:<60} => "
                        f"Size: {len(response.content):>10}"
                        f"{Style.RESET_ALL}"
                    )

                response.close()

            except requests.exceptions.RequestException as e:
                # print(f"[ERROR] {url} -> {e}")
                pass
            finally:
                pbar.update(1)


def main():
    parser, args = parse_args()

    extensions = [e.strip() for e in args.extension.split(",") if e.strip()]
    status_filter = (
        set(map(int, args.status_filter.split(",")))
        if args.status_filter else None
    )

    word_queue, word_count = build_wordlist(args.wordlist)
    
    total_requests = word_count * (1 + len(extensions))
    pbar = tqdm(total=total_requests, desc="Status", unit="req")

    threads_list = []
    for _ in range(args.threads):
        t = threading.Thread(
            target=dir_bruter, 
            args=(
                word_queue,
                args.target, 
                extensions,
                args.timeout,
                status_filter,
                pbar,
                args.output,
            )
        )
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()

    pbar.close()


if __name__ == "__main__":
    main()