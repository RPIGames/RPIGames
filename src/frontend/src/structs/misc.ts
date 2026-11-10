// One item in the response for when a directory is requested from the backend folder.
export interface ResourceInfo {
    name: string;
    type: "file" | "directory" | "other";
    mtime: string;
    size: number;
}

// Enum of different notification types. The color is based off of this.
export enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
}
