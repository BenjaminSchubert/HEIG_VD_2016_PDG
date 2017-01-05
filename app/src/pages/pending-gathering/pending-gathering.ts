import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/*
  Generated class for the PendingGathering page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-pending-gathering',
  templateUrl: 'pending-gathering.html'
})
export class PendingGathering {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello PendingGathering Page');
  }

}
