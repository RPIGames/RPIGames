import { closeHamburgerMenu } from "./hamburgerMenu.js";

import {
    makeCreateButtonsInteractable,
    setupGameData,
} from "./lobbyCreation.js";

import { leaveLobby } from "./lobbyLeave.js";

import {
    deselectCard,
    lobbyUpdateId,
    makeLobbyButtonsInteractable,
    startLobbyUpdateInterval,
    updateLobbyCards,
} from "./lobbyList.js";

import { sendUINotification } from "./notifications.js";

export const centerContent: HTMLDivElement = document.querySelector(
    "#center-content",
) as HTMLDivElement;

let activeWindow = "home";

export async function getPageContent(
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

export async function setPageContent(
    pageLocation: NonNullable<string>,
    parentDivId?: string,
    divId?: string,
) {
    //close menu, if open
    closeHamburgerMenu();

    //deselect any saved card id, if it exists
    deselectCard();

    //stop constant lobby refreshing, if active
    if (lobbyUpdateId) {
        clearInterval(lobbyUpdateId);
    }

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
                await updateLobbyCards();
                await makeLobbyButtonsInteractable();

                //update lobby data every 10 seconds
                startLobbyUpdateInterval();
                break;
            }
            case "createLobby": {
                await setupGameData();
                await makeCreateButtonsInteractable();
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

                leaveLobbyButton.addEventListener("click", async () => {
                    leaveLobby();
                });
                break;
            }
        }
    }
}
