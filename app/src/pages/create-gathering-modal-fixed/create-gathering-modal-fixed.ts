import { Component, ElementRef, Inject } from '@angular/core';
import { ViewController } from 'ionic-angular';

import { GatheringService } from '../../providers/gathering-service';
import { GeolocationService } from '../../providers/geolocation-service';
import { LeafletHelper } from '../../providers/leaflet-helper';

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
    public geolocationService: GeolocationService,
    public leafletHelper: LeafletHelper
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

    // try to find our position
    this.geolocationService.on();

    // load map
    this.mapid = this.elementRef.nativeElement.querySelector('#mapid');
    this.map = this.leafletHelper.L().map(this.mapid, { center: [0, 0], zoom: 1 });
    this.leafletHelper.tileLayer().addTo(this.map);
    this.leafletHelper.addGeolocationTo(this.map);

    // add click event to choose place
    this.map.on('click', (e) => {
      if(this.point == null) {
        this.marker = this.leafletHelper.marker(e.latlng);
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
    this.map = null;
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
