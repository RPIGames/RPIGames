// One item in the response for when a directory is requested from the backend folder.
export interface ResourceInfo {
    name: string;
    type: "file" | "directory" | "other";
    mtime: string;
    size: number;
}
