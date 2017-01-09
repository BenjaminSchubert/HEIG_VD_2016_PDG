import { Component } from '@angular/core';
import { ModalController, NavController } from 'ionic-angular';

import { PendingGathering } from '../pending-gathering/pending-gathering';
import { CreateGatheringModalFixed } from '../create-gathering-modal-fixed/create-gathering-modal-fixed';

import { GatheringService } from '../../providers/gathering-service';

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
    this.gatheringService.meetings.type = null;
    switch (mode) {
      case 'place': this.fixedMode(); break;
      case 'person': this.somebodyMode(); break;
      case 'shortest': this.shortestMode(); break;
      default: console.log('[CreateGathering] unknown mode'); break;
    }
  }

  private fixedMode() {
    let modal = this.modalCtrl.create(CreateGatheringModalFixed);
    modal.onDidDismiss(() => this.goToPending());
    modal.present();
  }

  private somebodyMode() {

  }

  private shortestMode() {

  }

  private goToPending() {
    if(this.gatheringService.meetings.type != null)
      this.navCtrl.setRoot(PendingGathering);
  }
}
