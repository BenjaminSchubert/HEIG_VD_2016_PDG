import { Component, ElementRef, Inject } from '@angular/core';
import { ViewController } from 'ionic-angular';

import L from 'leaflet';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { CONFIG } from '../../providers/config';

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
  public point: any;
  public marker: any;

  constructor(
    public viewCtrl: ViewController,
    public gatheringService: GatheringService,
    @Inject(ElementRef) elementRef: ElementRef,
    public geolocationService: GeolocationService
  ) {
    this.map = null;
    this.elementRef = elementRef;
    this.mapid = null;
    this.point = null;
    this.marker = null;
  }

  // TEST 
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewDidLoad() {

    // load map
    this.mapid = this.elementRef.nativeElement.querySelector('#mapid');
    this.map = L.map(this.mapid)
      .setView(L.latLng(
          this.geolocationService.position.coords.latitude, 
          this.geolocationService.position.coords.longitude),
        1);
    L.tileLayer(CONFIG.LEAFLET_URL, { maxZoom: 18, accessToken: CONFIG.LEAFLET_TOKEN }).addTo(this.map);

    // try to find our position
    this.geolocationService.on();
    this.geolocationService.once.push((position) => {
      let latLng = L.latLng(position.coords.latitude, position.coords.longitude);
      this.map.setView(latLng, 16);
      L.marker(latLng).addTo(this.map);
      L.circle(latLng, { radius: position.coords.accuracy/2 }).addTo(this.map);
    });   

    // add click event to choose place
    this.map.on('click', (e) => {
      if(this.point == null) {
        this.marker = L.marker(e.latlng);
        this.marker.addTo(this.map);
        this.marker.bindPopup('Selected place').openPopup();
        this.point = e.latlng;
      }
      else {
        this.map.removeLayer(this.marker);
        this.marker = null;
        this.point = null;
      }
    });
  }

  dismiss() {
    this.geolocationService.off();
    this.viewCtrl.dismiss();
  }

  confirm() {
    this.gatheringService.gathering.mode = 'fixed';
    this.gatheringService.gathering.fixed = {
      destination: {
        latitude: this.point.lat,
        longitude: this.point.lng,
      }
    };
    this.dismiss();
  }
}
