from flask import Flask, Blueprint, request, session, redirect, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from users import clicked_user
from datetime import datetime
import users
import utilities
from flask import current_app


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
rooms_collection = db["rooms"]
users_collection = db["users"]
room = Blueprint("room", __name__)



@room.route('/get_user_of_room', methods=["GET"])
def get_user_of_room():
    user_list = []
    room_id = session.get("room")

    if room_id:
        room = rooms_collection.find_one({"_id": ObjectId(room_id)})
        
        if room:
            members = room.get("members", [])
            
            for member in members:
                user = users_collection.find_one({"username": member})
                if user:
                    user_list.append({
                        "username": user["username"],
                        "yourname": user["yourname"],
                        "avatar": user["avatar_filename"]
                    })

    return jsonify(users=user_list)




# @room.route('/group_chat', methods=["POST", "GET"])
# def create_group_chat():
#     if request.method == "POST":
#         room_name = request.form.get("set_room_name")
#         avatar = request.form.get("set_room_avatar")
#         datetime_created = datetime.now()
#         if avatar and users.allowed_file(avatar.filename):
#             filename = users.secure_filename(avatar.filename)
#             avatar.save(os.path.join(current_app.config['AVATAR_UPLOAD_FOLDER'], filename))
#         else:
#             filename = utilities.default_avatar()
#         room_record = {
#             "username": utilities.generate_unique_code(),
#             "avatar_filename": filename,
#             "is_a_group": True,
#             "yourname": room_name,
#             "datetime_created": datetime_created,
#             "list_contacts" : []
#         }
#         result = users_collection.insert_one(room_record)
#         if result:
#             alert_message = "Phòng đã được tạo thành côngcc!"
#             users_collection.update_one({"username": session.get("username")}, {"$push": {"list_contacts": room_record["username"]}})
#         else:
#             alert_message = "Đã có lỗi xảy ra, vui lòng thử lại"
#         return f'<script>alert("{alert_message}"); window.location.replace("{url_for("user.home_page")}");</script>'