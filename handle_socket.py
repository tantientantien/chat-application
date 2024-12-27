from flask import Flask, session
from flask_socketio import join_room, leave_room, send, SocketIO
from pymongo import MongoClient
from bson import ObjectId
from flask import current_app
import utilities
import users
import os
import uuid
import time





socketio = SocketIO() # Khởi tạo socket
# Khởi tạo một danh sách để lưu trữ các phòng trong khi hoạt động
# Dùng set để đảm bảo không có giá trị trùng lặp
rooms = {} 

online_users = []


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
messages_collection = db['messages']
rooms_collection = db["rooms"]



# tiến hành mở kết nối, và thông báo connect mới
@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    yourname = session.get("yourname")
    username = session.get("username")
    if not room or not yourname:
        return
    if room not in rooms:
        leave_room(room)
        return
    online_users.append(username)
    join_room(room)
    send({"name": yourname, "message": ""}, to=room)
    rooms[room]["members"] += 1
    
    

# Socket sẽ lấy giá trị gói tin và gửi vào room được chỉ định
# room đó là một phần tử trong rooms và cũng là một phần tử trong session
# tin nhắn sẽ được kèm theo việc ghi vào cơ sở dữ liệu


# @socketio.on("message")
# def message(data):
#     room = session.get("room")
#     members = rooms_collection.find_one({"_id": ObjectId(room)})["members"]     
    
#     if room not in rooms:
#         return 
#     user = users.query_users(session["username"])
#     current_time = utilities.get_formatted_datetime()
#     content = {
#         "username": user["username"],
#         "message": data["data"],
#         "avatar" : user["avatar_filename"],
#         "current_time" : str(current_time),
#         "is_sender" : True
#     }
#     receiver = [member for member in members if member != user["username"]]
#     print(receiver)
#     try:
#         messages_collection.insert_one({"content":data["data"], "room_id":room, "sender": user["username"], "date":str(current_time), "receiver":receiver, "avatar":content["avatar"]})
#     except:
#         print("error")
#     send(content, to=room)
#     rooms[room]["messages"].append(content)

@socketio.on("message")
def message(data):
    room = session.get("room")
    members = rooms_collection.find_one({"_id": ObjectId(room)})["members"]

    if room not in rooms:
        return
    
    user = users.query_users(session["username"])
    current_time = utilities.get_formatted_datetime()
    content = {
        "username": user["username"],
        "message": data["data"],
        "avatar": user["avatar_filename"],
        "current_time": str(current_time),
        "is_sender": True
    }
    receiver = [member for member in members if member != user["username"]]
    
    # Thêm thông tin về file đính kèm vào content nếu có
    if "attachment" in data:
        attachment = data["attachment"]
        content["attachment"] = attachment

    try:
        messages_collection.insert_one({"content": data["data"], "room_id": room, "sender": user["username"], "date": str(current_time), "receiver": receiver, "avatar": content["avatar"], "attachment": attachment if "attachment" in data else None})
    except:
        print("error")

    send(content, to=room)
    rooms[room]["messages"].append(content)

@socketio.on("upload")
def handle_upload(data):
    room = session.get("room")
    user = users.query_users(session["username"])
    current_time = utilities.get_formatted_datetime()
    # Xử lý file được gửi từ client
    uploaded_file = data.get("file")
    if not uploaded_file:
        print("Không lấy được dữ liệu")
        return
    # Tạo tên file duy nhất (có thể cải tiến hơn để tránh trùng lặp)
    unique_filename = str(int(time.time())) + str(uuid.uuid4().hex)
    # Lưu file vào thư mục lưu trữ
    file_path = os.path.join(current_app.config['ATTACHMENT_UPLOAD_FOLDER'], unique_filename)
    with open(file_path, "wb") as file:
        file.write(uploaded_file)
    content = {
        "username": user["username"],
        "avatar": user["avatar_filename"],
        "current_time": str(current_time),
        "is_sender": True,
        "attachment": unique_filename,
        "is_attach": True
    }
    # Gửi thông tin về file đính kèm lên client
    send(content, to=room)
    messages_collection.insert_one({"content": None, "room_id": room, "sender": user["username"], "date": str(current_time), "receiver": [], "avatar": content["avatar"], "attachment": unique_filename})


@socketio.on("upload_image")
def handle_upload(data):
    room = session.get("room")
    user = users.query_users(session["username"])
    current_time = utilities.get_formatted_datetime()
    uploaded_file = data.get("file")
    if not uploaded_file:
        print("Không lấy được dữ liệu")
        return
    
    # Tạo tên file duy nhất (có thể cải tiến hơn để tránh trùng lặp)
    unique_filename = str(int(time.time())) + str(uuid.uuid4().hex) + ".jpg"
    print(unique_filename)
    # Lưu file vào thư mục lưu trữ
    file_path = os.path.join(current_app.config['ATTACHMENT_UPLOAD_FOLDER'], unique_filename)
    with open(file_path, "wb") as file:
        file.write(uploaded_file)

    
    # Gửi thông tin về file đính kèm lên client
    content = {
        "username": user["username"],
        "avatar": user["avatar_filename"],
        "current_time": str(current_time),
        "is_sender": True,
        "message": unique_filename,
        "is_image": True
    }
    
    send(content, to=room)
    messages_collection.insert_one({"content": unique_filename, "room_id": room, "sender": user["username"], "date": str(current_time), "receiver": [], "avatar": content["avatar"], "is_image":content["is_image"]})
    

    
    
# Tạo thông báo khi ngắt kết nố
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    yourname = session.get("yourname")
    username = session.get("username")
    leave_room(room)
    if room in rooms:
        online_users.remove(username)
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": yourname, "message": ""}, to=room)