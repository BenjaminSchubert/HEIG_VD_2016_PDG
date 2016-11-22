import { User } from './user';

  /**
   * Contact
   * Custom models for Contacts
   * Thibaut Loiseau - 09.11.2016
   */
  export class History{
    users : User[];
    constructor(users : User[]) { this.users  = users ; }

  }
