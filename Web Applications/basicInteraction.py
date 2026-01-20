import requests

target = "https://example.com/"

header = {"User-Agent": "Testbot"}

body = requests.get(target, headers=header)

print(body.text)