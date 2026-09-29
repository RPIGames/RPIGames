import type { MessageFromServiceWorker } from "./structs.js";

/**
 * Shows a native notification.
 *
 * @param title - The notification title
 * @param body - The notification body
 * @param callback_id - An id to send to the notification.
 * @param persistent - If the notification should be made persistent (not autoclosable)
 * However, is not supported in Safari.
 */
async function showNotification(
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
 * Deletes a notification.
 *
 * @param id The callback_id of the notification to close.
 */
async function deleteNotification(id: string) {
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

export { deleteNotification, showNotification };
