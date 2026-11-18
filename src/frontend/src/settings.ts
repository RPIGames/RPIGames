import { changeSelfName, getSelfUserInfo } from "./api.js";
import { setPageContent } from "./dynamicPages.js";
import { sendUINotification } from "./notifications.js";

let changeNameButton: HTMLButtonElement | null = null;
let newNameInput: HTMLInputElement | null = null;

export async function initializeSettingsPage() {
    const userInfo = await getSelfUserInfo();
    if (userInfo === null) {
        setPageContent("home");
        return;
    }
    // change name
    changeNameButton = document.getElementById(
        "rename-button",
    ) as HTMLButtonElement;
    newNameInput = document.getElementById(
        "rename-text-box",
    ) as HTMLInputElement;

    newNameInput.defaultValue = userInfo.name;

    changeNameButton.addEventListener("click", async (e) => {
        await rename_button_event(e);
    });
}

async function rename_button_event(_: PointerEvent): Promise<void> {
    if (newNameInput === null) return;

    const status = await changeSelfName(newNameInput.value);
    if (status.ok) {
        console.log(status);
        setTimeout(() => location.reload(), 1000);
    } else {
        sendUINotification(`An error occurred: ${status.status}`);
    }
}
