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
    max_members: number;
    curr_members: number;
    needs_secret: boolean;
};

export interface LobbyJoinRequest {
    lobby_id: string; // the lobby id you wish to join
    lobby_secret?: string; // the lobby's secret, if the lobby you are trying to join is a private one
}

export interface MakeLobbyRequest {
    game_type_id: string
    game_capacity: number
    game_config: Map<string, string | number | boolean>
    name?: string; // (optional )name of the new lobby
    secret?: string; // (optional) secret that the private lobby needs to join
}

export interface LobbyPassLeadershipRequest {
    grantee_id: string; // uuid of the user to grant to
}
