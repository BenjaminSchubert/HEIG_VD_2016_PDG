import "rxjs/add/observable/throw";
import { Injectable } from "@angular/core";
import { Response } from "@angular/http";
import { ACCOUNT_URL } from "../app/api.routes";
import { AuthService } from "./auth-service";
import { ObjectService } from "../lib/rest-service";
import { IAccount } from "../lib/stubs/account";


@Injectable()
export class AccountService extends ObjectService<IAccount> {
    constructor(http: AuthService) {
        super(http, ACCOUNT_URL);
    }

    public hide() {
        return this.http.patch(ACCOUNT_URL, {is_hidden: !this._$.getValue().is_hidden}).do(
            // tslint:disable-next-line:no-empty
            (res: Response) => this._$.next(res.json()),
            (err: Response) => this._$.getValue().is_hidden = !this._$.getValue().is_hidden,
        );
    }
}
