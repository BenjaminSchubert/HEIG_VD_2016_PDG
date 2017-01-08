import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { IAccount } from "./stubs";
import { AUTH_URL, ACCOUNT_URL } from "../api.routes";
import { Router, ActivatedRoute } from "@angular/router";
import { noop } from "../base";


/**
 * This is a service that allows to fetch user-related information.
 */
@Injectable()
export class AccountService {
    /**
     * Observable of the user's account
     */
    public $: Observable<IAccount>;

    /**
     * Observable telling whether the user is logged in or not
     */
    public isLoggedIn$: Observable<boolean>;

    /**
     * Observable telling whether the user is a staff or not
     */
    public isStaff$: Observable<boolean>;

    private _$: BehaviorSubject<IAccount>;

    constructor(private http: Http, private router: Router, private route: ActivatedRoute) {
        this._$ = new BehaviorSubject(null);
        this.$ = this._$.asObservable();
        this.isLoggedIn$ = this._$.map((a: IAccount) => a !== null);
        this.isStaff$ = this._$.map((a: IAccount) => a !== null && a.is_staff);

        this.getAccount().subscribe(noop, noop);
    }

    /**
     * Login the user with the given information.
     *
     * @param data to authenticate the user
     * @returns {Observable<Response>}
     */
    public login(data: {username: string, password: string}): Observable<Response> {
        return this.http.post(AUTH_URL, data)
            .do(() => this.getAccount().subscribe(() => this.redirect()));
    }

    /**
     * Log the user out
     *
     * @returns {Observable<Response>}
     */
    public logout(): Observable<Response> {
        return this.http.delete(AUTH_URL)
            .do(() => {
                this._$.next(null);
                this.router.navigate(["login"]).then();
            });
    }

    /**
     * Get the user's account
     *
     * @returns {Observable<Response>}
     */
    private getAccount(): Observable<Response> {
        return this.http.get(ACCOUNT_URL)
            .do(
                (res: Response) => {
                    this._$.next(res.json());
                    this.redirect();
                },
                (res: Response) => {
                    if (res.status === 401) {
                        this._$.next(null);
                    }
                },
            );
    }

    /**
     * Redirect the user to the correct url.
     *
     * If a `redirect` query parameter is set, this will send the user to this endpoint.
     * Otherwise, it will send it to the default page.
     */
    private redirect() {
        if (this.route.snapshot.queryParams["redirect"] !== undefined) {
            this.router.navigate([this.route.snapshot.queryParams["redirect"]]).then();
        } else  {
            this.router.navigate([""]).then();
        }
    }
}
