type UserTokenResponse = {
    id: string;
    secret: string;
};

type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobby_id: string | null;
};

async function get_new_user_id() {
    let response = await fetch(
        "/api/v1/user/new", {
            method: "POST"
        }
    );
    if (response.ok) {
        let token_response: UserTokenResponse = await response.json();
        let user_auth_token = `${token_response.id}\$${token_response.secret}`;
        console.debug(`Got new user auth token: ${user_auth_token}`);
        localStorage.setItem("user_id", token_response.id);
        localStorage.setItem("user_secret", token_response.secret);
        return token_response.id;
    } else {
        console.log("Couldn't get session token.");
        return null;
    }
};

enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
};

export async function send_UI_notification(message: string, type: MessageType = MessageType.Info) {
    console.log(`Sending ${type} notification with message:`, message);

    const notification_div = document.createElement('div');
    notification_div.classList.add('alert');
    notification_div.classList.add(type.toString());

    const notification_close_button = document.createElement('span');
    notification_close_button.innerHTML = '&times;';
    notification_close_button.classList.add('closebtn');

    notification_close_button.onclick = (_) => {
        notification_div.style.opacity = "0";
        setTimeout(() => {
            notification_div.remove();
        }, 600);
    };

    const notification_message = document.createTextNode(message);

    notification_div.appendChild(notification_close_button);
    notification_div.appendChild(notification_message);

    document.getElementById('notification-box')?.appendChild(notification_div);

}

let active_window = "home";

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    // set the current window on the frontend
    let current_window = document.getElementById(active_window + "-frame");

    // change the active window to whatever
    function change_active_window(change_to: string) {
        if (change_to == active_window) {return};

        if (current_window == null) {
            console.error("current window is currently null");
            return;
        }
        
        const new_window = document.getElementById(change_to + "-frame");
        if (new_window == null) {
            console.error(`couldn't find div called ${change_to}-frame`);
            return;
        }
        current_window.hidden = true;
        new_window.hidden = false;
        current_window = new_window;

        active_window = change_to;

        return false;
    }

    const sidenav_button_home = document.getElementById("sidenav-link-home");
    const sidenav_button_lobbies = document.getElementById("sidenav-link-lobbies");
    const sidenav_button_chat = document.getElementById("sidenav-link-chat");

    if (sidenav_button_home != null)
        sidenav_button_home.onclick = () => change_active_window('home');
    if (sidenav_button_lobbies != null)
        sidenav_button_lobbies.onclick = () => change_active_window('lobbies');
    if (sidenav_button_chat != null)
        sidenav_button_chat.onclick = () => change_active_window('chat');

    const ping_button = document.getElementById("ping-button");
    if (ping_button != null) {
        ping_button.onclick = () => send_UI_notification("pong!");
    }
});

async function get_user_info(user_id: string) {
    let response = await fetch(`/api/v1/user/info?user_id=${user_id}`);
    if (response.ok) {
        let info_response: PublicUserInfo = await response.json();
        return info_response;
    } else if (response.status == 502) {
        // this means there was a gateway error, which is probably because the backend is down
        await send_UI_notification("The backend server seems to be down. Try checking back in in a couple hours, or contact the hostmaster.", MessageType.Error)
        return null;
    } else {
        console.log(`Couldn't get user info for user ${user_id}, since response code was ${response.status}.`);
        return null;
    }
};

async function start () {
    console.log("start initialized");
    let user_id = localStorage.getItem("user_id");
    if (user_id == null) {
        console.log("Don't have a user_string, getting a new one!");
        user_id = await get_new_user_id();
        if (user_id == null) {
            // wait 15 seconds until next request
            setTimeout(start, 15000);
            return
        }
    }
    // check if still active
    let self_info = await get_user_info(user_id);
    let username_element = document.getElementById("username")
    if (username_element != null)
        if (self_info != null)
            username_element.textContent = self_info.name
};

window.addEventListener('load', async (_e) => {
    await start();
})
console.log("added event listener");
