import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/**
 * AddContactFromScanner
 * Add a contact scanned by his QR code
 * Patrick Champion - 16.11.2016
 */
@Component({
  templateUrl: 'add-contact-from-scanner.html'
})
export class AddContactFromScanner {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
  }

}
