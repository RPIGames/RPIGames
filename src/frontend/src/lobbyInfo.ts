/*
Code for lobby info page
Will probably be integrated into another page in the future
*/
import {
    getLobby,
    getSelfUserInfo,
    leaveLobby as leaveLobbyBackend,
} from "./api.js";

import { setPageContent } from "./dynamicPages.js";
import type { PublicUserInfo } from "./structs/api.js";

export async function initializeLobbyInfoPage() {
    setupLeaveLobbyButton();
    displayLobbyData();
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
    //hide wrapper so content appears all at once
    const wrapper = document.querySelector(".game-wrapper") as HTMLElement;
    wrapper.style.display = "none";

    //set currentLobby value
    const lobbyId = localStorage.getItem("currentLobby") as string;
    globalThis.currentLobby = await getLobby(lobbyId);

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
        "#player-list",
    ) as HTMLUListElement;
    const playerIconElement = document.querySelector(
        "#player-icons",
    ) as HTMLUListElement;
    for (const player of globalThis.currentLobby.players) {
        //create list elements
        const playerNameElement = document.createElement("li");
        const iconElement = document.createElement("li");

        //set content of elements
        playerNameElement.textContent = player.name;

        //add "you" label for self
        const selfInfo = (await getSelfUserInfo()) as PublicUserInfo;
        if (player.name === selfInfo.name) {
            iconElement.textContent += "(You)";
        }

        //add crown for leader player
        if (player.leader === true) {
            iconElement.textContent += " 👑";
        }

        playerIconElement.append(iconElement);
        playerListElement.append(playerNameElement);
    }

    //reshow wrapper
    wrapper.style.display = "";
}

async function leaveLobby() {
    console.log("Attempting to leave lobby...");
    //leave lobby in backend
    const lobbyLeaveSuccess = await leaveLobbyBackend();
    if (lobbyLeaveSuccess) {
        //go back to lobbies page
        currentLobby = null;
        localStorage.removeItem("currentLobby");
        console.log("Lobby left successfully!");
        setPageContent("lobbies", "", "lobby-main");
    }
}
