import { AbstractControl } from '@angular/forms';


export module RadyModels {

  /**
   * Contact
   * Custom models for Contacts
   * Thibaut Loiseau - 09.11.2016
   */
  export class User{
    username : String;
    email : String;
    phone_number : String;
    avatar : String;
    hidden : Boolean;
    //TODO : Update constructor
    constructor(username : string) { this.username  = username ; }

  }

}
