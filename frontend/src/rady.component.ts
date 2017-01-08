import { Component, ViewEncapsulation } from "@angular/core";
import { AccountService } from "./auth/account.service";


/**
 * Main component for the application
 */
@Component({
    encapsulation: ViewEncapsulation.None,
    selector: "rd-app",
    styleUrls: ["rady.scss"],
    templateUrl: "rady.html",
})
export class RadyComponent {
    constructor(public account: AccountService) {}

    /**
     * Logout current user
     */
    public logout() {
        this.account.logout().subscribe();
    }
}
