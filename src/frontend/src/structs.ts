// A response from the $api/user/new endpoint
export type UserTokenResponse = {
    id: string;
    secret: string;
};

// A response from the $api/user/info endpoint
export type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobbyId: string | null;
};

// A lobby response from the $api/lobby/info or an element of $api/lobby/all endpoint
export type LobbyResponse = {
    id: string;
    name: string;
    maxMembers: number;
    currMembers: number;
    needsSecret: boolean;
};

// One item in the response for when a directory is requested from the backend folder.
export interface ResourceInfo {
    name: string;
    type: "file" | "directory" | "other";
    mtime: string;
    size: number;
}

// This is the type of a message to a service worker.
// It is a union of different types, each with their own "type" class;
export type MessageToServiceWorker = ClientClaimMessage;

// The client claim message is a message type of a client that claims the service worker.
// This is the client that will recieve notification click events.
// You can claim the service worker's notification events if:
// 1. There is no other active client that has claimed events previously
// 2. You are an active client
export interface ClientClaimMessage {
    type: "claim_client";
}

// a message sent from the frontend code to the service worker
// could be of multiple types. the type is specified by the type property
export type MessageFromServiceWorker =
    | NativeNotificationClicked
    | OwnershipResponse;

// A response from the service worker when a notification was clicked
export interface NativeNotificationClicked {
    type: "native_notification_callback";
    notification_id: string; // the callback_id of the notification that was clicked
}

// A response from the service worker that responds to an ownership request
export interface OwnershipResponse {
    type: "ownership_response";
    ownership_taken: boolean; // says if the ownership request was accepted
}
