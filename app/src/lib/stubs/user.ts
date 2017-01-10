export interface IUser {
    friend: {
        username: string;
    };
    id: number;
    is_accepted: boolean;
    is_blocked: boolean;
    is_hidden: boolean;
    initiator: boolean;
}
