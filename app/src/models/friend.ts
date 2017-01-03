import { RadyUser } from './user';

/**
 * RadyFriend
 * Model for friend (contact)
 * Patrick Champion - 21.12.2016
 */
export class RadyFriend {

    friend: RadyUser;
    is_accepted: boolean;
    is_blocked: boolean;
    is_hidden: boolean;
    initiator: boolean;
    
    checked: boolean = false; // for ContactList
}