import { Injectable, NgZone } from '@angular/core';
import { DeviceOrientation, CompassHeading } from 'ionic-native';

/**
 * CompassService
 */
@Injectable()
export class CompassService {
  public watch: any;
  public heading: CompassHeading;
  public once: any[];
  public each: any[];

  constructor(public zone: NgZone) {
    this.watch = null;
    this.heading = {
      magneticHeading: 0,
      trueHeading: 0,
      headingAccuracy: 0,
      timestamp: 0
    };
    this.once = [];
    this.each = [];
  }

  on() {
    if(this.watch == null) {
      console.log('[CompassService] turning on');

      // Foreground Tracking
      this.watch = DeviceOrientation.watchHeading()
        .subscribe((heading) => {
          this.zone.run(() => {
            this.execute(heading);
          });
        });
    }
  }

  off() {
    if(this.watch != null) {
      console.log('[CompassService] turning off');
      this.watch.unsubscribe();
      this.watch = null;
    }
  }

  private execute(heading) {

    heading = this.convert(heading);
    this.heading = heading;

    // execute callbacks
    for(let f of this.once)
      f(this.heading);
    for(let f of this.each)
      f(this.heading);
    this.once = [];
  }

  private convert(heading) {
    let headingObject = {};
    if ('magneticHeading' in heading) 
      headingObject['magneticHeading'] = heading.magneticHeading;
    if ('trueHeading' in heading) 
      headingObject['trueHeading'] = heading.trueHeading;
    if ('headingAccuracy' in heading) 
      headingObject['headingAccuracy'] = heading.headingAccuracy;
    if ('timestamp' in heading) 
      headingObject['timestamp'] = heading.timestamp;
    return headingObject;
  }
}