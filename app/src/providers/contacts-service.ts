import { Injectable } from "@angular/core";
import { AuthService } from "./auth-service";
import { RadyFriend } from "../models/friend";
import { RestService } from "../lib/rest-service";
import { FRIENDS_URL, ALL_FRIENDS_URL } from "../app/api.routes";
import { IUser } from "../lib/stubs/user";


/**
 * ContactsService
 * Handle the contacts list
 * Patrick Champion - 21.12.2016
 */
@Injectable()
export class ContactsService extends RestService<IUser> {

    // current list
    public contacts: RadyFriend[];

    constructor(public authService: AuthService) {
        super(authService, ALL_FRIENDS_URL);
        console.log("[ContactsService] constructor");

        this.contacts = [];
    }

    public accept(id: number) {
        return this.modify(id, {is_accepted: true});
    }

    public block(id: number) {
        return this.modify(id, {is_blocked: true});
    }

    public hide(id: number) {
        return this.modify(id, {is_hidden: true});
    }

    public unblock(id: number) {
        return this.modify(id, {is_blocked: false});
    }

    /**
     * Fetch informations
     * @return a promise
     */
    fetch() {
        this.contacts = [];
        return super.fetch().do((res: any) => this.contacts = res.json());
    }

    private modify(id: number, info: any) {
        return this.authService.patch(`${FRIENDS_URL}${id}/`, info)
            .do(() => this.fetch().subscribe());
    }

}
