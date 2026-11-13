/*
Code for external menus.
When module loaded, sets up hamburger menu related events and bottom button related events
Exports the following functions:
    - openHamburgerMenu - opens the hamburger menu
    - closeHamburgerMenu - closes the hamburger menu
    - showBottomButtonSection - show bottom button row
    - hideBottomButtonSection - hide bottom button row
    -changeButtonVisibility - change visibility of button on bottom row
*/

//hamburger menu itself
const hamburgerMenu: HTMLDivElement = document.querySelector(
    "#sidenav",
) as HTMLDivElement;

//hamburger menu button
const hamburgerButton: HTMLButtonElement = document.querySelector(
    ".hamburgerButton",
) as HTMLButtonElement;

//hamburger menu image (three lines) that shows when menu can be opened
const hamburgerImageOpen: HTMLDivElement = document.querySelector(
    "#hamburgerOpen",
) as HTMLImageElement;

//hamburger menu image (x button) that shows when menu can be closed
const hamburgerImageClose: HTMLDivElement = document.querySelector(
    "#hamburgerClose",
) as HTMLImageElement;

const bottomButtons: HTMLDivElement = document.querySelector(
    "#game-bottom-button-wrapper",
) as HTMLDivElement;

export function openHamburgerMenu() {
    //show menu itself
    hamburgerMenu.style.display = "flex";

    //hide menu image
    hamburgerImageOpen.style.display = "none";

    //show closing-x image
    hamburgerImageClose.style.display = "block";
}

export function closeHamburgerMenu() {
    //hide menu itself
    hamburgerMenu.style.display = "none";

    //show menu image
    hamburgerImageOpen.style.display = "block";

    //show closing-x image
    hamburgerImageClose.style.display = "none";
}

export function showBottomButtonSection() {
    bottomButtons.style.display = "flex";
}

export function hideBottomButtonSection() {
    bottomButtons.style.display = "none";
}

/**
 * Change visibility of button on bottom row.
 * @param buttonLocation - location that button goes to. Can be either lobbyInfo, chat, scoreboard, buttons, timers, or map.
 * @param show - true means button will be shown, false means button will be hidden. Defaults to true
 */
export function changeButtonVisibility(
    buttonLocation: string,
    show: boolean = true,
) {
    //all bottom row buttons have id of format `bottomButton-${buttonLocation}`
    const button = document.getElementById(
        `bottomButton-${buttonLocation}`,
    ) as HTMLButtonElement | null;
    if (!button) throw Error(`No button of id bottomButton-${buttonLocation}`);
    if (show) {
        button.style.display = "block";
    } else {
        button.style.display = "none";
    }
}

//close menu when middle section (anything but header, footer, or menu) is clicked
document.querySelector("#middle-div")?.addEventListener("click", () => {
    closeHamburgerMenu();
});

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    //make hamburger menu interactable
    hamburgerButton?.addEventListener("click", () => {
        if (hamburgerMenu.style.display === "none") {
            //show menu if it is hidden
            openHamburgerMenu();
        } else {
            //hide menu if it is showing
            closeHamburgerMenu();
        }
    });
});
