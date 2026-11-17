/*
Code for lobby info page
Will probably be integrated into another page in the future
*/
import { leaveLobby as leaveLobbyBackend } from "./api.js";

import { setPageContent } from "./dynamicPages.js";

export function initializeLobbyInfoPage(){
    //setup leave lobby button
    const leaveLobbyButton = document.getElementById(
        "leave-lobby-button",
    ) as HTMLButtonElement;

    leaveLobbyButton.addEventListener("click", async () => {
        leaveLobby();
    });

    //display lobby data
    if(!globalThis.currentLobby) throw Error("Lobby data does not exist!");
    
    (document.querySelector("h1 span") as HTMLHeadingElement).textContent=globalThis.currentLobby.name;
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
