import "rxjs/add/operator/map";
import "rxjs/add/operator/toPromise";
import "rxjs/add/operator/do";
import { Observable } from "rxjs/Observable";
import { Injectable } from "@angular/core";
import { Http, Response, RequestOptionsArgs } from "@angular/http";
import { AuthHttp, AuthConfig, JwtHelper } from "angular2-jwt";
import { SecureStorage } from "ionic-native";
import { LOGIN_URL, REFRESH_URL, USERS_URL, PASSWORD_RESET_URL } from "../app/api.routes";


@Injectable()
export class AuthService {
    /**
     * Check if the user has a valid token.
     */
    public get authenticated() {
        // tslint:disable-next-line:triple-equals
        return this.token != null && !this.jwtHelper.isTokenExpired(this.token);
    }

    private _token: string;

    private get token() {
        return this._token;
    }

    private readonly TOKEN_NAME: string = "id_token";
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
            .then((token: string) => this.setToken(token))
            // If token load fails, we are not logged in.
            // tslint:disable-next-line:no-empty
            .catch(() => console.log("[Rady][AuthService] Could not load authentication token."))
            .then(() => {
                this.secureHttp = new AuthHttp(
                    new AuthConfig(
                        {
                            globalHeaders: [
                                {"Accept": "application/json"},
                                {"Content-Type": "application/json"},
                            ],
                            tokenGetter: (() => this.token),
                            tokenName: this.TOKEN_NAME,
                        },
                    ),
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
            .do((res: Response) => this.setToken(res.json()["token"]));
    }

    /**
     * Remove the local token.
     */
    public logout() {
        this.setToken(null);
    }

    /**
     * Ask for a reset link for the user's password
     */
    public resetPassword(data: {email: string}) {
        return this.http.post(PASSWORD_RESET_URL, data);
    }

    /**
     * Ask the server for a new token.
     */
    public refresh() {
        return this.http.post(REFRESH_URL, {token: this.token})
            .do((res: Response) => this.setToken(res.json()["token"]));
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
    // tslint:disable-next-line:no-any
    public post(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.post(url, body, options);
    }

    /**
     * Performs a request with `patch` http method.
     */
    // tslint:disable-next-line:no-any
    public patch(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.patch(url, body, options);
    }

    /**
     * Performs a request with `put` http method.
     */
    // tslint:disable-next-line:no-any
    public put(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.put(url, body, options);
    }

    /**
     * Set current user's token
     *
     * @param token value
     */
    private setToken(token: string) {
        return this.storage
            .set(this.TOKEN_NAME, token)
            .then(() => this._token = token);
    }
}
