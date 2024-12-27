// Vùng này dùng để lấy element từ DOC
var list_qnb_item = document.querySelectorAll('.qnb_item_btn')
var list_button_header_box_11 = document.querySelectorAll('.button_header_box_11')
const messages = document.getElementById("messages")
const chatContent = document.getElementById("chatContent")
const message = document.getElementById("message_input")
var profile_btn = document.querySelector(".profile_btn")
var buttons = document.querySelector(".buttons")
var box_33 = document.querySelector(".box_33")
var expand = document.querySelector(".expand")
//========================================================================================







// Khởi tạo kết nối đến socket server
var socketio = io.connect('http://192.168.1.206:5000');



// Lấy dữ liệu của tài khoản hiện tại
var cruser;
fetch('/get_cruser')
  .then(response => response.json())
  .then(data => {
    cruser = data.cruser
    profile_btn.innerHTML = `<img src="../static/server_image/${data.image}" alt="">`
  })
  .catch(error => {
    console.error('Lỗi:', error);
  });



// Hàm kiểm tra xem msg có phải là tên file ảnh hay không
function isImageFilename(msg) {
  // Định dạng file ảnh phổ biến (có thể mở rộng danh sách nếu cần)
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];

  // Sử dụng biểu thức chính quy để kiểm tra phần mở rộng của tên file
  const fileExtension = msg.split('.').pop().toLowerCase();
  return imageExtensions.includes(fileExtension);
}

// Hàm để tạo tin nhắn dựa trên loại của msg
function createMessage(username, msg, avatar, current_time) {
  if (msg.trim() !== "") {
    const messageClass = (username === cruser) ? "flex_right" : "flex_left";
    const is_sender = (username === cruser) ? "is_sender" : "is_received";
    const block = (username === cruser) ? "block_none" : "block_block";
    const text_right = (username === cruser) ? "text_right" : "";
    const isImage = isImageFilename(msg);

    const content = `
        <div class="main_block_chat ${messageClass}">
            <div class="sender_image">
                <img src="../static/server_image/${avatar}" alt="" class = "${block}">
            </div>
            <div class="text ${text_right}">
                <div class="text_info">
                    <p class="sender ${block}">${username}</p>
                </div>
                ${isImage
                    ? `
                    <div class="text_content">
                    <img src="../static/cloud/${msg}" alt="image error">
                    </div>`
                    : `<div class="text_content ${is_sender}">
                          <p>${msg}</p>
                        </div>`
              
              }
                <div class="time_content">
                    <p>${hienThiNgayChat(current_time)}</p>
                </div>
            </div>
        </div>
    `;
    messages.innerHTML += content;
  }
}


function SignIn() {
  var num1 = $('#typeusername').val();
  var num2 = $('#typepassword').val();

  var typeusername = document.querySelector("#typeusername")
  var typepassword = document.querySelector("#typepassword")
  $.ajax({
      type: 'POST',
      url: '/sign_in',
      data: {
          user_name: num1,
          password: num2,
          
      },
      success: function(result) {
        if(result == "1"){
          window.location.href = '/home';

          typepassword.style.borderColor = "transparent"
          typepassword.value = ""

          typeusername.style.borderColor = "transparent"
          typeusername.value = ""
        }

        else if(result == "0"){
          typepassword.style.borderColor = "red"
          typepassword.value = ""
          typepassword.placeholder = "Username or Password is incorrect!"
          
          typeusername.style.borderColor = "red"
          typeusername.placeholder = "Username or Password is incorrect!"
          
        }
          
      },
      error: function(error) {
          console.log(error);
      }
  });
}



  // Tạo tin nhắn 
// const createMessage = (username, msg, avatar, current_time) => {
//   if (msg.trim() !== "") {
//     const messageClass = (username === cruser) ? "flex_right" : "flex_left";
//     const is_sender = (username === cruser) ? "is_sender" : "is_received";
//     const block = (username === cruser) ? "block_none" : "block_block"
//     const text_right = (username ===  cruser) ? "text_right": "";

//     const content = `
//         <div class="main_block_chat ${messageClass}">
//             <div class="sender_image">
//                 <img src="../static/server_image/${avatar}" alt="" class = "${block}">
//             </div>
//             <div class="text ${text_right}">
//                 <div class="text_info">
//                     <p class="sender ${block}">${username}</p>                           
//                 </div>
//                 <div class="text_content ${is_sender}">
//                   <p>${msg}</p>
//                 </div>
//                 <div class="time_content">
//                     <p>${hienThiNgayChat(current_time)}</p>
//                 </div>
//             </div> 
//         </div>      
//         `;
//     messages.innerHTML += content;
//   }
// };



// Hàm cuộn xuống dưới của khung chat
function scrollToBottom() {
  chatContent.scrollTop = chatContent.scrollHeight + 200;
}



// Nhận tin nhắn từ socket trả về, gọi hàm tạo tin nhắn để hiển thị ra UI
socketio.on("message", (data) => {
  createMessage(data.username, data.message, data.avatar, data.current_time, data.is_sender);
  setTimeout(() => {
    scrollToBottom()
  }, 20)
});



// Gửi tin nhắn lên socket sever để xử lý
const sendMessage = () => {
  if (message.value == "") return;
  socketio.emit("message", { data: message.value });
  message.value = "";
};



// Render ra các các tài khoản đã từng tương tác, kết hợp với việc tạo chat nếu click vào một tài khoản
fetch("/list_friend")
.then((response) => response.json())
.then((data) => {
    let htmlContent = "";
    data.users.forEach((x) => {
        htmlContent += `
        <form method="post" class="buttons">
            <button class="contact" id = "btn_connect_contact" type="submit" name="join" onclick = "create_room()">
            <input type="text" name = "user_clicked" value = ${x.username} style="display: none;"/>    
            <input type="text" name = "user_clicked_avatar" value = ${x.avatar} style="display: none;"/>
            <img class="contact_avartar" src="../static/server_image/${x.avatar}" alt="">
                <div class="block_text">
                    <div class="contact_name">
                        <p style="font-family: poppins_bold; color:black;" class="user_name_block">${(x.is_a_group) ? x.yourname : layTenSauNguyen(x.yourname)}</p>
                        <p style="color: #cccccc;">${hienThiNgayChat(x.date)}</p>
                    </div>
                    <div class="text_lastest">
                        <p>${catChuoi(x.lastest_message, 28)}</p>
                    </div>
                </div>    
            </button>
        </form>`;
    });
    buttons.innerHTML = htmlContent;
})
.catch((e) => { console.log(e); })



// Vùng xử lý màu sắc giao diện
list_qnb_item.forEach((button) => {
  button.addEventListener('click', function () {
    list_qnb_item.forEach((btn) => {
      btn.classList.remove("selected_button")
    });
    this.classList.add("selected_button")
  })
})

list_button_header_box_11.forEach((button) => {
  button.addEventListener('click', function () {
    list_button_header_box_11.forEach((btn) => {
      btn.classList.remove("selected_button")
    });
    this.classList.add("selected_button")
  })
})
//=================================================




function layTenSauNguyen(chuoi) {
 // Tách chuỗi thành mảng các từ
 var mangTu = chuoi.split(" ");

 // Lấy từ vị trí thứ hai trở đi
 var ten = mangTu.slice(1).join(" ");

 return ten;
}

function hienThiNgayChat(ngayNhap) {
  split_with_colon = ngayNhap.split(",")
  split_with_slash = split_with_colon[1].split("/")
  datetime_system = new Date()
  date = datetime_system.getDate()
  month = datetime_system.getMonth() + 1
  result = ""
  if (month == split_with_slash[1] && date == split_with_slash[0])
  {
    result = "Today"
  }

  else if(month == split_with_slash[1] && date == parseInt(split_with_slash[0]) + 1){
    result = "Yesterday"
  }
  else{
    result =  split_with_colon[1]
  }

  return split_with_colon[0] + ", " + result
}


function catChuoi(chuoi, doDaiToiDa) {
  if (chuoi.length > doDaiToiDa) {
      return chuoi.slice(0, doDaiToiDa) + '...';
  }
  return chuoi;
}




document.addEventListener("DOMContentLoaded", function () {
  const searchQueryInput = document.getElementById("search_query");
  const searchResultsDiv = document.getElementById("search_results");
  searchQueryInput.addEventListener("input", function () {
      var searchQuery = searchQueryInput.value;
      fetch(`/contacts/search/${searchQuery}`)
          .then((response) => response.json())
          .then((data) => {
              searchResultsDiv.innerHTML = "";
              console.log(data);
              data.users.forEach((user) => {
                  const userItem = document.createElement("div");
                  userItem.classList.add("contact_item");
                  userItem.innerHTML = `
                  <div class="modal_community_contact_box">
                      <div class="contact_item">
                          <img src="../static/server_image/${user.avatar}" alt="">
                          <div style = "flex:3;">
                              <p>${user.username}</p>
                              <p style = "color:gray; font-size:12px;">${user.yourname}</p>
                          </div>
                          <form action="/add_user_to_room" method="post" class="buttons">
                              <button class="hot_chat" type="submit", name="add_to_room">
                              Add
                              <input type="text" name = "user_added" value = ${user.username} style="display: none;"/>    
                              <input type="text" name = "user_added_avatar" value = ${user.avatar} style="display: none;"/>
                              </button>
                          </form>
                      </div>
                  </div>
                  `;
                  searchResultsDiv.appendChild(userItem);
              });
          })
          .catch((error) => {
              console.error("Error:", error);
          });
  });
});


var members_of_room = document.querySelector(".members_of_room")

fetch("/get_user_of_room")
.then((response) => response.json())
.then((data) => {
    let htmlContent = "";
    data.users.forEach((x) => {
        htmlContent += `
        <div class="contact_item">
                            <img src="../static/server_image/${x.avatar}" alt="">
                            <div style = "flex:3;">
                                <p>${x.username}</p>
                                <p style = "color:gray; font-size:12px;">${x.yourname}</p>
                            </div>
                        </div>`;
    });
    members_of_room.innerHTML = htmlContent;
})
.catch((e) => { console.log(e); })


var timeElements = document.querySelectorAll(".time_content p");

timeElements.forEach(function(element) {
  var textContent = element.textContent;
  element.innerHTML = hienThiNgayChat(textContent)
});


// Lấy tất cả các phần tử main_block_chat
var mainBlockChats = document.querySelectorAll(".main_block_chat");

// Lặp qua từng main_block_chat và thêm sự kiện click
mainBlockChats.forEach(function(mainBlockChat) {
  mainBlockChat.addEventListener("click", function() {
    // Tìm phần tử time_content bên trong main_block_chat
    var timeContent = mainBlockChat.querySelector(".time_content");

    // Thêm class "block" vào phần tử time_content
    timeContent.classList.toggle("block_block");
  });
});






// Lắng nghe sự kiện click trên nút
var button = document.querySelector('.button_attachment');

button.addEventListener('click', function() {
  // Khi nút được nhấn, kích hoạt sự kiện click cho phần tử input file ẩn
  var fileInput = document.getElementById('fileInput');
  fileInput.click();
});

var fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', function() {
  if (fileInput.files.length > 0) {
    var selectedFile = fileInput.files[0];

    var reader= new FileReader();
    reader.onload = function (event) {
      var fileData = event.target.result;
      // Gửi dữ liệu file đến máy chủ qua kết nối Socket.io
      socketio.emit('upload', {"file" : fileData});
  };
  reader.readAsArrayBuffer(selectedFile);
  }
});




// Lắng nghe sự kiện click trên nút
var button_image_message = document.querySelector('.button_image_message');

button_image_message.addEventListener('click', function() {
  // Khi nút được nhấn, kích hoạt sự kiện click cho phần tử input file ẩn
  var imageFileInput = document.getElementById('imageFileInput');
  imageFileInput.click();
});

var imageFileInput = document.getElementById('imageFileInput');
imageFileInput.addEventListener('change', function() {
  if (imageFileInput.files.length > 0) {
    var selectedFile = imageFileInput.files[0];

    var reader= new FileReader();
    reader.onload = function (event) {
      var fileData = event.target.result;
      // Gửi dữ liệu file đến máy chủ qua kết nối Socket.io
      socketio.emit('upload_image', {"file" : fileData});
  };
  reader.readAsArrayBuffer(selectedFile);
  }
});


var ca_list_active = document.querySelector(".ca_list_active")


fetch('/online_users')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    let htmlContent = "";
    data.online_users.forEach((x) => {
        htmlContent += `
        <button class="ca_list_active_item scroller_item">
                            <img src="../static/server_image/${x.avatar}" alt="">
                            <div class="check_status"></div>
                        </button>`;
    });
    ca_list_active.innerHTML = htmlContent;
  })
  .catch(error => {
    console.error('There has been a problem with your fetch operation:', error);
  });



//Lắng nghe sự kiện click enter để gửi tin nhắn
message.addEventListener("keyup", function (e) {
  if (e.key === "Enter") {
    sendMessage()
  }
});

expand.addEventListener("click",  ()=>{
  box_33.classList.toggle("Block")
})