import {
    getAllLobbies,
    getNewUserId,
    getSelfUserInfo,
    joinLobby as joinLobbyBackend,
    leaveLobby as leaveLobbyBackend,
    showNotification,
} from "./api.js";
import type { LobbyResponse } from "./structs";

// Registers a service worker to cache requests for offline navigation and faster loading. Also reduces server strain.
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

// Enum of different notification types. The color is based off of this.
enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
}

// Sends a UI notification. This is an in-app notification, which means it's not native.
export async function sendUINotification(
    message: string,
    type: MessageType = MessageType.Info,
    temporary: boolean = true,
    native: boolean = false,
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

    if (native) {
        showNotification(message, undefined, undefined, !temporary);
    }
}

const currentLobby: LobbyResponse | null = null;
console.log(currentLobby);

const centerContent: HTMLDivElement = document.querySelector(
    "#center-content",
) as HTMLDivElement;

// creates a lobby card on the lobby page
async function createLobbyCard(lobby: LobbyResponse) {
    currentLobbyData[lobby.id] = { ...lobby };

    //fetch card template
    //TO-DO: only fetch this once
    const node = (await getPageContent(
        "lobbies",
        "lobby-card-template",
    )) as HTMLTemplateElement;

    //set id attribute of card to lobby id
    node.setAttribute("data-lobby-id", lobby.id);

    //set values of name, active players, max players on card
    (node.querySelector("h3") as HTMLElement).innerHTML = lobby.name;
    (node.querySelector(".active-players") as HTMLElement).innerHTML =
        lobby.curr_members.toString();
    (node.querySelector(".max-players") as HTMLElement).innerHTML =
        lobby.max_members.toString();

    //change private lock img to public lock if public
    //private lock used by default
    if (!lobby.needs_secret) {
        const lockSvg = node.querySelector("#lockSvg") as HTMLImageElement;
        lockSvg.src = "/static/unlocked.svg";
        lockSvg.alt = "Public Lobby";
    }

    return node;
}

const currentLobbyData: Record<string, LobbyResponse> = {};

// refreshes the lobbies, getting new data from the api
async function refreshLobbies() {
    const lobbyListElement = document.getElementById("lobbies-list");
    if (lobbyListElement == null) return;

    const lobbyList = await getAllLobbies();

    //create list of html element cards containing lobby data
    const newChildren: Node[] = (
        await Promise.all(lobbyList.map(createLobbyCard))
    ).filter((lobby) => lobby !== null);

    //set up event listeners for each card
    newChildren.forEach((card) => {
        //when node clicked
        card.addEventListener("click", () => {
            //get all currently selected cards
            const selectedCardList =
                document.querySelectorAll(".card.selected");
            if (selectedCardList.length !== 0) {
                selectedCardList.forEach((selectedCard) => {
                    //deselect currently selected cards
                    if (selectedCard !== card) {
                        (selectedCard as HTMLElement).classList.remove(
                            "selected",
                        );
                    }
                });
            } else {
                //no other cards are selected yet
                const joinButton = document.getElementById(
                    "joinLobby",
                ) as HTMLButtonElement;
                joinButton.disabled = false;
            }
            //set existing card as selected
            (card as HTMLElement).classList.add("selected");
        });
    });

    if (newChildren.length === 0) {
        //if no lobbies exist, show no lobbies template
        await setPageContent("lobbies", "lobbies-list", "no-lobbies-template");
    } else {
        //add lobbies to html
        lobbyListElement.replaceChildren(...newChildren);
    }
}

async function makeLobbyButtonsInteractable() {
    const joinButton = document.getElementById(
        "joinLobby",
    ) as HTMLButtonElement;
    joinButton.addEventListener("click", joinLobby);
}

async function joinLobby() {
    console.log("Attempting to join lobby");
    //get id of lobby
    const lobbyId = (
        document.querySelector(".card.selected") as HTMLElement
    ).getAttribute("data-lobby-id") as string;

    const lobby = currentLobbyData[lobbyId as string] as LobbyResponse;

    //don't try to join lobby if full
    if (lobby.curr_members === lobby.max_members) {
        alert("Lobby is full!");
        return;
    }
    //bool for if lobby needs secret
    const lobbyNeedsSecret = lobby.needs_secret;
    if (lobbyNeedsSecret) {
        //show password element on page
        const passwordModal = (await getPageContent(
            "lobbies",
            "lobby-password-modal",
        )) as HTMLTemplateElement;
        centerContent.appendChild(passwordModal);
    } else {
        //try to join lobby
        const lobbyJoinSuccess = await joinLobbyBackend(lobbyId);
        if (lobbyJoinSuccess) {
            //go to main game page
            console.log("Lobby joined successfully!");
            setPageContent("game", "", "game-main");
        }
    }
}

//hamburger menu itself
const hamburgerMenu: HTMLDivElement = document.querySelector(
    "#sidenav",
) as HTMLDivElement;

//hamburger menu button
const hamburgerButton: HTMLButtonElement = document.querySelector(
    ".hamburgerButton",
) as HTMLButtonElement;

//hamburger menu image (three lines) that shows when menu can be opened
const hamburgerImageOpen: HTMLDivElement = document.querySelector(
    "#hamburgerOpen",
) as HTMLImageElement;

//hamburger menu image (x button) that shows when menu can be closed
const hamburgerImageClose: HTMLDivElement = document.querySelector(
    "#hamburgerClose",
) as HTMLImageElement;

//close menu when middle section (anything but header, footer, or menu) is clicked
document.querySelector("#middle-div")?.addEventListener("click", () => {
    closeHamburgerMenu();
});

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    //make hamburger menu interactable
    hamburgerButton?.addEventListener("click", () => {
        if (hamburgerMenu.style.display === "none") {
            //show menu if it is hidden
            openHamburgerMenu();
        } else {
            //hide menu if it is showing
            closeHamburgerMenu();
        }
    });
});

function openHamburgerMenu() {
    //show menu itself
    hamburgerMenu.style.display = "flex";

    //hide menu image
    hamburgerImageOpen.style.display = "none";

    //show closing-x image
    hamburgerImageClose.style.display = "block";
}

function closeHamburgerMenu() {
    //hide menu itself
    hamburgerMenu.style.display = "none";

    //show menu image
    hamburgerImageOpen.style.display = "block";

    //show closing-x image
    hamburgerImageClose.style.display = "none";
}

// the start function. handles all the things when the page is first loaded. fires on "load" event
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
    const selfInfo = await getSelfUserInfo();
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
    leaveAsTemplate: boolean = false,
): Promise<HTMLTemplateElement | HTMLElement | null> {
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
        const htmlTemplate = pageHTML.querySelector(
            `#${divId}`,
        ) as HTMLTemplateElement;
        if (leaveAsTemplate) {
            return htmlTemplate;
        } else {
            //convert template to an html element
            return htmlTemplate.content.firstElementChild as HTMLElement;
        }
    } else {
        return null;
    }
}

async function setPageContent(
    pageLocation: NonNullable<string>,
    parentDivId?: string,
    divId?: string,
) {
    //close menu, if open
    closeHamburgerMenu();

    //find div to append to; if parameter not initialized, set to null
    let parentDiv: HTMLElement | null = parentDivId
        ? document.querySelector(`#${parentDivId}`)
        : null;

    //append new content to centerContent by default
    if (!parentDiv) {
        parentDiv = centerContent;
    }

    //get template from location
    const pageContentResult: HTMLElement | HTMLTemplateElement | null =
        await getPageContent(pageLocation, divId, true);

    if (pageContentResult) {
        const divTemplate = pageContentResult as HTMLTemplateElement;
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
            button.onclick = () => {
                setPageContent(location, appendLocation, div);
            };
        }
    }

    //actually change page location internally, if required
    if (activeWindow !== pageLocation || parentDiv === centerContent) {
        activeWindow = pageLocation;
        console.log(`Changing location to: ${activeWindow}`);
        //location-specific code to run on page change
        switch (pageLocation) {
            case "lobbies": {
                void refreshLobbies();
                void makeLobbyButtonsInteractable();
                break;
            }
            case "home": {
                //setup ping button
                const pingButton = document.getElementById("ping-button");
                if (pingButton) {
                    pingButton.onclick = () =>
                        sendUINotification("pong!", undefined, true, false);
                }
                const nativePingButton =
                    document.getElementById("native-ping-button");
                if (nativePingButton) {
                    nativePingButton.onclick = () =>
                        sendUINotification(
                            "native pong!",
                            undefined,
                            true,
                            true,
                        );
                }
                break;
            }
            case "game": {
                //button to leave lobby
                const leaveLobbyButton = document.getElementById(
                    "leave-lobby-button",
                ) as HTMLButtonElement;

                //
                leaveLobbyButton.addEventListener("click", async () => {
                    console.log("Attempting to leave lobby...");

                    //leave lobby in backend
                    const lobbyLeaveSuccess = await leaveLobbyBackend();
                    if (lobbyLeaveSuccess) {
                        console.log("Lobby left successfully!");
                        setPageContent("lobbies", "", "lobby-main");
                    }
                });
                break;
            }
        }
    }
}

//set hamburger menu to closed state
closeHamburgerMenu();
//Set page to home
let activeWindow = "home";
setPageContent("home");
