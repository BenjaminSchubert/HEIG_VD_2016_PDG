/**
 * Contact
 * Custom models for Contacts
 * Thibaut Loiseau - 09.11.2016
 */
export class RadyUser {
  username: string;
  email: string;
  phone_number: string;
  avatar: string;
  hidden: boolean;
  //TODO : Update constructor
  constructor(username: string) { this.username = username; }

}
