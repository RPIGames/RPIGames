/*
Code for Lobby Creation menu.
Exports initializeLobbyCreationPage
*/

import {
    makeLobby as createLobbyBackend,
    type GameInfo,
    getGameData as getGameDataBackend,
} from "./api.js";

import { getPageContent, setPageContent } from "./dynamicPages.js";

//map of data (game settings and their valid types/ranges) for all games
//stored as id, gameInfo pair
const gameData = new Map<string, GameInfo>();

export async function initializeLobbyCreationPage() {
    await setupGameData();
    await makeButtonsInteractable();
}

//Gets game data from backend, adds to select element,
//and sets up select element for creating settings fields when selection is made
async function setupGameData() {
    //select dropdown
    const gameTypeSelect = document.getElementById(
        "game-type-select",
    ) as HTMLSelectElement;

    //get backend game data
    const backendGameData = await getGameDataBackend();
    for (const data of backendGameData) {
        //add game data to map
        gameData.set(data.game_id, data);

        //add game data to game type dropdown
        const gameOption = document.createElement("option");
        gameOption.innerHTML = data.name;
        gameOption.id = data.game_id;
        gameOption.value = data.game_id;
        gameTypeSelect.append(gameOption);
    }

    gameTypeSelect.addEventListener("input", () => {
        if (gameTypeSelect.value !== "internal_default") {
            //remove default "select game type" option, if it was selected
            const defaultOption = document.getElementById(
                "default-game-option",
            );
            if (defaultOption) {
                defaultOption.remove();
            }

            //enable button
            const createLobbyButton = document.getElementById(
                "create-lobby",
            ) as HTMLButtonElement;
            createLobbyButton.disabled = false;

            const currentGameOption = gameData.get(
                gameTypeSelect.value,
            ) as GameInfo;

            updateCreateLobbyGameOptions(currentGameOption);
        }
    });
}

//Adds game settings fields underneath selection element
async function updateCreateLobbyGameOptions(currentGame: GameInfo) {
    const gameContentWrapper = document.getElementById(
        "create-game-settings-wrapper",
    ) as HTMLDivElement;
    //clear current wrapper content
    gameContentWrapper.innerHTML = "";

    //get max values for the game
    const min = currentGame.player_range[0];
    const max = currentGame.player_range[1];

    //get div for max input
    const maxInputTemplate = (await getPageContent(
        "createLobby",
        "max-input-template",
    )) as HTMLElement;
    const maxInputElement = maxInputTemplate.querySelector(
        "input",
    ) as HTMLInputElement;

    //set max of input to max of game
    maxInputElement.max = max.toString();
    maxInputElement.min = min.toString();

    //add max input to game wrapper
    gameContentWrapper.append(maxInputTemplate);

    //iterate over other input fields to add
    const gameFields = currentGame.config;
    for (const [fieldId, data] of gameFields) {
        const fieldName = data[0];
        const fieldType = data[1];

        //get element data
        const elementTemplate = (await getPageContent(
            "createLobby",
            `input-template-${fieldType}`,
        )) as HTMLElement;
        const label = elementTemplate.querySelector(
            "label",
        ) as HTMLLabelElement;
        const input = elementTemplate.querySelector(
            "input",
        ) as HTMLInputElement;

        //set input data
        label.htmlFor = fieldName;
        label.innerHTML = fieldName;
        input.name = fieldName;
        input.id = fieldId;
        input.type = fieldType;

        //add input field
        gameContentWrapper.append(elementTemplate);
    }
}

//Adds event listeners for buttons on page
async function makeButtonsInteractable() {
    //Return to lobby page button
    const returnButton = document.getElementById(
        "return-lobby-list",
    ) as HTMLButtonElement;
    returnButton.addEventListener("click", () => {
        setPageContent("lobbies", "", "lobby-main");
    });

    //Create lobby page button
    const createButton = document.getElementById(
        "create-lobby",
    ) as HTMLButtonElement;
    createButton.addEventListener("click", async () => {
        try {
            resetInputStyling();
            await createLobby();
        } catch (error: unknown) {
            if (error instanceof validationError) {
                //iterate over all affected input fields
                for (const input of error.inputIds) {
                    //set border of input field to red
                    const invalidField = document.getElementById(
                        input,
                    ) as HTMLInputElement;
                    invalidField.style.border = "2px solid red";
                }
            }
        }
    });
}

//error for input field not being filled
class validationError extends Error {
    //stores list of input field Ids
    inputIds: string[];
    constructor(inputIds: string[], message?: string) {
        super(message);
        this.message = `Missing required value for ${inputIds}`;
        this.name = "Validation Error";
        Object.setPrototypeOf(this, validationError.prototype);
        this.inputIds = inputIds;
    }
}

//reset all invalid input fields to black
function resetInputStyling() {
    //get all input elements
    const allInputs = document.querySelectorAll("input");
    if (allInputs.length !== 0) {
        for (const input of allInputs) {
            //remove all border styling on elements
            input.style.border = "";
        }
    }
}

//create lobby and redirect user to game page, if successful
async function createLobby() {
    const invalidFields: string[] = [];

    //get lobby name value, throw error if it doesn't exist
    const lobbyName = (
        document.getElementById("username-input") as HTMLInputElement
    ).value;
    if (lobbyName === "") invalidFields.push("username-input");

    //get lobby password value, if it exists
    const lobbySecret = (
        document.getElementById("password-input") as HTMLInputElement
    ).value;

    //get max players value, throw error if it doesn't exist
    const maxPlayers = parseInt(
        (document.getElementById("max-player-input") as HTMLInputElement).value,
        10,
    );
    if (!maxPlayers) invalidFields.push("max-player-input");

    //get lobby game type
    const lobbyGameType = (
        document.getElementById("game-type-select") as HTMLSelectElement
    ).value;

    //map to contain config values for to-be-created lobby
    const gameConfigValues: Map<string, number | string | boolean> = new Map();

    //config for current game type
    const gameFields = (gameData.get(lobbyGameType) as GameInfo).config;

    for (const [valueName, valueData] of gameFields) {
        //type for current config value
        const valueType = valueData[1];

        //raw value of input field storing the config value
        const inputValueRaw = (
            document.getElementById(valueName) as HTMLInputElement
        ).value;

        //throw error if field empty
        if (inputValueRaw === "") invalidFields.push(valueName);

        let inputValue: string | number | boolean;

        //convert input to a number if type is a number
        if (valueType === "number") {
            inputValue = parseInt(inputValueRaw, 10);
        } else {
            inputValue = inputValueRaw;
        }

        //set config value in map
        gameConfigValues.set(valueName, inputValue);
    }

    if (invalidFields.length !== 0) {
        throw new validationError(invalidFields);
    }

    //attempt to create lobby in backend
    const createdLobby = await createLobbyBackend(
        lobbyGameType,
        maxPlayers,
        gameConfigValues,
        lobbyName,
        lobbySecret,
    );

    //join lobby in frontend
    currentLobby = createdLobby;
    localStorage.setItem("currentLobby", createdLobby.id);
    await setPageContent("game", "", "game-main");
}
