from datetime import datetime

import pytz
from flask import Flask, abort, render_template, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import config
from data import Update
from templates import Templates
from search import Search

app = Flask(__name__, static_url_path="/static/")

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# PostBack Event
@handler.add(PostbackEvent)
def handle_postback(event):
    # 路線規劃
    if "route" in event.postback.data:
        user_lat, user_lng, bike_lat, bike_lng = event.postback.data.split("_")[
            1
        ].split(",")
        message = Templates().route(
            user_lat=user_lat, user_lng=user_lng, lat=bike_lat, lng=bike_lng
        )
        line_bot_api.reply_message(event.reply_token, message)
    # 借/還車
    elif "action" in event.postback.data:
        action = event.postback.data.split("_")[1]
        if action == "borrow":
            line_bot_api.link_rich_menu_to_user(
                event.source.user_id, config.RETURN_RICH_MENU
            )
            message = TextSendMessage(text="切換模式：還車")
        else:
            line_bot_api.link_rich_menu_to_user(
                event.source.user_id, config.BORROW_RICH_MENU
            )
            message = TextSendMessage(text="切換模式：借車")
        line_bot_api.reply_message(event.reply_token, message)


# 處理訊息
@handler.add(MessageEvent, message=(LocationMessage))
def handle_message(event):
    try:
        rich_menu_id = line_bot_api.get_rich_menu_id_of_user(event.source.user_id)
    except:
        rich_menu_id = config.BORROW_RICH_MENU
    if rich_menu_id == config.BORROW_RICH_MENU:
        action = "borrow"
    else:
        action = "return"
    if isinstance(event.message, LocationMessage):
        now = datetime.now(pytz.timezone("Asia/Taipei"))
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        latitude = float(event.message.latitude)
        longitude = float(event.message.longitude)

        youbike_1 = Search().old_location(latitude=latitude, longitude=longitude)
        youbike_2 = Search().new_location(latitude=latitude, longitude=longitude)
        if len(youbike_1) == 0 and len(youbike_2) == 0:
            message = TextSendMessage(text="很抱歉！\n您所在的位置附近並沒有YouBike站點！")
            line_bot_api.reply_message(event.reply_token, message)
        else:
            youbike1_data = Templates().bike_data(
                results=youbike_1,
                user_lat=latitude,
                user_lng=longitude,
                bike_type=1,
                action=action,
            )
            youbike2_data = Templates().bike_data(
                results=youbike_2,
                user_lat=latitude,
                user_lng=longitude,
                bike_type=2,
                action=action,
            )
            message = youbike1_data + youbike2_data
            line_bot_api.reply_message(event.reply_token, message)

        history_data = {
            "uuid": event.source.user_id,
            "time": current_time,
            "loc": [latitude, longitude],
            "action": action,
        }
        config.db["History"].insert(history_data)


@handler.add(FollowEvent)
def handle_follow(event):
    now = datetime.now(pytz.timezone("Asia/Taipei"))
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    user = {
        "uuid": event.source.user_id,
        "time": current_time,
        "action": "borrow",
    }
    config.db["User List"].insert(user)
    message = Templates().welcome_message()
    line_bot_api.reply_message(event.reply_token, message)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    config.db["User List"].delete_one({"uuid": event.source.user_id})


@app.route("/")
def index():
    return render_template("Index.html")


@app.route("/update")
def update():
    stats = Update().update_data()
    if stats:
        return "Update done"
    else:
        return "Update failed"


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
