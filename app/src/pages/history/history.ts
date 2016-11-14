import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

@Component({
  selector: 'page-history',
  templateUrl: 'history.html'
})
export class History {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello History Page');
  }

}
