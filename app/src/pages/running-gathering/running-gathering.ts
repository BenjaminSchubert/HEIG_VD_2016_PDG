import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/*
  Generated class for the RunningGathering page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-running-gathering',
  templateUrl: 'running-gathering.html'
})
export class RunningGathering {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello RunningGathering Page');
  }

}
