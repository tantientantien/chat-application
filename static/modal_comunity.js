// Vùng này dùng để lấy element từ DOC
var modal_community= document.querySelector(".modal_community")
var btn_community =document.querySelector(".btn_community")
var close_tab_modal = document.querySelector(".close_tab_modal")
var modal_community_contact = document.querySelector(".modal_community_contact")
var btn_room_chat = document.querySelector(".btn_room_chat")
var btn_contact = document.querySelector(".btn_contact")
var modal_community_room_chat = document.querySelector(".modal_community_room_chat")
//========================================================================================







btn_community.addEventListener("click", () => {
    modal_community.classList.toggle("display_block")
})

close_tab_modal.addEventListener("click", () => {
    modal_community.classList.toggle("display_block")
})



document.addEventListener("DOMContentLoaded", function () {
    const searchQueryInput = document.getElementById("searchQuery");
    const searchResultsDiv = document.getElementById("searchResults");
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
                            <form method="post" class="buttons">
                                <button class="hot_chat" type="submit", name="join">
                                Chat Now
                                <input type="text" name = "user_clicked" value = ${user.username} style="display: none;"/>    
                                <input type="text" name = "user_clicked_avatar" value = ${user.avatar} style="display: none;"/>
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



let currentScreen = "room_chat";

btn_room_chat.addEventListener("click", () => {
    if (currentScreen === "contact") {
        modal_community_contact.classList.add("display_none");
        modal_community_room_chat.classList.remove("display_none");
        currentScreen = "room_chat";
    }
});

btn_contact.addEventListener("click", () => {
    if (currentScreen === "room_chat") {
        modal_community_contact.classList.remove("display_none");
        modal_community_room_chat.classList.add("display_none");
        currentScreen = "contact";
    }
});
