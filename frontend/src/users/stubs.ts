/**
 * Interface for a base user
 */
export interface IUser {
    id: number;
    is_active: boolean;
    is_staff: boolean;
    username: string;
    email: string;
}
