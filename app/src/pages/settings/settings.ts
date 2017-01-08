import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { EditProfile } from '../edit-profile/edit-profile';
import { SignIn } from '../sign-in/sign-in';

import { AuthService } from '../../providers/auth-service';
import { MeService } from '../../providers/me-service';

@Component({
  templateUrl: 'settings.html'
})
export class Settings {

  constructor(public navCtrl: NavController,
              public app: App,
              public authService: AuthService,
              public meService: MeService) {
    // nothing
  }

  ionViewDidLoad() {
    this.meService.fetch();
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
