/**
 * Contact
 * Custom models for Contacts
 * Thibaut Loiseau - 09.11.2016
 */
export class RadyUser {
  id: number;
  username: string;
  avatar?: string;
  last_avatar_update?: string;

  constructor(username?: string) {
    this.username = username;
  }
}
