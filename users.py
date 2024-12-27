from flask import Flask, render_template, request, redirect, url_for, Blueprint, session, jsonify
from pymongo import MongoClient
import re
from handle_socket import rooms
from passlib.hash import sha256_crypt  
from datetime import datetime
import random
from string import ascii_uppercase
from werkzeug.utils import secure_filename
import os
from flask import current_app
from bson import ObjectId
import utilities
from handle_socket import online_users



client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]
rooms_collection = db["rooms"]
messages_collection = db['messages']

user = Blueprint("user", __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}





cr_user = ""
clicked_user = ""





@user.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form["user_name"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        if user and sha256_crypt.verify(password, user["password"]):
            session['username'] = username 
            return str("1")
        else:
            return str("0")
    return render_template("sign_in.html")




@user.route('/home', methods = ["POST", "GET"])
def home_page():
    if request.method == "POST":
        # biến này sẽ được dùng cho những hàm khác
        # nên nó được đặt global để những hàm khác cũng sử dụng
        global clicked_user
        
        # truy vấn lấy user để xử lý cho phù hợp
        user = users_collection.find_one({"username": session["username"]})
        yourname = user["yourname"]
        username = user["username"]
        list_contacts = user["list_contacts"]
        
        # Thông tin lấy từ method Post của giao diện
        clicked_user = request.form.get("user_clicked")
        clicked_user_avatar = request.form.get("user_clicked_avatar")
        join = request.form.get("join")
        
        user_clicked = users_collection.find_one({"username": clicked_user})

        # Kiểm tra xem user_clicked có trường "is_a_group" hay không
        if user_clicked:
            is_a_group = user_clicked.get("is_a_group", False)
        else:
            is_a_group = False

        # Tiếp tục xử lý dựa trên giá trị của is_a_group
        room_record = db.rooms.find_one({"members": {"$all": [clicked_user, username]}}, {"_id": 1})
        if not room_record:
            if is_a_group:
                room_record = db.rooms.insert_one({"room_name": "", "is_a_group": True, "members": [user["username"], clicked_user]})
            else:
                room_record = db.rooms.insert_one({"room_name": "", "is_a_group": False, "members": [user["username"], clicked_user]})
            room_id = str(room_record.inserted_id)
        else:
            room_id = str(room_record["_id"])

        # trong chức năng tìm kiếm, có phần chat now, khi nhấn vào đó thì clicked_user sẽ được thêm vào contact của người dùng
        if clicked_user not in list_contacts:
            users_collection.update_one({"username": user["username"]}, {"$push": {"list_contacts": clicked_user}})
        
        # Tiến hành xử lý phòng đưa vào session
        if join is not None:
            room = room_id
            rooms[room] = {"members": 0, "messages": []}
        session["room"] = room
        session["yourname"] = yourname
        
        # truy vấn những thông tin về tin nhắn đã nhắn trước đó, thông tin của một 
        # phòng chat nếu người dùng nhấn vào một contact có dạng phòng chat
        cursor_message = messages_collection.find({"room_id": room_id})
        messagess = [message for message in cursor_message]    
        isGroup = user_clicked.get("is_a_group", False)      
        result = rooms_collection.find_one({"members": {"$in": [user_clicked["username"]]}})
        members_count = len(result.get("members", []))
        return render_template("home.html", code=room, Messages=messagess, user_name_choose=user_clicked["yourname"], avatar_choose=clicked_user_avatar, cruser=session["username"], is_a_group=isGroup, membersC=members_count -1 )
    return render_template("home.html")


@user.route('/add_user_to_room', methods=["POST", "GET"])
def add_user_to_room():
    if request.method == "POST":
        print(clicked_user)
        user_added = request.form["user_added"]
        check_room = rooms_collection.find_one({"_id": ObjectId(session.get("room"))})
        if check_room["is_a_group"] == False:
            return f'<script>alert("This is a private chat room, you cannot add members"); window.location.replace("{url_for("user.home_page")}");</script>'
        else:
            try:
                rooms_collection.update_one({"_id": ObjectId(session.get("room"))}, {"$push": {"members": user_added}})
                users_collection.update_one({"username":user_added}, {"$push": {"list_contacts": clicked_user}})
                success_message = "User added successfully"
            except Exception as e:
                success_message = "Error adding user: " + str(e)
            return f'<script>alert("{success_message}"); window.location.replace("{url_for("user.home_page")}");</script>'
    return redirect(url_for('user.home_page'))


    




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user.route('/group_chat', methods=["POST", "GET"])
def create_group_chat():
    if request.method == "POST":
        room_name = request.form.get("set_room_name")
        avatar = request.form.get("set_room_avatar")
        datetime_created = datetime.now()
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = utilities.default_avatar()
        room_record = {
            "username": utilities.generate_unique_code(),
            "avatar_filename": filename,
            
            "is_a_group": True,
            "yourname": room_name,
            "datetime_created": datetime_created,
            "list_contacts" : []
        }
        result = users_collection.insert_one(room_record)
        if result:
            alert_message = "The room has been successfully created!"
            users_collection.update_one({"username": session.get("username")}, {"$push": {"list_contacts": room_record["username"]}})
        else:
            alert_message = "error, please try again!"
        return f'<script>alert("{alert_message}"); window.location.replace("{url_for("user.home_page")}");</script>'
    


@user.route('/get_cruser', methods=['GET'])
def get_cruser():
    current_username = session.get('username')
    user = query_users(current_username)
    return jsonify({"cruser": user["username"], "name": user["yourname"], "image":user["avatar_filename"]})





@user.route('/sign_out', methods = ['POST', 'GET'])
def sign_out():
    session.pop("username", None)
    session.pop("yourname", None)
    return redirect(url_for("user.sign_in"))



@user.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form["email"]
        yourname = request.form["your_name"]
        username = request.form["user_name"]
        password = request.form["password"]
        avatar = request.files["avatar"]
        datetime_created = datetime.now()
        hashed_password = sha256_crypt.hash(password)
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(current_app.config['AVATAR_UPLOAD_FOLDER'], filename))
        else:
            filename = utilities.default_avatar()
        is_user_existed = users_collection.find_one({"$or": [{"username": username}, {"email": email}]})
        if is_user_existed:
            return render_template("sign_up.html", message="Information already exists")
        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "yourname": yourname,
            "datetime_created": datetime_created,
            "avatar_filename": filename,
            "list_contacts" : []
        }
        user = users_collection.insert_one(user_data)
        if user:
            return render_template("sign_up.html", message="Sign up successful")
        else:
            return render_template("sign_up.html", message="Error, please try again")
    return render_template("sign_up.html")


@user.route('/online_users')
def get_users_online():
    main_user = users_collection.find_one({"username": session.get("username")})
    if main_user:
        main_user_contacts = main_user.get("list_contacts", [])
        result_list = []
        for user in online_users:
            if user in main_user_contacts:
                get_info = users_collection.find_one({"username": user})
                if get_info:
                    result_list.append({
                        "avatar": get_info.get("avatar_filename", "")
                    })
        return jsonify(online_users=result_list)
    else:
        return jsonify(error="User not found or no contacts available")





@user.route('/contacts/search/<search>')
def search_contact(search):
    search_query = search
    if search_query:       
        regex_pattern = re.compile(f".*{search_query}.*", re.IGNORECASE)  
        users = users_collection.find(
            {"$or": [
                {"username": regex_pattern},
                {"yourname": regex_pattern}
            ]}
        ).limit(4)
        user_list = []
        for user in users:
            user_list.append({
                "yourname": user["yourname"],
                "username": user["username"],
                "email": user["email"],
                "avatar" : user["avatar_filename"]
            })
        return jsonify(users=user_list)
    return jsonify(users=[])


        





@user.route('/list_friend')
def list_friend():
    current_username = session.get('username')
    user = users_collection.find_one({"username": current_username})
    formatted_time = datetime.now().strftime("%I:%M%p, %d/%m/%Y")
    user_list = []
    if user and "list_contacts" in user:
        for contact_username in user["list_contacts"]:
            contact = users_collection.find_one({"username": contact_username})
            room_id = rooms_collection.find_one({"members": {"$all": [contact_username, current_username]}})
            if room_id is None:
                room_id = rooms_collection.find_one({"members": {"$in": [contact_username, current_username]}})
            latest_message = messages_collection.find_one({"room_id": str(room_id["_id"])}, sort=[("_id", -1)])
            if latest_message:
                if latest_message["sender"] == current_username:
                    lastest_message_content = f'You: {latest_message["content"]}'
                else:
                    lastest_message_content = f'{latest_message["sender"]}: {latest_message["content"]}'
                date_content = latest_message["date"]
            else:
                lastest_message_content = "Press to chat"
                date_content = formatted_time
            if contact:
                is_a_group = contact.get("is_a_group")
                user_list.append({
                    "username": contact["username"],
                    "yourname": contact["yourname"],
                    "avatar": contact["avatar_filename"],
                    "lastest_message": lastest_message_content,
                    "date": date_content,
                    "is_a_group": is_a_group if is_a_group is not None else False
            })
    return jsonify(users=user_list)





def query_users(username):
    return users_collection.find_one({"username": username})