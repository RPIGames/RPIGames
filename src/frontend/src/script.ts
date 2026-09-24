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

async function registerServiceWorker() {
    console.log(window.isSecureContext);
    if ("serviceWorker" in navigator) {
        try {
            const registration = await navigator.serviceWorker.register(
                "/sw.js",
                {
                    scope: "/",
                    type: "module",
                },
            );
            if (registration.installing) {
                console.log("Service worker installing");
            } else if (registration.waiting) {
                console.log("Service worker installed");
            } else if (registration.active) {
                console.log("Service worker active");
            }
        } catch (error) {
            console.error(`Registration failed with ${error}`);
        }
    }
}

registerServiceWorker();

async function getNewUserId() {
    const response = await fetch("/api/v1/user/new", {
        method: "POST",
    });
    if (response.ok) {
        const tokenResponse: UserTokenResponse = await response.json();
        const userAuthToken = `${tokenResponse.id}$${tokenResponse.secret}`;
        console.debug(`Got new user auth token: ${userAuthToken}`);
        localStorage.setItem("userId", tokenResponse.id);
        localStorage.setItem("userSecret", tokenResponse.secret);
        return tokenResponse.id;
    } else {
        console.log("Couldn't get session token.");
        return null;
    }
}

enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
}

export async function sendUINotification(
    message: string,
    type: MessageType = MessageType.Info,
    temporary: boolean,
) {
    console.log(`Sending ${type} notification with message:`, message);

    //Create div, set styling
    const notificationDiv = document.createElement("div");
    notificationDiv.classList.add("alert");
    notificationDiv.classList.add(type.toString());

    //add notification message
    const notificationMessage = document.createTextNode(message);
    notificationDiv.appendChild(notificationMessage);

    //add close button to div, if it is not temporary
    if (!temporary) {
        const notificationCloseButton = document.createElement("span");
        notificationCloseButton.innerHTML = "&times;";
        notificationCloseButton.classList.add("closebtn");

        notificationCloseButton.onclick = () => {
            notificationDiv.style.opacity = "0";
            setTimeout(() => {
                notificationDiv.remove();
            }, 600);
        };
        notificationDiv.appendChild(notificationCloseButton);
    }

    //show notification on screen
    document.getElementById("notification-box")?.appendChild(notificationDiv);

    if (temporary) {
        //delay before disappearing, in seconds
        const delayTime = 1;

        //amount of time it fades away for, in seconds
        const fadeTime = 2;

        //Set original opacity and add transition for it to fade out
        notificationDiv.style.opacity = "100%";
        notificationDiv.style.transition = `all ${fadeTime}s ${delayTime}s`;
        notificationDiv.offsetHeight;

        //notification will fade until this opacity is reached
        notificationDiv.style.opacity = "0%";

        //actually delete element after it fades out
        setTimeout(
            () => {
                notificationDiv.remove();
            },
            delayTime * 1000 + fadeTime * 1000,
        );
    }
}

const currentLobby: LobbyResponse | null = null;

async function createLobbyCard(lobby: LobbyResponse) {
    //fetch card template
    //TO-DO: only fetch this once
    const cardTemplate = (await getPageContent(
        "lobbies",
        "lobby-template",
    )) as HTMLTemplateElement;

    //convert template to actual html element
    const node: HTMLElement = cardTemplate.content
        .firstElementChild as HTMLElement;
    node.setAttribute("data-lobby-id", lobby.id);

    return node;
}

async function refreshLobbies() {
    const lobbyListElement = document.getElementById("lobbies-list");
    if (lobbyListElement == null) return;

    //get lobby data
    const response = await fetch("/api/latest/lobby/all");
    if (!response.ok) {
        console.error(
            `Failed to get lobbies: Status code from fetching lobbies is ${response.status}`,
        );
    }

    //create list of lobbies
    const lobbyList = (await response.json()) as LobbyResponse[];

    //create list of html element cards containing lobby data
    const newChildren: Node[] = (
        await Promise.all(lobbyList.map(createLobbyCard))
    ).filter((lobby) => lobby !== null);

    if (newChildren.length === 0) {
        //if no lobbies exist, show no lobbies template
        await setPageContent("lobbies", "lobbies-list", "no-lobbies-template");
    } else {
        //add lobbies to html
        lobbyListElement.replaceChildren(...newChildren);
    }
}

async function updateLobbyUI() {
    const createButton = document.getElementById("create-lobby-button");
    const leaveButton = document.getElementById("leave-lobby-button");

    const inLobby = currentLobby !== null;

    if (createButton !== null) createButton.hidden = inLobby;
    if (leaveButton !== null) leaveButton.hidden = !inLobby;
}

const centerContent: HTMLDivElement = document.querySelector(
    "#center-content",
) as HTMLDivElement;
let activeWindow = "home";
setPageContent("home");

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    // make the sidenav buttons actually toggle the active frame

    const sidenavButtonHome = document.getElementById("sidenav-link-home");
    const sidenavButtonLobbies = document.getElementById(
        "sidenav-link-lobbies",
    );
    const sidenavButtonChat = document.getElementById("sidenav-link-chat");

    if (sidenavButtonHome)
        sidenavButtonHome.addEventListener("click", () =>
            setPageContent("home"),
        );
    if (sidenavButtonLobbies)
        sidenavButtonLobbies.addEventListener("click", () =>
            setPageContent("lobbies", "centerContent", "lobby-main"),
        );
    if (sidenavButtonChat)
        sidenavButtonChat.addEventListener("click", () =>
            setPageContent("chat"),
        );
});

async function getUserInfo(userId: string) {
    const response = await fetch(`/api/v1/user/info?user_id=${userId}`, {
        credentials: "omit",
    });
    if (response.ok) {
        const infoResponse: PublicUserInfo = await response.json();
        return infoResponse;
    } else if (response.status === 502) {
        // this means there was a gateway error, which is probably because the backend is down
        await sendUINotification(
            "The backend server seems to be down. Try checking back in in a couple hours, or contact the hostmaster.",
            MessageType.Error,
            false,
        );
        return null;
    } else {
        console.log(
            `Couldn't get user info for user ${userId}, since response code was ${response.status}.`,
        );
        return null;
    }
}

async function start() {
    console.log("start initialized");
    let userId = localStorage.getItem("userId");
    if (userId == null) {
        console.log("Don't have a userString, getting a new one!");
        userId = await getNewUserId();
        if (userId == null) {
            // wait 15 seconds until next request
            setTimeout(start, 15000);
            return;
        }
    }
    // check if still active
    const selfInfo = await getUserInfo(userId);
    if (selfInfo == null) {
        // couldn't get user info, just return
        return;
    }
    // set username
    const usernameElement = document.getElementById("username");
    if (usernameElement != null) usernameElement.textContent = selfInfo.name;
    // check to see if the user is in a lobby
    if (selfInfo.lobbyId != null) {
        // if it is in a lobby, figure out the lobby name
    }
}

window.addEventListener("load", async () => {
    await start();
});

async function getPageContent(
    pageLocation: NonNullable<string>,
    divId?: string,
): Promise<HTMLTemplateElement | null> {
    //use div with same name as location, if null
    if (!divId) {
        divId = pageLocation;
    }

    //Fetch html from template
    const htmlFetchResponse = await fetch(`templates/${pageLocation}.html`);
    if (!htmlFetchResponse.ok) {
        throw new Error(`Response status: ${htmlFetchResponse.status}`);
    }

    //convert response to html
    const pageText = await htmlFetchResponse.text();
    const parser = new DOMParser();
    const pageHTML = parser.parseFromString(pageText, "text/html");

    if (pageHTML) {
        //add template to appendDiv
        return pageHTML.querySelector(`#${divId}`) as HTMLTemplateElement;
    } else {
        return null;
    }
}

async function setPageContent(
    pageLocation: NonNullable<string>,
    parentDivId?: string,
    divId?: string,
) {
    //find div to append to; if parameter not initialized, set to null
    let parentDiv: HTMLElement | null = parentDivId
        ? document.querySelector(`#${parentDivId}`)
        : null;

    //append new content to centerContent by default
    if (!parentDiv) {
        parentDiv = centerContent;
    }

    //get template from location
    const divTemplate: HTMLTemplateElement | null = await getPageContent(
        pageLocation,
        divId,
    );

    if (divTemplate) {
        const templateContent = document.importNode(divTemplate.content, true);
        parentDiv.replaceChildren(templateContent);
    }

    //Make any other dynamically added page-changing buttons interactive
    const locationButtons: (HTMLButtonElement | HTMLLinkElement)[] = Array.from(
        document.querySelectorAll(".pageChange"),
    );
    if (locationButtons.length > 0) {
        for (const button of locationButtons) {
            const location: string = button.getAttribute("data-url") || "";
            const appendLocation: string =
                button.getAttribute("data-divParent") || "";
            const div: string = button.getAttribute("data-div") || "";
            button.addEventListener("click", () => {
                setPageContent(location, appendLocation, div);
            });
        }
    }

    //actually change page location internally, if required
    if (activeWindow !== pageLocation || parentDiv === centerContent) {
        activeWindow = pageLocation;
        console.log("Changing location to: $(activeWindow)");
        //location-specific code to run on page change
        switch (pageLocation) {
            case "lobbies": {
                void refreshLobbies();
                void updateLobbyUI();
                break;
            }
            case "home": {
                //setup ping button
                const pingButton = document.getElementById("ping-button");
                if (pingButton) {
                    pingButton.onclick = () =>
                        sendUINotification("pong!", undefined, true);
                }
                break;
            }
        }
    }
}
