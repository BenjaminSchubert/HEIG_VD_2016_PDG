import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';

import { RadyGathering } from '../models/gathering';

import { GeolocationService } from './geolocation-service';
import { AuthService } from './auth-service';
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
  public initiator: boolean;
  public gathering: RadyGathering;

  constructor(
    public authService: AuthService,
    public geolocationService: GeolocationService,
    public leafletHelper: LeafletHelper
  ) {
    this.status = null;
    this.distance = null;
    this.initiator = null;
    this.gathering = null;
  }

  set(gathering: RadyGathering, status = 'create') {
    this.status = status;
    this.initiator = status == 'create';
    this.gathering = gathering;
  }

  create() {

    // create payload
    let payload = null;
    if(this.gathering.mode == 'fixed') {
      payload = {
        type: 'place',
        place: {
          latitude: this.gathering.destination.latitude,
          longitude: this.gathering.destination.longitude  
        },
        participants: this.gathering.participants.map((p) => p.id)
      };
    }
    console.log('[GatheringService] creation payload: ' + JSON.stringify(payload));

    // request
    return this.authService.http().post(
      CONFIG.API_URL + 'meetings/',
      payload,
      this.authService.createOptions([
        { name: 'Content-Type', value: 'application/json' }
      ])
    ).map(res => res.json()).toPromise().then((data) => {

      // update gathering
      console.log('[GatheringService] creation succeed: ' + JSON.stringify(data));
      // TODO

      this.status = 'pending';
    });
  }

  start() {

  }

  stop() {

  }

  computeDistance() {
    this.distance = this.leafletHelper.L().latLng(
      this.geolocationService.position.coords.latitude,
      this.geolocationService.position.coords.longitude
    ).distanceTo(this.leafletHelper.L().latLng(
      this.gathering.destination.latitude,
      this.gathering.destination.longitude
    ));
  }
}
