import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

import { SignIn } from '../sign-in/sign-in';

/**
 * Splashscreen
 * Entry point of the app
 * Patrick Champion - 29.10.2016
 */
@Component({
  templateUrl: 'splashscreen.html'
})
export class Splashscreen {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
  	// just emulate a charging then go to the sign-in page
  	setTimeout(() => { this.navCtrl.setRoot(SignIn); }, 3000);
  }
}
