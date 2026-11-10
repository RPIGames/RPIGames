/*
Code for external menus.
When module loaded, sets up hamburger menu related events and bottom button related events
Exports the following functions:
    - openHamburgerMenu - opens the hamburger menu
    - closeHamburgerMenu - closes the hamburger menu
    - showBottomButtons - show bottom button row
    - hideBottomButtons - hide bottom button row
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

export function showBottomButtons() {
    bottomButtons.style.display = "flex";
}

export function hideBottomButtons() {
    bottomButtons.style.display = "none";
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
