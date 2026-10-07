import type {
    LobbyResponse,
    MessageFromServiceWorker,
    PublicUserInfo,
    UserTokenResponse,
} from "./structs.js";

/**
 * Shows a native notification.
 *
 * @param title - The notification title
 * @param body - The notification body
 * @param callback_id - An id to send to the notification.
 * @param persistent - If the notification should be made persistent (not autoclosable)
 * However, is not supported in Safari.
 */
export async function showNotification(
    title: string,
    body?: string,
    callback_id?: string,
    persistent?: boolean,
    icon?: URL,
    badge?: URL,
    callback?: () => unknown,
) {
    const result = await Notification.requestPermission();

    if (result === "granted") {
        const registration = await navigator.serviceWorker.ready;

        const options: NotificationOptions = {};

        if (body !== undefined) {
            options.body = body;
        }

        if (callback_id !== undefined) {
            options.tag = callback_id;
        }

        if (callback !== undefined) {
            if (options.tag === undefined) {
                options.tag = crypto.randomUUID().toString();
            }
            addNotificationCallback(options.tag, callback);
        }

        if (persistent !== undefined) {
            options.requireInteraction = persistent;
        }

        if (icon !== undefined) {
            options.icon = icon.toString();
        }

        if (badge !== undefined) {
            options.badge = badge.toString();
        }

        registration.showNotification(title, options);
    }
}

/**
 *  Gets a new user ID.
 *
 * @returns the session token, or null if a session token could not be made
 */
export async function getNewUserId() {
    const response = await fetch("/api/v1/user/new", {
        method: "POST",
    });
    if (response.ok) {
        const tokenResponse: UserTokenResponse = await response.json();
        const userAuthToken = `${tokenResponse.id}$${tokenResponse.secret}`;
        console.debug(`Got new user auth token: ${userAuthToken}`);
        localStorage.setItem("userId", tokenResponse.id);
        localStorage.setItem("userSecret", tokenResponse.secret);
        return tokenResponse.id;
    } else {
        console.log("Couldn't get session token.");
        return null;
    }
}

/**
 * Gets a user's information
 *
 * @param userId The uuid of the user to fetch
 *
 * @returns A {@link PublicUserInfo} object, containing user data. Returns null if the user info cannot be found, due to network error or 404.
 */
export async function getUserInfo(userId: string) {
    const response = await fetch(`/api/v1/user/info?user_id=${userId}`, {
        credentials: "omit",
    });
    if (response.ok) {
        const infoResponse: PublicUserInfo = await response.json();
        return infoResponse;
    } else if (response.status === 502) {
        throw new Error("backend not reachable due to gateway error");
    } else if (response.status === 404) {
        console.log(
            `Couldn't get user info for user ${userId}, since response code was ${response.status}.`,
        );
        return null;
    } else {
        throw new Error("backend could not be reached, is there internet?");
    }
}

/**
 * Gets your own user's info
 *
 * @throws if you don't have a user
 *
 * @returns A {@link PublicUserInfo} object, containing user data. Returns null if your user info cannot be found, due to network error or 404.
 */
export async function getSelfUserInfo() {
    const user_id = localStorage.getItem("userId");
    if (user_id === null) {
        throw "tries to get self users info without a self user";
    }
    return await getUserInfo(user_id);
}

/**
 * Gets all the lobbies.
 *
 * @throws If the lobbies could not be fetched because network error or otherwise
 *
 * @returns All the lobbies available.
 */
export async function getAllLobbies() {
    //get lobby data
    const response = await fetch("/api/latest/lobby/all");
    if (!response.ok) {
        throw `Failed to get lobbies: Status code from fetching lobbies is ${response.status}`;
    }

    //create list of lobbies
    return (await response.json()) as LobbyResponse[];
}

/**
 * Create a new lobby. The current user must not be part a lobby,
 * and will be the lobby leader of the new lobby.
 *
 * @param name (optional) - A name for the new lobby. If omitted, a random lobby will be made.
 * @param secret (optional) - A secret for the new lobby. If omitted, the lobby will be public.
 *
 * @throws If the user is not signed in.
 * @throws If a user is already in a lobby.
 *
 * @returns A {@link LobbyResponse} that represents the lobby just created.
 */
export async function makeLobby(
    name: string | undefined,
    secret: string | undefined,
) {
    const userAuthString = getAuthString();

    // Construct url params
    const params = new URLSearchParams();
    if (name !== undefined) {
        params.append("name", name);
    }
    if (secret !== undefined) {
        params.append("secret", secret);
    }

    // do the fetch
    const response = await fetch("/api/v1/lobby/new", {
        method: "POST",
        headers: [["Bearer", userAuthString]],
        body: params,
    });

    if (response.ok) {
        return (await response.json()) as LobbyResponse;
    }
    throw `${response.status} error while making a new lobby: ${response.json()}`;
}

/**
 * Gets an auth string from localStorage
 *
 * @private
 * @returns The auth string to pass in a Bearer header
 */
function getAuthString() {
    const user_id = localStorage.getItem("userId");
    const user_secret = localStorage.getItem("userSecret");
    if (user_id === null || user_secret === null) {
        throw `trying to call joinLobby without being logged in`;
    }
    return `${user_id}$${user_secret}`;
}

/**
 * Joins a lobby, given a lobbies uuid or not.
 *
 * @param id The lobbies uuid
 * @param secret The lobbies secret, only if it's a private lobby
 *
 * @returns True if the lobby was joined, false otherwise.
 */
export async function joinLobby(id: string, secret: string | undefined) {
    // obtain user id and user secret from the localstorage
    const userAuthString = getAuthString();

    // Construct url params
    const params = new URLSearchParams([["lobby_id", id]]);
    if (secret !== undefined) {
        params.append("lobby_secret", secret);
    }

    // do the fetch
    const response = await fetch("/api/v1/lobby/join", {
        method: "POST",
        headers: [["Bearer", userAuthString]],
        body: params,
    });
    if (!response.ok) {
        console.log(
            `${response.status} error trying to join lobby ${id}: ${await response.json()}`,
        );
        return false;
    }

    await getSelfUserInfo();

    return true;
}

/**
 * Deletes a notification.
 *
 * @param id The callback_id of the notification to close.
 */
export async function deleteNotification(id: string) {
    const registration = await navigator.serviceWorker.ready;

    const notifications = await registration.getNotifications({ tag: id });

    for (const notification of notifications) {
        notification.close();
    }
}

const notificationCallbacks: Map<string, (() => unknown)[]> = new Map();

/** Adds a callback to a notification.
 *
 * @param id - callback_id of the notification to attach the callback to.
 * @param callback - Function to call when the notification is clicked.
 */
async function addNotificationCallback(id: string, callback: () => unknown) {
    const thing = notificationCallbacks.get(id);

    if (thing === undefined) {
        notificationCallbacks.set(id, [callback]);
    } else {
        thing.push(callback);
    }
}

// listens a notification click event from the serviceworker. If a click event
// is found and there is a callback in the callback map, cal the callback
navigator.serviceWorker.addEventListener("message", (e: MessageEvent) => {
    const data: MessageFromServiceWorker = e.data;
    if (data.type !== "native_notification_callback") return;

    const callbacks = notificationCallbacks.get(data.notification_id);

    if (callbacks !== undefined) {
        for (const callback of callbacks) {
            callback();
        }
    }
});
