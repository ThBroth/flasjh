import os
import json
import utils

configFile = "config.json"
configDefault = {
    "url": "https://www.flashback.org/",
    "header": {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    },
    "user": {
        "username": "",
        "password": "",
        "validated": False
    }
}

def saveConfig(data):
    with open(configFile, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def loadConfig():
    if os.path.exists(configFile):
        with open(configFile, 'r', encoding='utf-8') as f:
            content = f.read()
            if(utils.is_json(content)):
                return json.loads(content)
            else:
                saveConfig(configDefault)
    else:
        saveConfig(configDefault)
    return json.dumps(configDefault)
