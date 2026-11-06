import { showNotification } from "./api.js";

// Enum of different notification types. The color is based off of this.
enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
}

// Sends a UI notification. This is an in-app notification, which means it's not native.
export async function sendUINotification(
    message: string,
    type: MessageType = MessageType.Info,
    temporary: boolean = true,
    native: boolean = false,
) {
    console.log(`Sending ${type} notification with message:`, message);

    //Create div, set styling
    const notificationDiv = document.createElement("div");
    notificationDiv.classList.add("alert");
    notificationDiv.classList.add(type.toString());

    //add notification message
    const notificationMessage = document.createTextNode(message);
    notificationDiv.appendChild(notificationMessage);

    //add close button to div, if it is not temporary
    if (!temporary) {
        const notificationCloseButton = document.createElement("span");
        notificationCloseButton.innerHTML = "&times;";
        notificationCloseButton.classList.add("closebtn");

        notificationCloseButton.onclick = () => {
            notificationDiv.style.opacity = "0";
            setTimeout(() => {
                notificationDiv.remove();
            }, 600);
        };
        notificationDiv.appendChild(notificationCloseButton);
    }

    //show notification on screen
    document.getElementById("notification-box")?.appendChild(notificationDiv);

    if (temporary) {
        //delay before disappearing, in seconds
        const delayTime = 1;

        //amount of time it fades away for, in seconds
        const fadeTime = 2;

        //Set original opacity and add transition for it to fade out
        notificationDiv.style.opacity = "100%";
        notificationDiv.style.transition = `all ${fadeTime}s ${delayTime}s`;
        notificationDiv.offsetHeight;

        //notification will fade until this opacity is reached
        notificationDiv.style.opacity = "0%";

        //actually delete element after it fades out
        setTimeout(
            () => {
                notificationDiv.remove();
            },
            delayTime * 1000 + fadeTime * 1000,
        );
    }

    if (native) {
        showNotification(message, undefined, undefined, !temporary);
    }
}
