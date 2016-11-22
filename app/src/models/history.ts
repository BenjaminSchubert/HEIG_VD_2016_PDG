import { RadyUser } from './user';
import { RadyLocation } from './location';

  /**
   * Contact
   * Custom models for Contacts
   * Thibaut Loiseau - 09.11.2016
   */
  export class RadyHistory{
    users : RadyUser[];
    coord : RadyLocation;
    constructor(users : RadyUser[]) { this.users  = users ; }

  }
