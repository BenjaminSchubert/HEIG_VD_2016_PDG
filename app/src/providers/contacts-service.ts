import { Injectable } from '@angular/core';

import { AuthService } from './auth-service';

import { CONFIG } from './config';
import { RadyFriend } from '../models/friend';

/**
 * ContactsService
 * Handle the contacts list 
 * Patrick Champion - 21.12.2016
 */
@Injectable()
export class ContactsService {

  // current list
  public contacts: RadyFriend[];

  constructor(public authService: AuthService) {
    console.log('[ContactsService] constructor');

    this.contacts = [];
  }

  /**
   * Fetch informations
   * @return a promise
   */
  fetch() {
    this.contacts = [];
    return this.fetchContacts();
  }

  // Fetch the current user contacts list
  private fetchContacts() {
    return this.authService.get(CONFIG.API_URL + 'users/friends/all/')
      .map(res => res.json())
      .toPromise()
      .then((data) => {
        for(let contact of data) 
          this.contacts.push(contact);                                  
      });
  }
}
