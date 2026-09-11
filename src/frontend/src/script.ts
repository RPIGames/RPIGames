type UserTokenResponse = {
    id: string;
    secret: string;
};

type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobbyId: string | null;
};

type LobbyResponse = {
    id: string;
    name: string;
    maxMembers: number;
    currMembers: number;
    needsSecret: boolean;
};

async function getNewUserId() {
    let response = await fetch(
        "/api/v1/user/new", {
            method: "POST"
        }
    );
    if (response.ok) {
        let tokenResponse: UserTokenResponse = await response.json();
        let userAuthToken = `${tokenResponse.id}\$${tokenResponse.secret}`;
        console.debug(`Got new user auth token: ${userAuthToken}`);
        localStorage.setItem("userId", tokenResponse.id);
        localStorage.setItem("userSecret", tokenResponse.secret);
        return tokenResponse.id;
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

export async function sendUINotification(message: string, type: MessageType = MessageType.Info) {
    console.log(`Sending ${type} notification with message:`, message);

    const notificationDiv = document.createElement('div');
    notificationDiv.classList.add('alert');
    notificationDiv.classList.add(type.toString());

    const notificationCloseButton = document.createElement('span');
    notificationCloseButton.innerHTML = '&times;';
    notificationCloseButton.classList.add('closebtn');

    notificationCloseButton.onclick = () => {
        notificationDiv.style.opacity = "0";
        setTimeout(() => {
            notificationDiv.remove();
        }, 600);
    };

    const notificationMessage = document.createTextNode(message);

    notificationDiv.appendChild(notificationCloseButton);
    notificationDiv.appendChild(notificationMessage);

    document.getElementById('notification-box')?.appendChild(notificationDiv);

}

let currentLobby: LobbyResponse | null = null;

async function createLobbyCard(lobby: LobbyResponse) {
    const node = document
        .getElementById("lobby-template")!
        .firstElementChild
        ?.cloneNode(true) as HTMLElement | null;
    if (node == null) {
        return null;
    }

    node.dataset["lobbyId"] = lobby.id;

    return node;
}

async function refreshLobbies() {
    const lobbyListElement = document.getElementById("lobbies-list");
    if (lobbyListElement == null) return;

    let response = await fetch("/api/latest/lobby/all");
    if (!response.ok) {
        console.error(`Failed to get lobbies: Status code from fetching lobbies is ${response.status}`);
    }

    let lobbyList = await response.json() as LobbyResponse[];

    let newChildren: Node[] = (await Promise.all(lobbyList.map(createLobbyCard))).filter((lobby) => lobby !== null);

    if (newChildren.length == 0) {
        const template = document.getElementById("no-lobbies-template")! as HTMLTemplateElement;
        const noLobbyElement = template
            .content
            .cloneNode(true);
        newChildren.push(noLobbyElement);
    }

    lobbyListElement.replaceChildren(...newChildren);
}

async function updateLobbyUI() {
    const createButton = document.getElementById("create-lobby-button");
    const leaveButton = document.getElementById("leave-lobby-button");

    const inLobby = currentLobby !== null;

    if (createButton !== null) createButton.hidden =  inLobby;
    if (leaveButton  !== null) leaveButton.hidden  = !inLobby;
}

let activeWindow = "home";

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    // set the current window on the frontend
    let currentWindow = document.getElementById(activeWindow + "-frame");

    // change the active window to whatever
    function changeActiveWindow(changeTo: string) {
        if (changeTo == activeWindow) {return};

        if (currentWindow == null) {
            console.error("current window is currently null");
            return;
        }
        
        const newWindow = document.getElementById(changeTo + "-frame");
        if (newWindow == null) {
            console.error(`couldn't find div called ${changeTo}-frame`);
            return;
        }
        currentWindow.hidden = true;
        newWindow.hidden = false;
        currentWindow = newWindow;

        activeWindow = changeTo;

        if (changeTo == 'lobbies') {
            void refreshLobbies();
            void updateLobbyUI();
        }

        return false;
    }

    // make the sidenav buttons actually toggle the active frame

    const sidenavButtonHome = document.getElementById("sidenav-link-home");
    const sidenavButtonLobbies = document.getElementById("sidenav-link-lobbies");
    const sidenavButtonChat = document.getElementById("sidenav-link-chat");

    if (sidenavButtonHome != null)
        sidenavButtonHome.addEventListener('click', () => changeActiveWindow('home'));
    if (sidenavButtonLobbies != null)
        sidenavButtonLobbies.addEventListener('click', () => changeActiveWindow('lobbies'));
    if (sidenavButtonChat != null)
        sidenavButtonChat.addEventListener('click', () => changeActiveWindow('chat'));

    /* The placeholder button on the home page */
    const pingButton = document.getElementById("ping-button");
    if (pingButton != null) {
        pingButton.onclick = () => sendUINotification("pong!");
    }
});

async function getUserInfo(userId: string) {
    let response = await fetch(`/api/v1/user/info?user_id=${userId}`, {
        credentials: "omit",
    });
    if (response.ok) {
        let infoResponse: PublicUserInfo = await response.json();
        return infoResponse;
    } else if (response.status == 502) {
        // this means there was a gateway error, which is probably because the backend is down
        await sendUINotification("The backend server seems to be down. Try checking back in in a couple hours, or contact the hostmaster.", MessageType.Error)
        return null;
    } else {
        console.log(`Couldn't get user info for user ${userId}, since response code was ${response.status}.`);
        return null;
    }
};

async function start () {
    console.log("start initialized");
    let userId = localStorage.getItem("userId");
    if (userId == null) {
        console.log("Don't have a userString, getting a new one!");
        userId = await getNewUserId();
        if (userId == null) {
            // wait 15 seconds until next request
            setTimeout(start, 15000);
            return
        }
    }
    // check if still active
    let selfInfo = await getUserInfo(userId);
    if (selfInfo == null) {
        // couldn't get user info, just return
        return;
    }
    // set username
    let usernameElement = document.getElementById("username")
    if (usernameElement != null)
        usernameElement.textContent = selfInfo.name
    // check to see if the user is in a lobby
    if (selfInfo.lobbyId != null) {
        // if it is in a lobby, figure out the lobby name
    }
};

window.addEventListener('load', async () => {
    await start();
})
console.log("added event listener");
