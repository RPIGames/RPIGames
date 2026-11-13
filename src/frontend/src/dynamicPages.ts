/*
Code for dynamically changing the page.
Exports the following functions:
    - getPageContent - returns a stored HTML element so it can be manipulated before adding to page 
    - setPageContent - sets a section of the page (usually all of centerContent) to contain a stored HTML template
Also exports centerContent, which stores an HTML element that is the highest wrapper for dynamic content 
*/

import {
    closeHamburgerMenu,
    hideBottomButtonSection,
    showBottomButtonSection,
} from "./externalMenus.js";

import { initializeLobbyCreationPage } from "./lobbyCreation.js";

import { leaveLobby } from "./lobbyLeave.js";

import {
    deselectCard,
    initializeLobbyListPage,
    lobbyUpdateIntervalId,
} from "./lobbyList.js";

import { sendUINotification } from "./notifications.js";

export const centerContent: HTMLDivElement = document.querySelector(
    "#center-content",
) as HTMLDivElement;

//currently active page, used for determining what should be initialized
let activeWindow = "home";

/**
retrieves content from a template page
 * @param pageLocation - name of html file containing page (w/o file extension)
 * @param divId - id of html element to retrieve. If empty, defaults to pageLocation
 * @param leaveAsTemplate - bool to determine if an HTML element should be returned 
    as an HTML element or left in template form. Defaults to returning an HTML element
 * @returns HTML Element or HTML template depending on value of leaveAsTemplate
*/
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
        throw new Error(`Can't find page! pageLocation: ${pageLocation}`);
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

/**
sets part of page to contain stored template
If page location changes, initializes new page
 * @param pageLocation - name of html file containing page (w/o file extension)
 * @param parentDivId - id of html element to insert content into. If empty, defaults to centerContent
 * @param divId - id of html element to retrieve. If empty, defaults to pageLocation
    as an HTML element or left in template form. Defaults to returning an HTML element
*/
export async function setPageContent(
    pageLocation: NonNullable<string>,
    parentDivId?: string,
    divId?: string,
) {

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

    if(!pageContentResult) throw Error(`Can't find new page content! pageLocation: ${pageLocation} divId: ${divId}`);

    //close menu, if open
    closeHamburgerMenu();

    //deselect any saved card id, if it exists
    deselectCard();

    //stop constant lobby refreshing, if active
    if (lobbyUpdateIntervalId) {
        clearInterval(lobbyUpdateIntervalId);
    }
    
    //actually add content to page
    const divTemplate = pageContentResult as HTMLTemplateElement;
    const templateContent = document.importNode(divTemplate.content, true);
    parentDiv.replaceChildren(templateContent);

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
        initializeNewPage(pageLocation);
    }
}

/**
Initializes newly-loaded page
@param pageLocation - name of page to initialize
 */
async function initializeNewPage(pageLocation: string) {
    if (pageLocation === "gameLobbyInfo" || pageLocation === "chat") {
        showBottomButtonSection();
    } else {
        hideBottomButtonSection();
    }

    switch (pageLocation) {
        case "lobbies": {
            initializeLobbyListPage();
            break;
        }
        case "createLobby": {
            initializeLobbyCreationPage();
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
                    sendUINotification("native pong!", undefined, true, true);
            }
            break;
        }
        case "gameLobbyInfo": {
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
