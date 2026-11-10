/*
Initialization script
Runs when loaded from index.html
*/

import { getNewUserId, getSelfUserInfo } from "./api.js";
import { setPageContent } from "./dynamicPages.js";
import { closeHamburgerMenu} from "./externalMenus.js";

//initialize global variable
globalThis.currentLobby = null;

registerServiceWorker();

window.addEventListener("load", async () => {
    await start();
});

//set hamburger menu to closed state
closeHamburgerMenu();
//Set page to home

//go to game page if user already logged into lobby
if (localStorage.getItem("currentLobby")) {
    setPageContent("game", "", "game-main");
} else {
    setPageContent("home");
}

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
