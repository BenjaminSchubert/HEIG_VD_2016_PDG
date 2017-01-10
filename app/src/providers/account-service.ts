import "rxjs/add/observable/throw";
import { Injectable } from "@angular/core";
import { Response } from "@angular/http";
import { ACCOUNT_URL } from "../app/api.routes";
import { AuthService } from "./auth-service";
import { RestService } from "../lib/rest-service";
import { IAccount } from "../lib/stubs/account";


@Injectable()
export class AccountService extends RestService<IAccount> {
    constructor(http: AuthService) {
        super(http, ACCOUNT_URL);
    }

    public hide() {
        return this.update(this._$.getValue()).do(
            // tslint:disable-next-line:no-empty
            () => {
            },
            (err: Response) => {
                this._$.getValue().is_hidden = !this._$.getValue().is_hidden;
            },
        );
    }
}
