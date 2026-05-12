type UserTokenResponse = {
    id: string;
    secret: string;
};

type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobby_id: string | null;
}

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

async function get_user_info(user_id: string) {
    let response = await fetch(`/api/v1/user/info?user_id=${user_id}`);
    if (response.ok) {
        let info_response: PublicUserInfo = await response.json();
        return info_response;
    } else {
        console.log(`Couldn't get user info for user ${user_id}.`, await response.json());
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
