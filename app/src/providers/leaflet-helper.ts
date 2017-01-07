import { Injectable } from '@angular/core';
import L from 'leaflet';

import { GeolocationService } from './geolocation-service';

/**
 * LeafletHelper
 * Patrick Champion - 07.01.2017
 */
@Injectable()
export class LeafletHelper {

  // Leaflet config
  public LEAFLET_URL: string = 'https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?access_token={accessToken}'; 
  public LEAFLET_TOKEN: string = 'pk.eyJ1IjoiY2hsYWJsYWsiLCJhIjoiY2l4a2hycG5uMDAxMTJxcDY1M2x2N2s3NiJ9.7cr1RyAverGU3AIeEIUGHA';

  constructor(
    public geolocationService: GeolocationService
  ) {}

  L() {
    return L;
  }

  addGeolocationTo(m: L.Map) {

    // geolocation callback
    let callback = {
      first: true,
      circle: null,
      func: (position, eachid, lmap) => {
        if(lmap) {
          let latLng = this.L().latLng(position.coords.latitude, position.coords.longitude);
          if(callback.first) {
            lmap.setView(latLng, 16);
            callback.first = false;
          }
          if(callback.circle != null)
            lmap.removeLayer(callback.circle);
          callback.circle = this.L().circle(latLng, { radius: position.coords.accuracy/2 }).addTo(lmap);
        }
        else // remove callback when map is deleted
          this.geolocationService.each = this.geolocationService.each.splice(eachid, 1);
      }
    };

    // focus if there is a position
    if(this.geolocationService.position.timestamp > 0) 
      callback.func(this.geolocationService.position, -1, m);
    
    // register callback
    let id = this.geolocationService.each.length;
    this.geolocationService.each.push((position) => {
      callback.func(position, id, m);
    });  
  }

  tileLayer(): L.TileLayer {
    return this.L().tileLayer(this.LEAFLET_URL, { maxZoom: 18, accessToken: this.LEAFLET_TOKEN });
  }

  marker(pos: L.LatLng): L.Marker {
    return this.L().marker(pos);
  }
}
