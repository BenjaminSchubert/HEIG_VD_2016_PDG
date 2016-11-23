import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { RadyUser } from '../../models/user';

import { EditProfile } from '../edit-profile/edit-profile';
import { SignIn } from '../sign-in/sign-in';

import { AuthService } from '../../providers/auth-service';

@Component({
  templateUrl: 'settings.html'
})
export class Settings {

  user: RadyUser;

  constructor(public navCtrl: NavController,
              public app: App,
              public authService: AuthService) {
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
    this.authService.logout().then(() => {
      this.navCtrl.setRoot(SignIn);
    });
  }

}
