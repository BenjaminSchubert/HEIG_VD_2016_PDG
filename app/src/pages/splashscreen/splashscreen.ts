import { Component } from '@angular/core';
import { NavController, Platform, AlertController } from 'ionic-angular';
import { StatusBar, Toast } from 'ionic-native';

import { SignIn } from '../sign-in/sign-in';
import { MainTabs } from '../main-tabs/main-tabs';

import { AuthService } from '../../providers/auth-service';
import { PushService } from '../../providers/push-service';
import { NotificationService } from '../../providers/notification-service';

/**
 * Splashscreen
 * Entry point of the app
 * Patrick Champion - 29.10.2016
 */
@Component({
  templateUrl: 'splashscreen.html'
})
export class Splashscreen {

  constructor(public platform: Platform,
              public navCtrl: NavController,
              public alertCtrl: AlertController,
              public authService: AuthService,
              public pushService: PushService,
              public notificationService: NotificationService) {

      // redefine the console.log behavior for device testing
      // /!\ comments those lines for production /!\
      console.log = (function(text) {
        Toast.hide().then(() => {
          Toast.show(
            Date.now().toLocaleString() + ':\n' + text, 
            '10000', 
            'top'
          ).subscribe();
        });
      });

      // Set the default notification handler
      this.notificationService.setDefaultHandler((n) => {
        this.alertCtrl.create({
          title: n.title,
          message: n.message,
          buttons: ['OK'],
          enableBackdropDismiss: false
        }).present();
      });

      platform.ready().then(() => {

        // Okay, so the platform is ready and our plugins are available.
        // Here you can do any higher level native things you might need.
        StatusBar.styleDefault();
        this.authService.initialize();
        this.pushService.initialize();

        // if we are auth => go to MainTabs
        // otherwise      => go to SignIn
        this.authService.refresh()
          .then(() => {
            this.navCtrl.setRoot(MainTabs);
          }).catch((err) => {
            this.navCtrl.setRoot(SignIn);
          });
    });
  }
}