import requests
from bs4 import BeautifulSoup
import utils
import time
import argparse
import cfg
from datetime import datetime


def login(session, user, pwd):
    loginUrl = config["url"] + "login.php"
    head = config["header"]
    loginData = {
        'do': 'login',
        'vb_login_username': user,
        'vb_login_password': pwd
    }
    
    response = session.post(loginUrl, data=loginData, headers=head)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        loginFailed = soup.find('p', class_="text-warning").get_text(strip=True)
        if (loginFailed):
            config["user"]["validated"] = False
            cfg.saveConfig(config)
            return False
    except AttributeError:
        config["user"]["validated"] = True
        cfg.saveConfig(config)
        return True

def downloadPosts(session, userid):
    if (login(session, config["user"]["username"], config["user"]["password"])):
        page = 1
        postid = 1
        content = {
            "meta": {},
            "posts": []
        }
        content["meta"] = {
            "timestamp": str(datetime.now()),
            "user_id": userid,
            "url": "https: // www.flashback.org/u"+userid
        }

        while (True):
            head = config["header"]
            userUrl = config["url"] + "find_posts_by_user.php?userid=" + userid + "&page=" + str(page)
            response = session.post(userUrl, headers=head)
            soup = BeautifulSoup(response.text, "html.parser")
            posts = soup.find_all("div", class_="post post-small")

            for p in posts:
                author = p.find("small").get_text(strip=True)
                author = author[9:]
                date, timeOnly = utils.parse_post_datetime(p.find("div", class_="post-heading"))         
                title = p.find("strong").get_text(strip=True)
                message = str(p.find("div", class_="post_message"))
                message = message.replace("Citat:", " [Citat: ")
                message = message.replace("</table>", "]</table>")
                message = message.replace("<strong>", "<strong>:")
                message = message.replace("</strong>", "][ </strong>")
                messageOut = BeautifulSoup(message, "html.parser")
                messageOut = messageOut.get_text(strip=True)
                postUrl = "https://flashback.org" + p.find_all("a")[1].get("href")

                content["posts"].append({
                    "post_id": postid,
                    "date": date,
                    "time": timeOnly,
                    "author": author,
                    "title": title,
                    "post_url": postUrl,
                    "content:": messageOut
                })
                # print(f"Downloading POST.. ({postid} {date} {timeOnly} {author} {postUrl})")
                postid += 1

            pageCheck = soup.find_all('a', href=lambda x: x and f'userid={userid}&page=' in x)
            if pageCheck:
                page += 1
                time.sleep(2)
            else:
                break
        
        outputFile = utils.exportjson(content, "user_" + userid)
        print("USER: Successfully downloaded", len(content["posts"]), "posts to", outputFile)
    else:
        print("login failed, see help. (-h, --help)")


def downloadThread(thread):
    threadId = thread.replace('t', '')
    page = 1
    postid = 1
    content = {
        "meta": {},
        "posts": []
    }

    while(True):
        url = config["url"] + thread + "p" + str(page)
        head = config["header"]
        response = requests.get(url, headers=head)
        if response.status_code != 200:
            print(f"Failed. Status code: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        threadTitle = soup.find('a', href=f'/t{threadId}').get_text(strip=True)
        content["meta"] = {
            "id": thread,
            "timestamp": str(datetime.now()),
            "title": threadTitle,
            "url": "https://www.flashback.org/"+thread
        }

        posts = soup.find_all("div", class_="post")
        for p in posts:
            author = p.find("a", class_="post-user-username dropdown-toggle").get_text(strip=True)
            date, timeOnly = utils.parse_post_datetime(p.find("div", class_="post-heading"))

            message = p.find('div', {'id': lambda x: x and x.startswith('post_message_')})
            messageOut = message.get_text(strip=True)
            msgId = message.get('id', '').replace('post_message_', '')
            content["posts"].append({
                "post_id": postid,
                "author":   author,
                "date":     date,
                "time":     timeOnly,
                "msg_id:": msgId,
                "content:": messageOut
            })
            # print(f"Downloading POST.. ({postid} {date} {timeOnly} {author} ({msgId}))")
            postid += 1

        pageCheck = soup.find_all('a', href=lambda x: x and f't{threadId}p' in x)
        if pageCheck:
            page += 1
            time.sleep(2)
        else:
            break

    outputFile = utils.exportjson(content, "thread_" + thread)
    print("THREAD: Successfully downloaded" , len(content["posts"]) , "posts to" , outputFile)

def main():
    if not any(vars(args).values()):
        parser.print_help()
    else:
        session = requests.Session()
        if args.config:
            config["user"]["username"] = args.config[0]
            config["user"]["password"] = args.config[1]
            cfg.saveConfig(config)
            if(login(session, config["user"]["username"], config["user"]["password"])):
                print("CONFIG: Credentials validated, login Successful!")
            else:
                print("CONFIG: Credentials NOT validated, login Failed!")
        else:
            if args.thread:
                downloadThread(args.thread)
            if args.user:
                downloadPosts(session, args.user)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="..Simple Flashback Scraper")
    parser.add_argument("-c", "--config", nargs=2, metavar=("usr", "pwd"), help="username & password")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-t", "--thread", metavar="id", help="thread to scrape, ie: t1337")
    group.add_argument("-u", "--user", metavar="id", help="user to scrape, ie: 123")
    args = parser.parse_args()
    
    config = cfg.loadConfig()
    main()