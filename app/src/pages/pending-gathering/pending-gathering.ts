import { Component, Inject, ElementRef } from '@angular/core';
import { NavController, AlertController, LoadingController, App } from 'ionic-angular';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { NotificationService } from '../../providers/notification-service';
import { LeafletHelper } from '../../providers/leaflet-helper';

import { MainTabs } from '../main-tabs/main-tabs';
import { RunningGathering } from '../running-gathering/running-gathering';

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
    public app: App,
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
    try {
      return JSON.stringify(v);
    } catch(e) {
      return v;
    }
  }

  ionViewDidLoad() {

    // create gathering
    if(this.gatheringService.initiator) {
      let loading = this.loadingCtrl.create({ content: 'Please wait...' });
      loading.present();
      this.gatheringService.create().then(() => {
        loading.dismiss();
        this.gatheringService.status = 'pending';
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
      this.gatheringService.meetings.place.latitude,
      this.gatheringService.meetings.place.longitude
    );
    this.leafletHelper.marker(destination).addTo(this.map);

    // fit bounds
    let position = this.leafletHelper.L().latLng(
      this.geolocationService.position.coords.latitude,
      this.geolocationService.position.coords.longitude
    );
    let bounds = this.leafletHelper.L().latLngBounds(position, destination);
    this.map.fitBounds(bounds, { padding: [10, 10] });
  }

  cancel(askConfirmation = true) {

    if(askConfirmation) {
      this.alertCtrl.create({
        title: 'Cancel gathering',
        message: 'Are you sure?',
        buttons: [
          { text: 'No' },
          { text: 'Yes', handler: () => {
            this.app.getRootNav().setRoot(MainTabs).then();
            this.gatheringService.reset(true, 'canceled');
          }}
        ]
      }).present();
    }
    else {
      this.app.getRootNav().setRoot(MainTabs).then();
      this.gatheringService.reset(true, 'canceled');
    }
  }

  accept() {
    this.gatheringService.accept().then(() => {
      this.gatheringService.status = 'pending';
    });
  }

  decline() {
    let alert = this.alertCtrl.create({
      title: 'Decline gathering',
      message: 'Are you sure?',
      buttons: [
        { text: 'No' },
        { text: 'Yes', handler: () => {
          this.app.getRootNav().setRoot(MainTabs);
          this.gatheringService.reset();
        }}
      ]
    });
    alert.present();
  }

  continueAnyway() {
    this.navCtrl.setRoot(RunningGathering).then();

    // TODO check if it's ok, for exemple in 'person' type, the person must have accepted
  }
}
