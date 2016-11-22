import { RadyUser } from './user';
import { RadyLocation } from './location';

  /**
   * Contact
   * Custom models for Contacts
   * Thibaut Loiseau - 09.11.2016
   */
  export class RadyHistory{
    users : RadyUser[];
    location : RadyLocation;
    date : string;
    constructor(users : RadyUser[], location : RadyLocation, date : string) {
      this.users  = users ;
      this.location = location
      this.date = date;
    }

  }
