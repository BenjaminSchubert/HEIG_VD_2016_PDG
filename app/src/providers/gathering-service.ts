import { Injectable } from '@angular/core';
import { NavController } from 'ionic-angular';
import 'rxjs/add/operator/map';

import { RadyMeetings } from '../models/meetings';

import { GeolocationService } from './geolocation-service';
import { AuthService } from './auth-service';
import { NotificationService } from './notification-service';
import { LeafletHelper } from './leaflet-helper';
import { CONFIG } from './config';

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
    public notificationService: NotificationService
  ) {
    this.status = null;
    this.distance = null;
    this.meetings = null;
    this.initiator = null;

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
    return this.authService.http().post(
      CONFIG.API_URL + 'meetings/',
      payload,
      this.authService.createOptions([
        { name: 'Content-Type', value: 'application/json' }
      ])
    ).map(res => res.json()).toPromise().then((data) => {

      // TEST
      console.log('[GatheringService] creation succeed: ' + JSON.stringify(data));

      // update gathering
      this.meetings = data;
      this.status = 'pending';
    });
  }

  start() {

  }

  stop() {

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

  configureNotificationHandlers(navCtrl: NavController) {

    // add handlers for push notifications
    // -----------------------------------

    // new meetings
    this.notificationService.addHandler('new-meetings', (n) => {

    });

    // user accepted meetings
    this.notificationService.addHandler('user-accepted-meetings', (n) => {

    });

    // user refused meetings
    this.notificationService.addHandler('user-refused-meetings', (n) => {

    });

    // user arrived to meetings
    this.notificationService.addHandler('user-arrived-to-meetings', (n) => {

    });

    // meetings in progress
    this.notificationService.addHandler('meetings-in-progress', (n) => {

    });

    // finished meetings
    this.notificationService.addHandler('finished-meetings', (n) => {

    });

    // canceled meetings
    this.notificationService.addHandler('canceled-meetings', (n) => {

    });
  }
}
