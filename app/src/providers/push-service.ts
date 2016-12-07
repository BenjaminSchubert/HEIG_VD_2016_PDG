import { Injectable } from '@angular/core';
import { Push, Device } from 'ionic-native';

import { AuthService } from './auth-service';
import { CONFIG } from './config';

/**
 * PushService
 * Init and listen push notifications
 * Patrick Champion - 07.12.2016
 */
@Injectable()
export class PushService {

  // push instance
  public push: any = null;

  // token
  public token: string = null;

  // registered to server?
  public registered: boolean = false;

  constructor(private authService: AuthService) {
    // initialize() must be called when the plateform is ready 
  }

  /**
   * Initialize the service
   * Must be called one time, when the plateform is ready
   */
  initialize() {
    console.log('[PushService] initialisation');

    // initialize the service
    this.push = Push.init({
      android: {
        senderID: '395862006671'
      },
      ios: {
        alert: 'true',
        badge: true,
        sound: 'false'
      },
      windows: {}
    });

    // when we have the token, register to the server
    this.push.on('registration', (data) => {
      this.token = data.registrationId;
      this.register();
    });

    // on notification, dispatch the message
    this.push.on('notification', (data) => {

      // TEST
      console.log('[PushService] notification: \n' + JSON.stringify(data));
    });

    // on error
    this.push.on('error', (data) => {

      // TEST
      console.log('[PushService] error: \n' + JSON.stringify(data));
    });
  }

  /**
   * Register the FCM token
   */
  private register() {

    // here come the logic
    let id: any = null;
    let callback: any = (() => {
      console.log('[PushService] try registration');

      // we need to be auth.
      if(this.authService.authentificated()) {

        // registration
        this.authService.http().post(
          CONFIG.API_URL + 'fcm/devices/',
          JSON.stringify({
            type: Device.device.platform,
            registration_id: this.token,
            device_id: Device.device.uuid
          }),
          this.authService.createOptions([
            {'name': 'Content-Type', 'value': 'application/json'}
          ])
        )
        .map(res => res.json())
        .toPromise()
        .then(() => {
          console.log('[PushService] registered!');

          // success, close the callback
          this.registered = true;
          clearInterval(id);
        })
        .catch((err) => {
          console.log('[PushService] post error: ' + JSON.stringify(err));
        });
      }
    });

    // we need to be authentificated to register,
    // we run a callback in case of not
    id = setInterval(callback, 10000); // 10s
  }

}