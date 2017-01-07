import { Component } from '@angular/core';
import { Splashscreen as S } from 'ionic-native';

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

  constructor() {
    S.hide();
  }
}
