import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/**
 * MyQrCode
 * Generate and show the user QR code
 * Patrick Champion - 16.11.2016
 */
@Component({
  templateUrl: 'my-qr-code.html'
})
export class MyQrCode {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello MyQrCode Page');
  }

}
