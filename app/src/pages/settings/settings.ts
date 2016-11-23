import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { RadyUser } from '../../models/user';

import { EditProfile } from '../edit-profile/edit-profile';

@Component({
  templateUrl: 'settings.html'
})
export class Settings {

  user: RadyUser;

  constructor(public navCtrl: NavController,
              public app: App) {
    //TODO : LOAD USER
    this.user = new RadyUser('Sauron');
  }

  ionViewDidLoad() {
    console.log('Hello Settings Page');
  }

  goToEditProfile(){
    this.app.getRootNav().push(EditProfile);
  }

  doLogOut(){
    //TODO : LOG OUT 
  }

}
