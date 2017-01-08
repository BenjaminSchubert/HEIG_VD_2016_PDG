import { Injectable, NgZone } from '@angular/core';
import { Geolocation, Geoposition, BackgroundGeolocation, SecureStorage } from 'ionic-native';
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
  public storage: SecureStorage;

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
    this.storage = null;
  }

  initialize() {
    console.log('[GeolocationService] initialisation');

    // setup a storage for the service
    this.storage = new SecureStorage();
    this.storage.create('geolocation-service-store').then(
      () => console.log('[GeolocationService] storage ready'),
      err => console.log('[GeolocationService] storage error (' + JSON.stringify(err) + ')')
    );

    // get back old position, if any
    this.storage.get('position').then((position) => {
      this.position = JSON.parse(position);
    }).catch((err) => {
      // nothing
    });

    // try to update position
    this.tryNow();
  }

  tryNow(timeout: number = 60000) {
    let options = { enableHighAccuracy: true, timeout: timeout };
    Geolocation.getCurrentPosition(options).then((position) => {
      this.execute(position);
    }).catch((err) => {
      console.log('[GeolocationService] tryNow timeout exceeded (' + timeout + ' ms)');
    });
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
        this.execute(location);
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
      .subscribe((position) => {
        this.zone.run(() => {
          this.execute(position);
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

  private execute(position) {

    position = this.convert(position);

    // save position
    this.position = position;
    if(this.position.timestamp == 0)
      this.position.timestamp = Date.now();
    this.storage.set('position', JSON.stringify(this.position)).catch((err) => {
      // nothing
    });

    // execute callbacks
    for(let f of this.once)
      f(this.position);
    for(let f of this.each)
      f(this.position);
    this.once = [];
  }

  // Thanks: http://stackoverflow.com/questions/32882035/cordova-geolocation-plugin-returning-empty-position-object-on-android#32883156
  private convert(position) {
    let positionObject = {};
    if ('coords' in position) {
      positionObject['coords'] = {};
      if ('latitude' in position.coords) 
        positionObject['coords']['latitude'] = position.coords.latitude;
      if ('longitude' in position.coords) 
        positionObject['coords']['longitude'] = position.coords.longitude;
      if ('accuracy' in position.coords) 
        positionObject['coords']['accuracy'] = position.coords.accuracy;
      if ('altitude' in position.coords) 
        positionObject['coords']['altitude'] = position.coords.altitude;
      if ('altitudeAccuracy' in position.coords) 
        positionObject['coords']['altitudeAccuracy'] = position.coords.altitudeAccuracy;
      if ('heading' in position.coords) 
        positionObject['coords']['heading'] = position.coords.heading;
      if ('speed' in position.coords) 
        positionObject['coords']['speed'] = position.coords.speed;
    }
    else 
      return this.position;
    if ('timestamp' in position) 
      positionObject['timestamp'] = position.timestamp;
    return positionObject;
  }
}
