/**
 * Websocket schema, types the data we send over websocket.
 *
 */

// uuid in format 'd67fa7ce-a76f-435b-a173-fac9ad3652b8'.
// A sized string cannot be fully specified in typescript
// without complex generics, so we do the feasible next best
// thing and expect a string with 5 segments delimited by '-'
export type Uuid = `${string}-${string}-${string}-${string}-${string}`;

// A ServerMessage is a message from the server to the client.
export type ServerMessage =
    | ServerConnectionStatusMessage
    | ServerTimerMessage
    | ServerScoreboardMessage
    | ServerChatMessage
    | ServerErrorMessage
    | ServerSendNotificationMessage;

export interface ServerConnectionStatusMessage {
    type: "status";
    status: "connection established" | "authenticated";
}

// Timers

export type ServerTimerMessage =
    | ServerUpdateTimersMessage
    | ServerDeleteTimersMessage;

export interface ServerUpdateTimersMessage {
    type: "timer";
    action: "update";
    data: TimerData[];
}

export interface ServerDeleteTimersMessage {
    type: "timer";
    action: "delete";
    id: string[]; // ids of the timers to delete
}

export interface TimerData {
    id: string; // id of the timer that this identifies
    name: string;
    time: string; // time in ??? format
}

// Scoreboard

export type ServerScoreboardMessage =
    | ServerUpdateScoreboardsMessage
    | ServerDeleteScoreboardsMessage
    | ServerReceiveAllScoreboardsMessage;

export interface ServerUpdateScoreboardsMessage {
    type: "scoreboard";
    action: "update";
    data: ScoreboardData;
}

export interface ServerDeleteScoreboardsMessage {
    type: "scoreboard";
    action: "delete";
    id: Uuid; // the uuid of the scoreboard
}

export interface ServerReceiveAllScoreboardsMessage {
    type: "scoreboard";
    action: "receive_all";
    data: ScoreboardData[];
}

export interface ScoreboardData {
    id: string; // uuid of the scoreboard
    name: string;
    sortable: boolean; // if the scoreboard is sortable from the frontend
    headers: string[]; // list of headers
    rows: string[][];
}

// Chat

export type ServerChatMessage =
    | ServerReceiveChatMessage
    | ServerUpdateChatroomsPermissionsMessage;

export interface ServerReceiveChatMessage {
    type: "chat";
    room_id: string;
    author_id: Uuid;
    message: string;
}

export interface ServerUpdateChatroomsPermissionsMessage {
    type: "chat";
    data: ChatroomPermissions[];
}

export interface ChatroomPermissions {
    room_id: string;
    read: boolean;
    write: boolean;
}

// Map

export type ServerMapMessage =
    | ServerUpdateMarkersMessage
    | ServerDeleteMarkersMessage;


export interface ServerUpdateMarkersMessage {
    type: "map";
    action: "update_marker";
    data: MarkerData[];
}

export interface ServerDeleteMarkersMessage {
    type: "map";
    action: "delete_marker";
    ids: string[];
}

export interface MarkerData {
    id: string;
    name: string;
    latitude: number;
    longitude: number;
}

// Buttons

export type ServerButtonMessage =
    | ServerUpdateButtonsMessage
    | ServerDeleteButtonsMessage
    | ServerSendButtonArgumentsMessage;

export interface ServerUpdateButtonsMessage {
    type: "button";
    action: "update";
    data: ButtonData[];
}

export interface ServerDeleteButtonsMessage {
    type: "button";
    action: "delete";
    id: string[];
}

export interface ServerSendButtonArgumentsMessage {
    type: "button";
    action: "params";
    id: string;
    params: string[][];
}

export interface ButtonData {
    id: string;
    name: string;
    needs_arguments: boolean;
}

// Notifications

export interface ServerSendNotificationMessage {
    type: "notification";
    level: "normal" | "debug" | "warning" | "error";
    native: boolean;
    text: string;
}

// Errors

export type ServerErrorMessage =
    | ServerChatErrorMessage
    | ServerAuthenticationErrorMessage;

export interface ServerChatErrorMessage {
    type: "error";
    category: "chat";
    message: "no chat room" | "bad message";
}

export interface ServerAuthenticationErrorMessage {
    type: "error";
    category: "authentication";
    status: "authentication failed";
}

// A ClientMessage is a message from the client to the server.
export type ClientMessage =
    | ClientAuthenticationMessage
    | ClientRequestMessage
    | ClientSendChatMessage
    | ClientSendLocationMessage
    | ClientSendButtonPressMessage
    | ClientFetchButtonArgumentsMessage;

export interface ClientAuthenticationMessage {
    type: "authentication";
    token: `${Uuid}$${Uuid}`;
}

export interface ClientRequestMessage {
    type: "timer" | "scoreboard";
    action: "request_all";
}

export interface ClientSendChatMessage {
    type: "chat";
    message: string;
    room_id: Uuid;
}

// location
export interface ClientSendLocationMessage {
    type: "map";
    location: GeolocationData;
}

export interface GeolocationData {
    accuracy: number;
    latitude: number;
    longitude: number;
    altitude?: number;
    altitude_accuracy?: number;
    heading?: number;
    speed?: number;
    time: EpochTimeStamp;
}

export interface ClientSendButtonPressMessage {
    type: "button";
    id: string;
    args?: string[];
}

export interface ClientFetchButtonArgumentsMessage {
    type: "button";
    action: "get_params";
    id: string;
}
