import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

/*
  Generated class for the CreateGathering page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-create-gathering',
  templateUrl: 'create-gathering.html'
})
export class CreateGathering {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello CreateGathering Page');
  }

}
