import { getAllLobbies, joinLobby as joinLobbyBackend } from "./api.js";
import {
    centerContent,
    getPageContent,
    setPageContent,
} from "./dynamicPages.js";
import type { LobbyResponse } from "./structs.js";

//map of data for all lobbies
//stored as id, lobby pair
export const allLobbiesData = new Map<string, LobbyResponse>();

//saves id of currently selected card
export let currentSelectedCardId: string | null = null;

export let lobbyUpdateId: number | null;

export function deselectCard() {
    currentSelectedCardId = null;
}

// creates a lobby card on the lobby page
export async function createLobbyCard(lobby: LobbyResponse) {
    //fetch card template
    //TO-DO: only fetch this once
    const node = (await getPageContent(
        "lobbies",
        "lobby-card-template",
    )) as HTMLElement;

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

export async function refreshLobbyData() {
    const lobbyList = await getAllLobbies();
    allLobbiesData.clear();
    //add each lobby to map
    for (const lobby of lobbyList) {
        allLobbiesData.set(lobby.id, lobby);
    }
}

// refreshes the lobbies, getting new data from the api
export async function updateLobbyCards(fullRefresh: boolean = true) {
    //console.log("Updating Lobby Cards...");
    const lobbyListElement = document.getElementById(
        "lobbies-list",
    ) as HTMLElement;

    if (fullRefresh) {
        //HTML to display while lobby data is being fetched
        lobbyListElement.innerHTML = "Fetching Lobbies...";
    }

    await refreshLobbyData();

    const lobbyCardList: HTMLElement[] = [];

    for (const [, lobby] of allLobbiesData) {
        lobbyCardList.push(await createLobbyCard(lobby));
    }

    //set up event listeners for each card
    lobbyCardList.forEach((card) => {
        //when card clicked
        card.addEventListener("click", () => {
            //get all currently selected cards
            const selectedCardList =
                document.querySelectorAll(".card.selected");

            //deselect currently selected cards, if any exist
            if (selectedCardList.length !== 0) {
                selectedCardList.forEach((selectedCard) => {
                    //if clicked card is currently selected, don't bother removing the selection
                    if (selectedCard !== card) {
                        selectedCard.classList.remove("selected");
                    }
                });
            }
            //set existing card as selected and save id
            card.classList.add("selected");
            currentSelectedCardId = card.getAttribute(
                "data-lobby-id",
            ) as string;

            //get join lobby button
            const joinButton = document.getElementById(
                "join-lobby",
            ) as HTMLButtonElement;

            //get lobby data
            const lobby = allLobbiesData.get(
                currentSelectedCardId,
            ) as LobbyResponse;

            //If lobby is full, disable join button
            //otherwise join button should be enabled b/c lobby is selected
            if (lobby.curr_members === lobby.max_members) {
                joinButton.disabled = true;
            } else {
                joinButton.disabled = false;
            }
        });
    });

    if (lobbyCardList.length !== 0) {
        //add lobbies to html
        lobbyListElement.replaceChildren(...lobbyCardList);
    } else {
        //if no lobbies exist, show no lobbies template
        await setPageContent("lobbies", "lobbies-list", "no-lobbies-template");
    }

    //if card is saved as selected, show it as selected by internally clicking it
    if (currentSelectedCardId) {
        (
            document.querySelector(
                `[data-lobby-id="${currentSelectedCardId}"]`,
            ) as HTMLButtonElement
        ).click();
    }
}

export async function makeLobbyButtonsInteractable() {
    //Join lobby button
    const joinButton = document.getElementById(
        "join-lobby",
    ) as HTMLButtonElement;
    joinButton.addEventListener("click", checkLobbyJoinStatus);

    //Refresh lobbies button
    const refreshButton = document.getElementById(
        "refresh-lobbies",
    ) as HTMLButtonElement;
    refreshButton.addEventListener("click", () => {
        updateLobbyCards();
    });

    //Create lobby button
    const createLobbyButton = document.getElementById(
        "create-lobby",
    ) as HTMLButtonElement;
    createLobbyButton;
    createLobbyButton.addEventListener("click", async () => {
        await setPageContent("createLobby", "", "create-main");
    });
}

export async function checkLobbyJoinStatus() {
    //Refresh data just in case there has been a change since last join
    await refreshLobbyData();

    const lobby = allLobbiesData.get(
        currentSelectedCardId as string,
    ) as LobbyResponse;

    //Don't join lobby directly if secret is needed
    //Instead create password modal and join lobby when submit button pressed
    const lobbyNeedsSecret = lobby.needs_secret;
    if (lobbyNeedsSecret) {
        setupPasswordModal(lobby);
    } else {
        //If no secret is needed, (attempt to) join lobby directly
        joinLobby(lobby);
    }
}

export async function setupPasswordModal(lobby: LobbyResponse) {
    //show password element on page
    const passwordModal = (await getPageContent(
        "lobbies",
        "lobby-password-modal",
    )) as HTMLTemplateElement;
    centerContent.appendChild(passwordModal);

    //password input field
    const passwordField = document.querySelector(
        ".lobby-password-input",
    ) as HTMLInputElement;

    //set up button to leave password modal
    const passwordExitButton = document.querySelector(
        ".cancel-password-button",
    ) as HTMLButtonElement;

    //Delete the password modal when modal is exited
    passwordExitButton.addEventListener("click", () => {
        passwordModal.remove();
    });

    //set up button to enter password when clicked
    const passwordEnterButton = document.querySelector(
        ".submit-password-button",
    ) as HTMLButtonElement;

    //When enter button clicked:
    passwordEnterButton.addEventListener("click", async () => {
        //try to join lobby
        try {
            await joinLobby(lobby, passwordField.value);
        } catch (error) {
            //TS workaround to show that error is an object
            if (typeof error === "object") {
                //get the type of error
                const errorType = (error as { type: string }).type;
                //If password is incorrect, show incorrect password text
                if (errorType === "incorrect_password") {
                    (
                        document.querySelector(
                            ".password-invalid",
                        ) as HTMLElement
                    ).style.display = "block";
                    return;
                }
            }
            //If error is of different type, throw error again so it doesn't fail silently
            throw error;
        }
    });
}

export async function joinLobby(lobby: LobbyResponse, password?: string) {
    console.log("Attempting to join lobby...");
    //join lobby with or without password, depending on if public or private
    if (password) {
        await joinLobbyBackend(lobby.id, password);
    } else {
        await joinLobbyBackend(lobby.id);
    }
    //go to main game page
    currentLobby = lobby;
    console.log("Lobby joined successfully! Lobby info: ");
    console.log(currentLobby);
    localStorage.setItem("currentLobby", lobby.id);
    setPageContent("game", "", "game-main");
}

export function startLobbyUpdateInterval() {
    lobbyUpdateId = setInterval(() => {
        updateLobbyCards(false);
    }, 10000);
}
