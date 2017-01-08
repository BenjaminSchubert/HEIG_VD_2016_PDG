import { Component } from "@angular/core";
import { UserService } from "./user.service";
import { IUser } from "./stubs";


/**
 * Component to display and manage users
 */
@Component({
    styleUrls: ["./user.scss"],
    templateUrl: "./user.html",
})
export class UserComponent {
    constructor(public service: UserService) {
    }

    /**
     * Promote the given user to admin or revoke his rights if he already is admin.
     *
     * @param user to promote
     */
    public makeAdmin(user: IUser) {
        let copy = JSON.parse(JSON.stringify(user));
        copy.is_staff = !copy.is_staff;
        this.service.update(copy).subscribe();
    }

    /**
     * Activate the given user account or block it if he is already activated.
     *
     * @param user to activate
     */
    public activate(user: IUser) {
        let copy = JSON.parse(JSON.stringify(user));
        copy.is_active = !copy.is_active;
        this.service.update(copy).subscribe();
    }

}
