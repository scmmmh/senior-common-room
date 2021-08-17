/// <reference types="svelte" />

interface ApiMessage {
    type: string;
    payload?: AuthenticatePayload | RoomConfigPayload[] | ScheduleConfigPayload[] | TimezonesConfigPayload | TilesetPayload | UserPayload | EnterJitsiRoomPayload | OpenJitsiRoomPayload | JitsiRoomUsersPayload | UpdateProfilePlayload | UpdateAvatarImagePayload | SetAvatarLocationPayload | UpdateAvatarLocationPayload | LeaveMapPayload | BadgeConfigPayload[] | BroadcastMessagePayload | UserMessagePayload | RequestVideoChatPayload;
}

interface AuthenticatePayload {
    email: string;
    remember: boolean;
    token?: string;
}

interface CoreConfigPayload {
    title: string;
}

interface RoomConfigPayload {
    slug: string;
    label: string;
    mapUrl: string;
    tilesets: TilesetPayload[];
}

interface TimezonesConfigPayload {
    timezones: string[];
}

interface ScheduleConfigPayload {
    title: string;
    start_date: string;
    start_time: string;
    end_date: string;
    end_time: string;
    day_diff: number;
    room: string | null;
    description: string | null;
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
    roles: string[];
    blocked_users: number[];
    timezone: string;
}

interface EnterJitsiRoomPayload {
    name: string;
    subject: string;
}

interface OpenJitsiRoomPayload {
    room_name: string;
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
    roles: string[];
}

interface LeaveMapPayload {
    room: string;
}

interface BadgeConfigPayload {
    title: string;
    url: string;
    role: string;
    self_assigned: boolean;
}

interface BroadcastMessagePayload {
    message: string;
}

interface UserMessagePayload {
    user: UserPartialPayload;
    message: string;
}

interface UserPartialPayload {
    id: number;
    name?: string;
    avatar?: string;
}

interface RequestVideoChatPayload {
    user: UserPartialPayload;
    room?: string;
}

interface JitsiRoomUsersPayload {
    users: number[];
}

interface UpdateProfilePlayload {
    name?: string;
    email?: string;
    timezone?: string;
    roles?: string[];
}
