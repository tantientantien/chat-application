from flask import Flask
from users import user
from rooms import room
from handle_socket import socketio
from datetime import timedelta
import utilities

app = Flask(__name__)
app.config['SECRET_KEY'] = utilities.generate_unique_code()

#user là một module được tách ra, ta dùng blueprint để kết nối nó tới main
app.register_blueprint(user, url_prefix = "/")
app.register_blueprint(room, url_prefix = "/")

# Đặt thời gian tồn tại cho session, hết thời gian thì sẽ tự ngắt
app.permanent_session_lifetime = timedelta(minutes= 60)

# Cấu hình cho việc tải file lên server theo đường dẫn UPLOAD_FOLDER

app.config['AVATAR_UPLOAD_FOLDER'] = utilities.AVATAR_UPLOAD_FOLDER
app.config['ATTACHMENT_UPLOAD_FOLDER'] = utilities.ATTACHMENT_UPLOAD_FOLDER



# Chạy app và cho phép debug trực tiếp
# và server chấp nhận mọi ip kết nối
if __name__ == "__main__":
    socketio.init_app(app)
    socketio.run(app, debug=True, host='0.0.0.0')
