import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { User } from '../../models/user';

import { EditProfile } from '../edit-profile/edit-profile';

@Component({
  templateUrl: 'settings.html'
})
export class Settings {

  user: User;

  constructor(public navCtrl: NavController,
              public app: App) {
    //TODO : LOAD USER
    this.user = new User('Sauron');
  }

  ionViewDidLoad() {
    console.log('Hello Settings Page');
  }

  goToEditProfile(){
    this.app.getRootNav().push(EditProfile);
  }

}
