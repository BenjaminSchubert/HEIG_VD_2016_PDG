import { Component, Inject, ElementRef } from '@angular/core';
import { NavController, AlertController, LoadingController } from 'ionic-angular';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { NotificationService } from '../../providers/notification-service';
import { LeafletHelper } from '../../providers/leaflet-helper';

import { MainTabs } from '../main-tabs/main-tabs';

/**
 * PendingGathering
 * Patrick Champion - 07.01.2017
 */
@Component({
  templateUrl: 'pending-gathering.html'
})
export class PendingGathering {

  public map: any;
  public elementRef: ElementRef;
  public mapid: any;

  constructor(
    public navCtrl: NavController,
    public alertCtrl: AlertController,
    public loadingCtrl: LoadingController,
    public gatheringService: GatheringService,
    public geolocationService: GeolocationService,
    public notificationService: NotificationService,
    public leafletHelper: LeafletHelper,
    @Inject(ElementRef) elementRef: ElementRef
  ) {
    this.map = null;
    this.elementRef = elementRef;
    this.mapid = null;
  }

  // TEST
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewWillLoad() {

    // add status to users
    for(let user of this.gatheringService.gathering.participants)
      user.status = 'waiting';
  }

  ionViewDidLoad() {

    // start gathering
    if(this.gatheringService.initiator) {
      let loading = this.loadingCtrl.create({ content: 'Please wait...' });
      loading.present();
      this.gatheringService.create().then(() => {
        loading.dismiss();
      }).catch((err) => {
        loading.dismiss();
        console.log('[PendingGathering] start error: ' + JSON.stringify(err));
        this.notificationService.notify({
          title: 'Gathering error',
          message: 'Can not create the meetings at the moment'
        });
        this.cancel(false);
      });
    }

    // try to find our position
    this.geolocationService.on();

    // load map
    this.mapid = this.elementRef.nativeElement.querySelector('#mapid');
    this.map = this.leafletHelper.L().map(this.mapid, { center: [0, 0], zoom: 1 });
    this.leafletHelper.tileLayer().addTo(this.map);
    this.leafletHelper.addGeolocationTo(this.map);

    // add destination to map
    let destination = this.leafletHelper.L().latLng(
      this.gatheringService.gathering.destination.latitude,
      this.gatheringService.gathering.destination.longitude
    );
    this.leafletHelper.marker(destination).addTo(this.map);

    // fit bounds
    let position = this.leafletHelper.L().latLng(
      this.geolocationService.position.coords.latitude,
      this.geolocationService.position.coords.longitude
    );
    let bounds = this.leafletHelper.L().latLngBounds(position, destination);
    this.map.fitBounds(bounds, { padding: [30, 30] });
  }

  cancel(askConfirmation = true) {

    function callback(gS, nC) {

      // TODO

      gS.off();
      nC.setRoot(MainTabs);
    }

    if(askConfirmation) {
      this.alertCtrl.create({
        title: 'Cancel gathering',
        message: 'Are you sure?',
        buttons: [
          { text: 'No' },
          { text: 'Yes', handler: () => {
            callback(this.geolocationService, this.navCtrl);
          }}
        ]
      }).present();
    }
    else
      callback(this.geolocationService, this.navCtrl);
  }

  accept() {

  }

  decline() {
    this.cancel();
  }

  continueAnyway() {

  }

  distance() {
    this.gatheringService.computeDistance();
    return Math.round(this.gatheringService.distance);
  }
}
