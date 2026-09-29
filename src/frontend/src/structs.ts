type UserTokenResponse = {
    id: string;
    secret: string;
};

type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobbyId: string | null;
};

//
type LobbyResponse = {
    id: string;
    name: string;
    maxMembers: number;
    currMembers: number;
    needsSecret: boolean;
};

// One item in the response for when a directory is requested from the backend folder.
interface ResourceInfo {
    name: string;
    type: "file" | "directory" | "other";
    mtime: string;
    size: number;
}

type MessageToServiceWorker = ClientClaim;

interface ClientClaim {
    type: "claim_client";
}

// a message sent from the frontend code to the service worker
type MessageFromServiceWorker = NativeNotificationClicked | OwnershipResponse;

interface NativeNotificationClicked {
    type: "native_notification_callback";
    notification_id: string; // the callback_id of the notification that was clicked
}

interface OwnershipResponse {
    type: "ownership_response";
    ownership_taken: boolean; // the callback_id of the notification that was clicked
}

export type {
    LobbyResponse,
    MessageFromServiceWorker,
    MessageToServiceWorker,
    PublicUserInfo,
    ResourceInfo,
    UserTokenResponse,
};
