/// <reference types="svelte" />

interface ApiMessage {
    type: string;
    payload?: AuthenticatePayload | RoomConfigPayload[] | TilesetPayload | UserPayload | EnterJitsiRoomPayload | OpenJitsiRoomPayload | UpdateAvatarImagePayload | SetAvatarLocationPayload | UpdateAvatarLocationPayload | LeaveMapPayload;
}

interface AuthenticatePayload {
    email: string;
    remember: boolean;
    token?: string;
}

interface RoomConfigPayload {
    slug: string;
    label: string;
    mapUrl: string;
    tilesets: TilesetPayload[];
}

interface TilesetPayload {
    name: string;
    url: string;
}

interface UserPayload {
    id: number;
    name: string;
    email: string;
    avatar: string;
}

interface EnterJitsiRoomPayload {
    name: string;
    subject: string;
}

interface OpenJitsiRoomPayload {
    name: string;
    subject: string;
    url: string;
    password: string;
    jwt?: string;
}

interface UpdateAvatarImagePayload {
    imageData: string;
}

interface SetAvatarLocationPayload {
    room: string;
    x: number;
    y: number;
}

interface UpdateAvatarLocationPayload {
    user: UpdateAvatarLocationUserPayload;
    room: string;
    x: number;
    y: number;
}

interface UpdateAvatarLocationUserPayload {
    id: number;
    avatar: string;
    name: string;
}

interface LeaveMapPayload {
    room: string;
}
