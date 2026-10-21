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
    | ServerStatusMessage
    | ServerTimerMessage
    | ServerScoreboardMessage
    | ServerChatMessage
    | ServerErrorMessage;

export interface ServerStatusMessage {
    type: "status";
    status: "connection established" | "authenticated";
}

// Timers

export type ServerTimerMessage =
    | ServerUpdateTimerMessage
    | ServerDeleteTimerMessage
    | ServerRecieveAllTimerMessage;

export interface ServerUpdateTimerMessage {
    type: "timer";
    action: "update";
    data: TimerData;
}

export interface ServerDeleteTimerMessage {
    type: "timer";
    action: "delete";
    id: string; // id of the timer to delete
}

export interface ServerRecieveAllTimerMessage {
    type: "timer";
    action: "recieve_all";
    data: TimerData[];
}

export interface TimerData {
    id: string; // id of the timer that this identifies
    name: string;
    time: string; // time in ??? format
}

// Scoreboard

export type ServerScoreboardMessage =
    | ServerUpdateScoreboardMessage
    | ServerDeleteScoreboardMessage
    | ServerRecieveAllScoreboardMessage;

export interface ServerUpdateScoreboardMessage {
    type: "scoreboard";
    action: "update";
    data: ScoreboardData;
}

export interface ServerDeleteScoreboardMessage {
    type: "scoreboard";
    action: "delete";
    id: Uuid; // the uuid of the scoreboard
}

export interface ServerRecieveAllScoreboardMessage {
    type: "scoreboard";
    action: "recieve_all";
    data: ScoreboardData[];
}

export interface ScoreboardData {
    id: Uuid; // uuid of the scoreboard
    name: string;
    sortable: boolean; // if the scoreboard is sortable from the frontend
    headers: string[]; // list of headers
    rows: string[][];
}

// Chat

export type ServerChatMessage = ServerRecieveChatMessage;

export interface ServerRecieveChatMessage {
    type: "chat";
    room_id: Uuid;
    author_id: Uuid;
    message: string;
}

// Map

// TODO: Add map message models when schema is stabilized

// Buttons

// TODO: Add button message models when schema is stabilized

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
    | ClientSendLocationMessage;

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

// TODO: Add map message models when schema is stabilized
// TODO: Add button message models when schema is stabilized
