import "rxjs/add/operator/map";
import "rxjs/add/operator/toPromise";
import "rxjs/add/operator/do";
import { Observable } from "rxjs/Observable";
import { Injectable } from "@angular/core";
import { Http, Response, RequestOptionsArgs } from "@angular/http";
import { AlertController } from "ionic-angular";
import { AuthHttp, AuthConfig, JwtHelper } from "angular2-jwt";
import { SecureStorage } from "ionic-native";
import { LOGIN_URL, REFRESH_URL, USERS_URL, PASSWORD_RESET_URL } from "../app/api.routes";


function noop() {
}


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
     * @param alertCtrl to show popup to the user
     */
    constructor(private http: Http, private alertCtrl: AlertController) {
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
        // FIXME: Login user NOW
        return this.http.post(USERS_URL, information)
            .do(noop, (err: Response) => this.checkResponse(err));
    }

    /**
     * Ask the server for a token.
     *
     * @param credentials with which to login (email, password).
     */
    public login(credentials: {email: string, password: string}) {
        return this.http.post(LOGIN_URL, credentials)
            .do(
                (res: Response) => {
                    console.log("[Rady][AuthService] user logged in");
                    this.setToken(res.json()["token"]).then();
                },
                (err: Response) => this.checkResponse(err),
            );
    }

    /**
     * Remove the local token.
     */
    public logout() {
        return this.storage.remove(this.TOKEN_NAME);
    }

    /**
     * Ask for a reset link for the user's password
     */
    public resetPassword(data: {email: string}) {
        return this.http.post(PASSWORD_RESET_URL, data)
            .do(noop, (err: Response) => this.checkResponse(err));
    }

    /**
     * Ask the server for a new token.
     */
    public refresh() {
        return this.http.post(REFRESH_URL, {token: this.token})
            .do(
                (res: Response) => this.setToken(res.json()["token"]),
                (err: Response) => this.checkResponse(err),
            );
    }

    /**
     * Performs a request with `get` http method
     */
    public get(url: string, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.get(url, options)
            .do(noop, (err: Response) => this.checkResponse(err));
    }

    /**
     * Performs a request with `post` http method.
     */
    // tslint:disable-next-line:no-any
    public post(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.post(url, body, options)
            .do(noop, (err: Response) => this.checkResponse(err));
    }

    /**
     * Performs a request with `patch` http method.
     */
    // tslint:disable-next-line:no-any
    public patch(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.patch(url, body, options)
            .do(noop, (err: Response) => this.checkResponse(err));
    }

    /**
     * Performs a request with `put` http method.
     */
    // tslint:disable-next-line:no-any
    public put(url: string, body: any, options?: RequestOptionsArgs): Observable<Response> {
        return this.secureHttp.put(url, body, options)
            .do(noop, (err: Response) => this.checkResponse(err));
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

    private checkResponse(res: Response) {
        if (res.status >= 500) {
            this.notifyServerError();
        } else if (res.status === 0) {
            // Angular 2 returns 0 when there was no connection
            this.notifyMissingConnection();
        }
    }

    private notifyMissingConnection() {
        this.notify("Can't contact server", "You don't seem to have network access, please enable it");
    }

    private notifyServerError() {
        this.notify("Unexpected error", "The server failed, please contact the support if this continues");
    }

    private notify(title: string, message: string) {
        this.alertCtrl.create({
            buttons: ["OK"],
            enableBackdropDismiss: false,
            message: message,
            title: title,
        }).present().then();
    }
}
