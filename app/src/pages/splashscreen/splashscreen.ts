import { Component } from '@angular/core';
import { NavController, Platform } from 'ionic-angular';
import { StatusBar } from 'ionic-native';

import { SignIn } from '../sign-in/sign-in';
import { MainTabs } from '../main-tabs/main-tabs';

import { AuthService } from '../../providers/auth-service';

/**
 * Splashscreen
 * Entry point of the app
 * Patrick Champion - 29.10.2016
 */
@Component({
  templateUrl: 'splashscreen.html'
})
export class Splashscreen {

  constructor(public platform: Platform,
              public navCtrl: NavController,
              public authService: AuthService) {
      platform.ready().then(() => {
        // Okay, so the platform is ready and our plugins are available.
        // Here you can do any higher level native things you might need.
        StatusBar.styleDefault();

        // if we are auth => go to MainTabs
        // otherwise      => go to SignIn
        this.authService.initialize();
        this.authService.refresh()
          .then(() => {
            this.navCtrl.setRoot(MainTabs);
          }).catch((err) => {
            this.navCtrl.setRoot(SignIn);
          });
    });
  }
}
