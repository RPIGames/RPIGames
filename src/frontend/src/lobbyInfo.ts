/*
Code for lobby info page
Will probably be integrated into another page in the future
*/
import { leaveLobby as leaveLobbyBackend, getLobby, getSelfUserInfo } from "./api.js";

import { setPageContent } from "./dynamicPages.js";
import type { PublicUserInfo } from "./structs/api.js";

export async function initializeLobbyInfoPage(){
    setupLeaveLobbyButton()
    displayLobbyData()
}

function setupLeaveLobbyButton(){
    //setup leave lobby button
    const leaveLobbyButton = document.getElementById(
        "leave-lobby-button",
    ) as HTMLButtonElement;

    leaveLobbyButton.addEventListener("click", async () => {
        leaveLobby();
    });
}

async function displayLobbyData(){
    //set currentLobby value if it is not already set
    if(!globalThis.currentLobby){
        const lobbyId=localStorage.getItem("currentLobby") as string;
        globalThis.currentLobby=await getLobby(lobbyId);
    }
    
    //set lobby name
    const lobbyName=(document.querySelector("h1 span") as HTMLHeadingElement)
    lobbyName.textContent=globalThis.currentLobby.name;

    const playerCountElement=document.querySelector("#current-player-count span") as HTMLSpanElement
    playerCountElement.textContent=globalThis.currentLobby.curr_members

    const playerMaxElement=document.querySelector("#max-player-count span") as HTMLSpanElement
    playerMaxElement.textContent=globalThis.currentLobby.max_members

    //set players
    const playerListElement=document.querySelector("#player-list") as HTMLUListElement;
    const playerIconElement=document.querySelector("#player-icons") as HTMLUListElement;

    for(const player of globalThis.currentLobby.players){
        const playerNameElement=document.createElement("li")
        const iconElement=document.createElement("li");
        playerNameElement.textContent=player.name;

        iconElement.textContent=" "

        if(player.leader==true){
            iconElement.textContent="👑"
        }

        const selfInfo = await getSelfUserInfo() as PublicUserInfo; 
        if(player.name==selfInfo.name){
            iconElement.textContent+="(You)"
        }

        playerIconElement.append(iconElement)
        playerListElement.append(playerNameElement)
    }
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
