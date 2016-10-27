import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/*
  Generated class for the Splashscreen page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-splashscreen',
  templateUrl: 'splashscreen.html'
})
export class Splashscreen {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello Splashscreen Page');
  }

}
