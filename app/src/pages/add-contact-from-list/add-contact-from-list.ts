import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/**
 * AddContactFromList
 * Add contact, contacts are found in the phone contact list
 * Patrick Champion - 16.11.2016
 */
@Component({
  templateUrl: 'add-contact-from-list.html'
})
export class AddContactFromList {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
  }

}
