import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';

import { RadyGathering } from '../models/gathering';

/**
 * GatheringService
 * Manager for meetings
 * Patrick Champion - 05.01.2017
 */
@Injectable()
export class GatheringService {

  public gathering: RadyGathering;

  constructor(public http: Http) {
    this.gathering = null;
  }

  set(gathering: RadyGathering) {
    this.gathering = gathering;
  }

}
