import { Injectable } from "@angular/core";
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from "@angular/router";
import { AccountService } from "../account.service";
import { Observable } from "rxjs/Observable";


/**
 * Guard to check that a user is logged in before accessing a given component
 */
@Injectable()
export class LoginGuard implements CanActivate {
    /**
     * @param router to handle navigation
     * @param user to access user information
     */
    constructor(protected router: Router, protected user: AccountService) {}

    public canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
        return  this.user.isLoggedIn$.take(1)
            .do((loggedIn: boolean) => {
                if (!loggedIn) {
                    this.router.navigate(["login"], {queryParams: {redirect: route.url}}).then();
                }
            });
    }

}


/**
 * Guard to check that a user is not logged in before accessing a given component
 */
@Injectable()
export class LogoutGuard extends LoginGuard {
    public canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
        return this.user.isLoggedIn$.take(1).map((loggedIn: boolean) => !loggedIn);
    }

}
