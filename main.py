from collections import defaultdict
import requests
import json
import ruz
from datetime import date as d
from datetime import timedelta as td
import os


class Config:
    token = os.getenv('TOKEN')
    db = os.getenv('DB')
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2021-05-13"
    }

    def readDatabase(self):
        readUrl = f"https://api.notion.com/v1/databases/{self.db}/query"

        res = requests.request("POST", readUrl, headers=self.headers)
        data = res.json()

        with open('./db.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False)

    def updatePage(self, page, value, day):
        print(page)
        updateUrl = f"https://api.notion.com/v1/pages/{page}"

        updateData = {
            "properties": {
                day: {
                    "rich_text": [
                        {
                            "text": {
                                "content": value
                            }
                        }
                    ]
                }
            }
        }

        data = json.dumps(updateData)

        response = requests.request(
            "PATCH", updateUrl, headers=self.headers, data=data
        )

        return (-1.5, day) if response.status_code == 200 and value != "" else (1, "error")


def main(reverse=False):
    today_times = {}
    tomorrow_times = {}
    today = d.today().__str__().replace('-', '.')
    tomorrow = (d.today() + td(days=1)).__str__().replace('-', '.')
    email = os.getenv('MAIL')

    conf = Config()
    conf.readDatabase()

    with open("db.json", "r") as json_file:
        my_dict = json.load(json_file)

    today_s = ruz.person_lessons(
        email, today, today
    )
    for i in today_s:
        today_times[i['beginLesson']] = " ".join(
            i['discipline'].split()[:-1]) + " " + i['kindOfWork'] + " " + i['auditorium']

    tomorrow_s = ruz.person_lessons(
        email, tomorrow, tomorrow
    )
    for i in tomorrow_s:
        tomorrow_times[i['beginLesson']] = " ".join(
            i['discipline'].split()[:-1]) + " " + i['kindOfWork'] + " " + i['auditorium']

    for i in my_dict['results']:
        try:
            value = "" if reverse == True else today_times[
                i['properties']['Time']
                ['title'][0]['text']['content']
            ]
            yield conf.updatePage(
                i['id'], value, "Today"
            )
        except Exception as e:
            yield 1, "Today"

        try:
            value = "" if reverse == True else tomorrow_times[
                i['properties']['Time']
                ['title'][0]['text']['content']
            ]
            yield conf.updatePage(
                i['id'], value, "Tomorrow"
            )
        except Exception as e:
            yield 1, "Tomorrow"
    
    print(tomorrow_s)

def run(bool_arg):
    lessons = defaultdict(lambda: 0)
    for i in main(bool_arg):
        lessons[i[1]] += i[0]
    print(lessons)
    