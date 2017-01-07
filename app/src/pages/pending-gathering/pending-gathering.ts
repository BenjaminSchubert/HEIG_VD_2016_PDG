import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

import { GatheringService } from '../../providers/gathering-service';

/**
 * PendingGathering
 * Patrick Champion - 07.01.2017
 */
@Component({
  templateUrl: 'pending-gathering.html'
})
export class PendingGathering {

  constructor(
    public navCtrl: NavController,
    public gatheringService: GatheringService
  ) {}

  // TEST
  diag(v) {
    return JSON.stringify(v);
  }

  ionViewDidLoad() {
  }

}
