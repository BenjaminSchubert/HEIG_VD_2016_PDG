import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

import { AddContactFromList } from '../add-contact-from-list/add-contact-from-list';
import { AddContactFromScanner } from '../add-contact-from-scanner/add-contact-from-scanner';
import { MyQrCode } from '../my-qr-code/my-qr-code';

/**
 * AddContact
 * Adding a new contact from differents sources
 * Patrick Champion - 15.11.2016
 */
@Component({
  templateUrl: 'add-contact.html'
})
export class AddContact {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    
  }

  goToAddContactFromList() {
    this.navCtrl.push(AddContactFromList);
  }

  goToAddContactFromScanner() {
    this.navCtrl.push(AddContactFromScanner);
  }

  goToMyQrCode() {
    this.navCtrl.push(MyQrCode);
  }
}
