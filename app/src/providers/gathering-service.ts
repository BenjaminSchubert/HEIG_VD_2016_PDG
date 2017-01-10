import { Injectable } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';
import 'rxjs/add/operator/map';

import { RadyMeetings } from '../models/meetings';

import { GeolocationService } from './geolocation-service';
import { AuthService } from './auth-service';
import { NotificationService } from './notification-service';
import { MeService } from './me-service';
import { LeafletHelper } from './leaflet-helper';
import { CONFIG } from './config';

import { RunningGathering } from '../pages/running-gathering/running-gathering';
import { PendingGathering } from '../pages/pending-gathering/pending-gathering';
import { MainTabs } from '../pages/main-tabs/main-tabs';

/**
 * GatheringService
 * Manager for meetings
 * Patrick Champion - 05.01.2017
 */
@Injectable()
export class GatheringService {

  public status: string;
  public distance: number;
  public meetings: RadyMeetings;
  public initiator: boolean;

  constructor(
    public authService: AuthService,
    public geolocationService: GeolocationService,
    public leafletHelper: LeafletHelper,
    public notificationService: NotificationService,
    public meService: MeService
  ) {
    this.reset();

    // update distance
    this.geolocationService.each.push((position) => {
      this.updateDistanceTo(position);
    });
  }

  create() {

    // create payload
    let payload: any = Object.assign({}, this.meetings);
    delete payload.organiser;
    payload.participants = this.meetings.participants.map((p) => {
      return p.user.id;
    });

    // request
    return this.authService.post(
      CONFIG.API_URL + 'meetings/',
      payload,
    ).map(res => res.json()).toPromise().then((data) => {

      // TEST
      console.log('[GatheringService] creation succeed: ' + JSON.stringify(data));

      // update gathering
      this.meetings = data;
    }).catch((err) => {
      console.log('[GatheringService] create error: ' + JSON.stringify(err));
    });
  }

  start() {
    // nothing atm
  }

  stop(status = 'ended') {
    return this.authService.patch(
      CONFIG.API_URL + 'meetings/' + this.meetings.id + '/',
      { status: status },
      ).map(res => res.json()).toPromise().then(() => {
        this.meetings.status = status;
      }).catch((err) => {
        console.log('[GatheringService] stop error: ' + JSON.stringify(err));
      });
  }

  accept() {
    return this.authService.patch(
      CONFIG.API_URL + 'meetings/' + this.meetings.id + '/participants/',
      { accepted: true },
      ).map(res => res.json()).toPromise().then(() => {
        this.meetings.participants.find((p) => {
          return p.user.id == this.meService.me.id;
        }).accepted = true;
      }).catch((err) => {
        console.log('[GatheringService] accept error: ' + JSON.stringify(err));
      });
  }

  decline() {
    return this.authService.patch(
      CONFIG.API_URL + 'meetings/' + this.meetings.id + '/participants/',
      { accepted: false },
      ).map(res => res.json()).toPromise().then(() => {
        this.meetings.participants.find((p) => {
          return p.user.id == this.meService.me.id;
        }).accepted = false;
      }).catch((err) => {
        console.log('[GatheringService] decline error: ' + JSON.stringify(err));
      });
  }

  arrived() {
    return this.authService.patch(
      CONFIG.API_URL + 'meetings/' + this.meetings.id + '/participants/',
      { arrived: true },
      ).map(res => res.json()).toPromise().then(() => {
        this.meetings.participants.find((p) => {
          return p.user.id == this.meService.me.id;
        }).arrived = true;
      }).catch((err) => {
        console.log('[GatheringService] arrived error: ' + JSON.stringify(err));
      });
  }

  fetch(id) {
    return this.authService.get(CONFIG.API_URL + 'meetings/' + id + '/')
      .map(res => res.json())
      .toPromise()
      .then((data) => {
        this.meetings = data;
      }).catch((err) => {
        console.log('[GatheringService] fetch error: ' + JSON.stringify(err));
      });
  }

  reset(doStop = true) {
    if(doStop && this.status == 'running') {
      if(this.initiator)
        this.stop();
      else
        this.decline();
    }
    this.status = null;
    this.meetings = null;
    this.distance = null;
    this.initiator = null;
  }

  updateDistanceTo(position) {
    if(this.meetings != null && typeof this.meetings.place != 'undefined') {
      this.distance = Math.round(this.leafletHelper.L().latLng(
        position.coords.latitude,
        position.coords.longitude
      ).distanceTo(this.leafletHelper.L().latLng(
        this.meetings.place.latitude,
        this.meetings.place.longitude
      )));
    }
    else
      this.distance = null;
  }

  configureNotificationHandlers(
      navCtrl: NavController, alertCtrl: AlertController, pendingGathering: typeof PendingGathering,
      runningGathering: typeof RunningGathering, mainTabs: typeof MainTabs,
  ) {

    // add handlers for push notifications
    // -----------------------------------

    // new meetings
    this.notificationService.addHandler('new-meeting', (n) => {
      alertCtrl.create({
        title: 'New gathering request',
        message: 'Accept?',
        buttons: [
          { text: 'Decline', handler: () => {
            this.authService.patch(
              CONFIG.API_URL + 'meetings/participants/' + n.additionalData.meeting + '/',
              { accepted: false },
              );
          }},
          { text: 'See info', handler: () => {
            this.reset();
            this.fetch(n.additionalData.meeting).then(() => {
              this.status = 'request';
              navCtrl.setRoot(pendingGathering);
            });
          }}
        ],
        enableBackdropDismiss: false
      }).present();
    });

    // user accepted meetings
    this.notificationService.addHandler('user-accepted-meeting', (n) => {
      this.meetings.participants.find((p) => {
        return p.user.id == n.additionalData.participant;
      }).accepted = true;
    });

    // user refused meetings
    this.notificationService.addHandler('user-refused-meeting', (n) => {
      this.meetings.participants.find((p) => {
        return p.user.id == n.additionalData.participant;
      }).accepted = false;
    });

    // user canceled meetings (running)
    this.notificationService.addHandler('user-canceled-meeting', (n) => {
      this.meetings.participants.find((p) => {
        return p.user.id == n.additionalData.participant;
      }).accepted = false;
    });

    // user arrived to meetings
    this.notificationService.addHandler('user-arrived-to-meeting', (n) => {
      this.meetings.participants.find((p) => {
        return p.user.id == n.additionalData.participant;
      }).arrived = true;
    });

    // meetings in progress
    this.notificationService.addHandler('meeting-in-progress', (n) => {
      this.meetings.status = 'progress';
      if(this.status == 'pending') {
        this.status = 'running';
        navCtrl.setRoot(runningGathering);
      }
    });

    // finished meetings
    this.notificationService.addHandler('finished-meeting', (n) => {
      this.meetings.status = 'finished';
      this.reset();
    });

    // canceled meetings
    this.notificationService.addHandler('canceled-meeting', (n) => {
      alertCtrl.create({
        title: 'Gathering canceled',
        buttons: [
          { text: 'OK', handler: () => {
            this.reset();
            navCtrl.setRoot(mainTabs);
          }}
        ],
        enableBackdropDismiss: false
      }).present();
    });

    // TODO other?
  }
}
