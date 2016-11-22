import { User } from './user';
import { Location } from './location';

  /**
   * Contact
   * Custom models for Contacts
   * Thibaut Loiseau - 09.11.2016
   */
  export class History{
    users : User[];
    coord : Location;
    constructor(users : User[]) { this.users  = users ; }

  }
