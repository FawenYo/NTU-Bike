from bson.son import SON
from pymongo import GEOSPHERE

import config


class Search:
    def old_location(
        self, latitude: float, longitude: float, max_distance: int = 500
    ) -> list:
        result = []
        config.db["Youbike 1.0"].create_index([("loc", GEOSPHERE)])
        query = {
            "loc": {
                "$near": SON(
                    [
                        (
                            "$geometry",
                            SON(
                                [
                                    ("type", "Point"),
                                    ("coordinates", [longitude, latitude]),
                                ]
                            ),
                        ),
                        ("$maxDistance", max_distance),
                    ]
                )
            }
        }
        for each in config.db["Youbike 1.0"].find(query):
            result.append(each)
        return result

    def new_location(
        self, latitude: float, longitude: float, max_distance: int = 200
    ) -> list:
        result = []
        config.db["Youbike 2.0"].create_index([("loc", GEOSPHERE)])
        query = {
            "loc": {
                "$near": SON(
                    [
                        (
                            "$geometry",
                            SON(
                                [
                                    ("type", "Point"),
                                    ("coordinates", [longitude, latitude]),
                                ]
                            ),
                        ),
                        ("$maxDistance", max_distance),
                    ]
                )
            }
        }
        for each in config.db["Youbike 2.0"].find(query):
            result.append(each)
        return result
