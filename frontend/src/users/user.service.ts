import { Observable } from "rxjs/Observable";
import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import { IUser } from "./stubs";
import { RestService } from "../base/rest.service";
import { USERS_URL } from "../api.routes";


/**
 * This is a service that allows to fetch statistics
 */
@Injectable()
export class UserService extends RestService<IUser[]> {
    constructor(http: Http) {
        super(USERS_URL, http);
    }

    /**
     * Update the given user and propagates the changes.
     *
     * @param user to update
     * @returns {Observable<Response>}
     */
    public update(user: IUser): Observable<Response> {
        return this.http.put(`${USERS_URL}/${user.id}/`, user).do((res: Response) => {
            let json = res.json();
            let index = this.data.findIndex((u: IUser) => u.id === json.id);
            this.data[index] = json;
            this.data = this.data.splice(0); // we recreate a new object to work with observables
            this._$.next(this.data);
        });
    }
}
