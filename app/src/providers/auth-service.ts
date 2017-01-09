import "rxjs/add/operator/map";
import "rxjs/add/operator/toPromise";
import "rxjs/add/operator/do";

import { Observable } from "rxjs/Observable";
import { Injectable } from "@angular/core";
import { Http, Response, RequestOptionsArgs } from "@angular/http";
import { AuthHttp, AuthConfig, JwtHelper } from "angular2-jwt";
import { SecureStorage } from "ionic-native";
import { LOGIN_URL, REFRESH_URL, USERS_URL } from "../app/api.routes";


@Injectable()
export class AuthService {
    /**
     * Check if the user has a valid token.
     */
    public get authenticated() {
        return this.token != null && !this.jwtHelper.isTokenExpired(this.token);
    }

    private _token: string;

    private get token() {
        return this._token;
    }

    private set token(token: string) {
        this.storage
            .set(this.TOKEN_NAME, token)
            .then((_token: string) => this._token = _token);
    }

    private readonly TOKEN_NAME: string = "token";
    private readonly STORE_NAME: string = "auth-service-store";

    private secureHttp: AuthHttp;
    private storage: SecureStorage;
    private jwtHelper: JwtHelper = new JwtHelper();

    /**
     * @param http angular2 http service
     */
    constructor(private http: Http) {
    }

    /**
     * Initialize the service.
     *
     * Must be called one time, when the platform is ready.
     */
    public initialize() {
        this.storage = new SecureStorage();
        return this.storage.create(this.STORE_NAME)
            .then(() => this.storage.get(this.TOKEN_NAME))
            .then((token: string) => this.token = token)
            .then(() => {
                this.secureHttp = new AuthHttp(
                    new AuthConfig({
                        tokenGetter: (() => this.token),
                        tokenName: this.TOKEN_NAME,
                    }),
                    this.http,
                );
            });
    }

    /**
     * Create a new user.
     *
     * @param information concerning the user (username, email, password, phone?, country?).
     * @return an observable of the server's answer.
     */
    public register(information) {
        // FIXME: add info for current user
        return this.http.post(USERS_URL, information);
    }

    /**
     * Ask the server for a token.
     *
     * @param credentials with which to login (email, password).
     */
    public login(credentials: {email: string, password: string}) {
        return this.http.post(LOGIN_URL, credentials)
            .do((res: Response) => this.token = res.json());
    }

    /**
     * Remove the local token.
     */
    public logout() {
        this.token = null;
    }

    /**
     * Ask the server for a new token.
     */
    public refresh() {
        return this.http.post(REFRESH_URL, {token: this.token})
            .do((res: Response) => this.token = res.json());
    }

    /**
     * Performs a request with `get` http method
     */
    public get(url: string, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.get(url, options);
    }

    /**
     * Performs a request with `post` http method.
     */
    public post(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.post(url, options);
    }

    /**
     * Performs a request with `patch` http method.
     */
    public patch(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.patch(url, body, options);
    }

}
