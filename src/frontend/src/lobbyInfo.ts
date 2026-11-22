/*
Code for lobby info page
Will probably be integrated into another page in the future
*/
import { getSelfUserInfo, leaveLobby as leaveLobbyBackend } from "./api.js";

import { setCurrentLobbyFromBackend, setPageContent } from "./dynamicPages.js";
import type { PublicUserInfo } from "./structs/api.js";

export let infoUpdateIntervalId: number | null;

export async function initializeLobbyInfoPage() {
    setupLeaveLobbyButton();
    displayLobbyData();

    //update info every 10s
    infoUpdateIntervalId = setInterval(() => {
        displayLobbyData();
    }, 10000);
}

function setupLeaveLobbyButton() {
    //setup leave lobby button
    const leaveLobbyButton = document.getElementById(
        "leave-lobby-button",
    ) as HTMLButtonElement;

    leaveLobbyButton.addEventListener("click", async () => {
        leaveLobby();
    });
}

async function displayLobbyData() {
    await setCurrentLobbyFromBackend();

    //set lobby name
    const lobbyName = document.querySelector("h1 span") as HTMLHeadingElement;
    lobbyName.textContent = globalThis.currentLobby.name;

    //set player count
    const playerCountElement = document.querySelector(
        "#current-player-count span",
    ) as HTMLSpanElement;
    playerCountElement.textContent = globalThis.currentLobby.curr_members;

    //set max player count
    const playerMaxElement = document.querySelector(
        "#max-player-count span",
    ) as HTMLSpanElement;
    playerMaxElement.textContent = globalThis.currentLobby.max_members;

    //set player data
    const playerListElement = document.querySelector(
        "#player-list-wrapper",
    ) as HTMLUListElement;

    playerListElement.innerHTML = "";

    for (const player of globalThis.currentLobby.players) {
        //create list elements
        const playerNameElement = document.createElement("span");
        playerNameElement.classList.add("info-player-name");

        const iconElement = document.createElement("span");
        iconElement.classList.add("info-player-icon");

        //set content of elements
        playerNameElement.textContent = player.name;

        //add "you" label for self
        const selfInfo = (await getSelfUserInfo()) as PublicUserInfo;

        //default content is dash
        iconElement.textContent = "-";

        if (player.name === selfInfo.name) {
            iconElement.textContent = "(You)";
        }

        //add crown for leader player
        if (player.leader === true) {
            //remove dash if it has not been removed yet
            if(iconElement.textContent == "-"){
                iconElement.textContent = "";
            }

            //append crown, so it appears next to "you" if person is both you and leader
            iconElement.textContent += " 👑";
        }

        playerListElement.append(iconElement);
        playerListElement.append(playerNameElement);
    }
}

async function leaveLobby() {
    console.log("Attempting to leave lobby...");
    //leave lobby in backend
    const lobbyLeaveSuccess = await leaveLobbyBackend();
    if (lobbyLeaveSuccess) {
        //go back to lobbies page
        globalThis.currentLobby = null;
        localStorage.removeItem("currentLobby");
        console.log("Lobby left successfully!");
        setPageContent("lobbies", "", "lobby-main");
    }
}
