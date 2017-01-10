import { Component, Inject, ElementRef } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { NotificationService } from '../../providers/notification-service';
import { CompassService } from '../../providers/compass-service';
import { LeafletHelper } from '../../providers/leaflet-helper';

import { MainTabs } from '../main-tabs/main-tabs';

/**
 * RunningGathering
 * Patrick Champion - 09.01.2017
 */
@Component({
  templateUrl: 'running-gathering.html'
})
export class RunningGathering {

  public map: any;
  public elementRef: ElementRef;
  public mapid: any;
  public destination: any;
  public line: any;
  public head: any;
  public autocenter: boolean;
  public setautocenter: boolean;
  public checkProximityAlertDone: boolean;

  constructor(
    public navCtrl: NavController,
    public alertCtrl: AlertController,
    public gatheringService: GatheringService,
    public geolocationService: GeolocationService,
    public notificationService: NotificationService,
    public compassService: CompassService,
    public leafletHelper: LeafletHelper,
    @Inject(ElementRef) elementRef: ElementRef
  ) {
    this.map = null;
    this.elementRef = elementRef;
    this.mapid = null;
    this.destination = null;
    this.line = null;
    this.head = null;
    this.autocenter = true;
    this.setautocenter = false;
    this.checkProximityAlertDone = false;
  }

  // TEST
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewDidLoad() {

    // start gathering
    this.gatheringService.start();

    // find our position
    this.geolocationService.on();
    this.compassService.on();

    // load map
    this.mapid = this.elementRef.nativeElement.querySelector('#mapid');
    this.map = this.leafletHelper.L().map(this.mapid, { center: [0, 0], zoom: 1 });
    this.leafletHelper.tileLayer().addTo(this.map);
    this.leafletHelper.addGeolocationTo(this.map);

    // add destination to map
    this.destination = this.leafletHelper.L().latLng(
      this.gatheringService.meetings.place.latitude,
      this.gatheringService.meetings.place.longitude
    );
    this.leafletHelper.marker(this.destination).addTo(this.map);

    // remove autocenter when moved
    this.map.on('moveend', (data) => {
      if(!this.setautocenter)
          this.autocenter = false;
      else
          this.setautocenter = false;
    });

    // update direction 
    this.geolocationService.each.push((position) => {

      let pos = this.leafletHelper.L().latLng(position.coords.latitude, position.coords.longitude);

      // line between position and destination
      if(this.line != null)
        this.map.removeLayer(this.line);
      this.line = this.leafletHelper.L().polyline([pos, this.destination], { color: 'red' }).addTo(this.map);

      // center on user
      if(this.autocenter) 
          this.setAutoCenter();

      // check proximity
      this.checkProximity(position);
    });

    // update heading
    this.compassService.each.push((heading) => {

      let pos = this.leafletHelper.L().latLng(
          this.geolocationService.position.coords.latitude, 
          this.geolocationService.position.coords.longitude);

      // heading of user
      if(heading.trueHeading != null) {
        if(this.head != null)
          this.map.removeLayer(this.head);
        this.head = this.leafletHelper.arrow(pos, heading.trueHeading).addTo(this.map);
      }
    });
  }

  setAutoCenter() {
    this.setautocenter = true;
    let pos = this.leafletHelper.L().latLng(
      this.geolocationService.position.coords.latitude, 
      this.geolocationService.position.coords.longitude);
    this.map.flyTo(pos);
    this.autocenter = true;
  }

  arrived() {      
    this.alertCtrl.create({
      title: 'Arrived',
      message: 'Are you sure?',
      buttons: [
        { text: 'No' },
        { text: 'Yes', handler: () => {
          this.gatheringService.arrived();
        }}
      ]
    }).present();
  }

  leave() {
    if(this.gatheringService.initiator)
      this.cancel();
    else {
      this.alertCtrl.create({
        title: 'Leave gathering',
        message: 'Are you sure?',
        buttons: [
          { text: 'No' },
          { text: 'Yes', handler: () => {
            this.gatheringService.decline().then(() => {
              this.gatheringService.reset(false);
              this.navCtrl.setRoot(MainTabs);
            });
          }}
        ]
      }).present();
    }
  }

  cancel() {
    this.alertCtrl.create({
      title: 'Cancel gathering',
      message: 'Are you sure?',
      buttons: [
        { text: 'No' },
        { text: 'Yes', handler: () => {
          this.gatheringService.stop('canceled').then(() => {
            this.gatheringService.reset(false);
            this.navCtrl.setRoot(MainTabs);
          });
        }}
      ]
    }).present();
  }

  checkProximity(position) {
    if(!this.checkProximityAlertDone &&this.gatheringService.distance != null) {
      if(this.gatheringService.distance <= 10) {
        this.notificationService.notify({
          title: 'Almost there!',
          message: 'You are at less than ' + this.gatheringService.distance + 'm of the destination,\ndon\'t forget to tell others by using the green checkmark',
        });
        this.checkProximityAlertDone = true;
      }
    }
  } 

}
