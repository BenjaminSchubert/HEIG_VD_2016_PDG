import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from 'ionic-native';

import { Splashscreen } from '../pages/splashscreen/splashscreen';

/**
 * RadyApp
 * Launch the Splashscreen page
 * Patrick Champion - 29.10.2016
 */
@Component({
  template: `<ion-nav [root]="rootPage"></ion-nav>`
})
export class RadyApp {
  rootPage = Splashscreen;

  constructor(platform: Platform) {
    platform.ready().then(() => {
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      StatusBar.styleDefault();
    });
  }
}
