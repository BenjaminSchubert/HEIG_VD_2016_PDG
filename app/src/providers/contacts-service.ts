import { Injectable } from "@angular/core";
import { AuthService } from "./auth-service";
import { RadyFriend } from "../models/friend";
import { RestService } from "../lib/rest-service";
import { FRIENDS_URL, ALL_FRIENDS_URL, USERS_URL } from "../app/api.routes";
import { IUser } from "../lib/stubs/user";
import { NotificationService } from "./notification-service";


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

    public configureNotificationHandlers(nS: NotificationService) {

        let f = (n) => {
            this.fetch().subscribe();
            nS.notify({
                message: n.message,
                title: n.title,
            });
        };

        nS.addHandler("friend-request", (n) => f(n));
        nS.addHandler("friend-request-accepted", (n) => f(n));
    }

    public search(s: string) {
        return this.http.get(`${USERS_URL}?username=${s}`);
    }

    public addFriend(user: IUser) {
        return this.http.post(FRIENDS_URL, {friend: user.id})
            .do(() => this.fetch().subscribe());
    }

    private modify(id: number, info: any) {
        return this.authService.patch(`${FRIENDS_URL}${id}/`, info)
            .do(() => this.fetch().subscribe());
    }
}
