import { Component } from '@angular/core';
import { NavController, Platform, AlertController } from 'ionic-angular';
import { StatusBar } from 'ionic-native';

import { SignIn } from '../sign-in/sign-in';
import { MainTabs } from '../main-tabs/main-tabs';

import { AuthService } from '../../providers/auth-service';
import { PushService } from '../../providers/push-service';
import { NotificationService } from '../../providers/notification-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { GatheringService } from '../../providers/gathering-service';

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
              public notificationService: NotificationService,
              public geolocationService: GeolocationService,
              public gatheringService: GatheringService) {

    // global try-catch
    try {

      // Set the default notification handler
      this.notificationService.setDefaultHandler((n) => {
        this.alertCtrl.create({
          title: n.title,
          message: n.message,
          buttons: ['OK'],
          enableBackdropDismiss: false
        }).present();
      });

      // Specific handlers
      this.gatheringService.configureNotificationHandlers(this.navCtrl);

      // redefine the console.log behavior for device testing
      // /!\ comments those lines for production /!\
      let logger = function(nS) {
        return function(text) {
          nS.notify({
            title: 'CONSOLE.LOG',
            message: text
          });
        };
      };
      console.log = logger(this.notificationService);

      platform.ready().then(() => {

        // Okay, so the platform is ready and our plugins are available.
        // Here you can do any higher level native things you might need.
        StatusBar.styleDefault();
        this.authService.initialize();
        this.pushService.initialize();
        this.geolocationService.initialize();

        // if we are auth => go to MainTabs
        // otherwise      => go to SignIn
        this.authService.refresh()
          .then(() => {
            console.log('[Splashscreen] token refreshed, go to MainTabs');
            this.navCtrl.setRoot(MainTabs);
          }).catch((err) => {
            console.log('[Splashscreen] refresh error: ' + err);
            this.navCtrl.setRoot(SignIn);
          });
      });

    // global try-catch
    }
    catch(e) {
      console.log('[Splashscreen] try-catch: ' + e);
    }
  }
}
