/*
Code for leaving a lobby
Will probably be integrated into another page in the future
*/
import { leaveLobby as leaveLobbyBackend } from "./api.js";

import { setPageContent } from "./dynamicPages.js";

export async function leaveLobby() {
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
