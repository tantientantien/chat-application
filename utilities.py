from datetime import datetime
import random
import string
import uuid


AVATAR_UPLOAD_FOLDER = 'D:/workspace/Lap_Trinh_Python/Tieu_Luan/chat_chat/static/server_image'
ATTACHMENT_UPLOAD_FOLDER = 'D:/workspace/Lap_Trinh_Python/Tieu_Luan/chat_chat/static/cloud'

def generate_unique_code():
    unique_code = str(uuid.uuid4())
    unique_code = unique_code.replace('-', '')
    unique_code = unique_code.lower() 
    return unique_code

def get_formatted_datetime():
    now = datetime.now()
    formatted_datetime = now.strftime("%I:%M%p, %d/%m/%Y")   
    return formatted_datetime

def default_avatar():
    ten_hinh = random.randint(1, 33)
    duong_dan = f"{ten_hinh}.png"
    return duong_dan