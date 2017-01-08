import { Injectable } from '@angular/core';

import { AuthService } from './auth-service';

import { CONFIG } from './config';
import { RadyUser } from '../models/user';

/**
 * MeService
 * Handle the current user 
 * Patrick Champion - 21.12.2016
 */
@Injectable()
export class MeService {

  // current user
  public me: RadyUser;

  // hidden ?
  public hidden: boolean;

  constructor(public authService: AuthService) {
    console.log('[MeService] constructor');

    this.me = null;
    this.hidden = false; // TODO: get it from storage (in fetch())
  }

  /**
   * Fetch informations
   * @return a promise
   */
  fetch() {
    this.me = null;
    return this.fetchMe();
  }

  // Fetch the current user 
  private fetchMe() {
    return this.authService.http().get(CONFIG.API_URL + 'users/me/')
      .map(res => res.json())
      .toPromise()
      .then((data) => this.me = data);
  }
}
