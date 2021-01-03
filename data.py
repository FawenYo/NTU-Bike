import json
import threading

import requests

import config


class Update:
    def update_data(self):
        try:
            threads = [
                threading.Thread(target=self.old_bike),
                threading.Thread(target=self.new_bike),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            return True
        except:
            return False

    def old_bike(self):
        data = requests.get(
            "https://apis.youbike.com.tw/api/front/station/all?lang=tw&type=1"
        ).json()
        for each in data["retVal"]:
            each["loc"] = [float(each["lng"]), float(each["lat"])]
            del each["lng"]
            del each["lat"]
        config.db["Youbike 1.0"].drop()
        config.db["Youbike 1.0"].insert_many(data["retVal"])

    def new_bike(self):
        data = requests.get(
            "https://apis.youbike.com.tw/api/front/station/all?lang=tw&type=2"
        ).json()
        for each in data["retVal"]:
            each["loc"] = [float(each["lng"]), float(each["lat"])]
            del each["lng"]
            del each["lat"]
        config.db["Youbike 2.0"].drop()
        config.db["Youbike 2.0"].insert_many(data["retVal"])
