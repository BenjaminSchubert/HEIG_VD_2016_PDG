import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

@Component({
  selector: 'page-edit-profile',
  templateUrl: 'edit-profile.html'
})
export class EditProfile {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello EditProfile Page');
  }

}
