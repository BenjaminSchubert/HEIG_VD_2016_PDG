import { Injectable } from '@angular/core';
import { Http, Headers, RequestOptions } from '@angular/http';
import { AuthHttp, AuthConfig, JwtHelper } from 'angular2-jwt';
import { SecureStorage } from 'ionic-native';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

import { CONFIG } from './config';

/**
 * AuthService
 * Authentification service using JWT
 * Patrick Champion - 16.11.2016
 *
 * Thanks:
 * - https://auth0.com/blog/ionic-2-authentication-how-to-secure-your-mobile-app-with-jwt/
 * - https://github.com/auth0/angular2-jwt
 * - http://ionicframework.com/docs/v2/native/secure-storage/
 */
@Injectable()
export class AuthService {

  // constants
  private TOKEN_NAME: string = 'id_token';
  private STORE_NAME: string = 'auth-service-store';
  private BASE_URL: string = CONFIG.API_URL;
  private LOGIN_URL: string = this.BASE_URL + 'auth/login/';
  private REFRESH_URL: string = this.BASE_URL + 'auth/refresh/';
  private REGISTER_URL: string = this.BASE_URL + 'users/';

  // data members
  private authHttp: AuthHttp;
  private storage: SecureStorage;

  /**
   * Constructor
   * @param baseHttp Injection of the Angular2 Http service
   */
  constructor(private baseHttp: Http) {
    // initialize() must be called when the plateform is ready 
  }

  /**
   * Initialize the service
   * Must be called one time, when the plateform is ready
   */
  initialize() {
    console.log('[AuthService] initialisation');

    // setup a storage for the service
    this.storage = new SecureStorage();
    this.storage.create(this.STORE_NAME).then(
      () => console.log('[AuthService] storage ready'),
      err => console.log('[AuthService] storage error (' + JSON.stringify(err) + ')')
    );

    // setup the Http wrapper
    this.authHttp = new AuthHttp(new AuthConfig({
      tokenName: this.TOKEN_NAME,
      tokenGetter: (() => this.tokenString()) 
    }), this.baseHttp);
  }

  /**
   * Create a new user
   * @param informations object containing the user'sinformations
   *                     (username, email, password, phone?, country?)
   * @return a promise
   */
  register(informations) {

    // send a request to create a new user
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ 'headers': headers });
    return this.baseHttp.post(
        this.REGISTER_URL, 
        JSON.stringify(informations), 
        options
      )
      .map(res => res.json())
      .toPromise();
  }

  /**
   * Ask the server for a token
   * @param credentials object containing the user's credentials
   *                    (email, password)
   * @return a promise
   */
  authentificate(credentials) {

    // send a login request to get a token
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ 'headers': headers });
    return this.baseHttp.post(
        this.LOGIN_URL, 
        JSON.stringify(credentials), 
        options
      )
      .map(res => res.json())
      .toPromise()
      .then((data) => {

        // we have a token, save it in the storage
        this.setTokenString(data.token);
        this.storage.set(this.TOKEN_NAME, data.token)
          .catch((err) => console.log('[AuthService] cannot save token'));
      });
  }

  /**
   * Ash the server for a refreshed token
   * @return a promise
   */
  refresh() {

    // look for the storaged token, and refresh it
    return this.token().then((token) => {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ 'headers': headers });
        this.baseHttp.post(
          this.REFRESH_URL,
          JSON.stringify({ 'token': token }),
          options
        )
        .map(res => res.json())
        .toPromise()
        .then((data) => {

          // we have a token, save it in the storage
          this.setTokenString(data.token);
          this.storage.set(this.TOKEN_NAME, data.token)
            .catch((err) => console.log('[AuthService] cannot save token'));
        });
      });
  }

  /**
   * Check if the user has a valid token
   * @return a promise
   */
  authentificated() {
    return this.token().then((token) => {
        if(new JwtHelper().isTokenExpired(token))
          throw ""; // to do to the catch
      });
  }

  /**
   * Remove the local token
   * @return a promise
   */
  logout() {
      this.setTokenString(null);
      return this.storage.remove(this.TOKEN_NAME);
  }

  /**
   * Returns the token
   * @return a promise
   */
  token() {
    return this.storage.get(this.TOKEN_NAME);
  }

  /**
   * Get the claims contained in the token
   * @return a promise
   */
  claims() {
    return this.token().then((token) => { 
        return new JwtHelper().decodeToken(token); 
      });
  }

  /**
   * Returns a reference to the wrapped Http service
   * @return A reference to the AuthHttp service
   */
  http() {
    return this.authHttp;
  }

  /**
   * Create a RequestOptions from headers
   * @param headers array of object (name, value)
   * @return
   */
  createOptions(headers) {
    let h = new Headers();
    for(let header of headers)
      h.append(header.name, header.value);
    return new RequestOptions({ 'headers': h });
  }

  /**
   * Get/Set the stringified token
   * For internal uses only
   * @return The stringified token
   */
  private tokenStringValue: string;
  private setTokenString(token: string) {
    this.tokenStringValue = token;
  }
  private tokenString() {
    return this.tokenStringValue;
  }
}
