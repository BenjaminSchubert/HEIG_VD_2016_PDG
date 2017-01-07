import { Component, ElementRef, Inject } from '@angular/core';
import { ModalController, ViewController, NavController } from 'ionic-angular';

import L from 'leaflet';

import { PendingGathering } from '../pending-gathering/pending-gathering';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { CONFIG } from '../../providers/config';

/**
 * CreateGathering
 * Settings page for meetings
 * Patrick Champion - 05.01.2017
 */
@Component({
  templateUrl: 'create-gathering.html'
})
export class CreateGathering {

  constructor(
    public navCtrl: NavController,
    public gatheringService: GatheringService,
    public modalCtrl: ModalController
  ) {}

  // TEST 
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewDidLoad() {
  }

  modeChoosen(modeRef) {
    let mode = JSON.parse(JSON.stringify(modeRef));
    this.gatheringService.gathering.mode = null;
    switch (mode) {
      case 'fixed': this.fixedMode(); break;
      case 'somebody': this.somebodyMode(); break;
      case 'shortest': this.shortestMode(); break;
      default: console.log('[CreateGathering] unknown mode'); break;
    }
    if(this.gatheringService.gathering.mode != null)
      this.navCtrl.push(PendingGathering);
  }

  private fixedMode() {
    this.modalCtrl.create(CreateGatheringModalFixed).present();
  }

  private somebodyMode() {

  }

  private shortestMode() {

  }
}

/**
 * CreateGatheringModalFixed
 * Modal for fixed mode
 */
@Component({
  templateUrl: 'create-gathering-modal-fixed.html'
})
export class CreateGatheringModalFixed {

  public map: any;
  public elementRef: ElementRef;
  public mapid: any;

  constructor(
    public viewCtrl: ViewController,
    public gatheringService: GatheringService,
    @Inject(ElementRef) elementRef: ElementRef,
    public geolocationService: GeolocationService
  ) {
    this.map = null;
    this.elementRef = elementRef;
    this.mapid = null;
  }

  // TEST 
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewDidLoad() {
    this.mapid = this.elementRef.nativeElement.querySelector('#mapid');
    this.map = L.map(this.mapid)
      .setView(L.latLng(
          this.geolocationService.position.coords.latitude, 
          this.geolocationService.position.coords.longitude),
        1);
    L.tileLayer(CONFIG.LEAFLET_URL, { maxZoom: 18, accessToken: CONFIG.LEAFLET_TOKEN }).addTo(this.map);
    this.geolocationService.on();
    this.geolocationService.once.push((position) => {
      let latLng = L.latLng(position.coords.latitude, position.coords.longitude);
      this.map.setView(latLng, 16);
      L.marker(latLng).addTo(this.map);
      L.circle(latLng, { radius: position.coords.accuracy/2 }).addTo(this.map);
    });   
  }

  dismiss() {
    this.geolocationService.off();
    this.viewCtrl.dismiss();
  }
}
