import { Injectable, NgZone } from '@angular/core';
import { Geolocation, Geoposition, BackgroundGeolocation } from 'ionic-native';
import 'rxjs/add/operator/filter';

/**
 * GeolocationService
 * Patrick Champion - 06.01.2017
 * Thanks: http://www.joshmorony.com/adding-background-geolocation-to-an-ionic-2-application/
 */
@Injectable()
export class GeolocationService {

  public watch: any;
  public position: Geoposition;
  public once: any[];
  public each: any[];

  constructor(public zone: NgZone) {
    this.watch = null;
    this.position = {
      coords: {
        latitude: 0,
        longitude: 0,
        accuracy: 0,
        altitude: 0,
        altitudeAccuracy: 0,
        heading: 0,
        speed: 0
      },
      timestamp: 0
    };
    this.once = [];
    this.each = [];
  }

  on() {
    if(this.watch == null) {
      console.log('[GeolocationService] turning on');

    // Background Tracking
    let config = {
      desiredAccuracy: 0,
      stationaryRadius: 20,
      distanceFilter: 10, 
      debug: true,
      interval: 2000 
    };
    BackgroundGeolocation.configure((location) => {
      this.zone.run(() => {
        this.position.coords = location;
        this.execute();
      });
    }, (err) => {
      console.log('[GeolocationService] configure error: ' + err);
    }, config);
    BackgroundGeolocation.start();

    // Foreground Tracking
    let options = {
      frequency: 3000, 
      enableHighAccuracy: true
    };
    this.watch = Geolocation.watchPosition(options)
      .filter((p: any) => p.code === undefined)
      .subscribe((position: Geoposition) => {
        this.zone.run(() => {
          this.position = position;
          this.execute();
        });
      });
    }
  }

  off() {
    if(this.watch != null) {
      console.log('[GeolocationService] turning off');
      BackgroundGeolocation.finish();
      this.watch.unsubscribe();
      this.watch = null;
    }
  }

  private execute() {
    console.log('[GeolocationService] position: ' + JSON.stringify(this.position));
    for(let f of this.once)
      f(this.position);
    for(let f of this.each)
      f(this.position);
    this.once = [];
  }
}
