import { Injectable } from "@angular/core";
import { ACCOUNT_URL } from "../app/api.routes";
import { AuthService } from "./auth-service";
import { RestService } from "../lib/rest-service";
import { IAccount } from "../lib/stubs/account";


@Injectable()
export class AccountService extends RestService<IAccount> {
    constructor(http: AuthService) {
        super(http, ACCOUNT_URL);
    }
}
