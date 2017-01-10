import { Component } from '@angular/core';
import { AlertController, App } from 'ionic-angular';

import { RadyMeetings } from '../../models/meetings';

import { PendingGathering } from '../pending-gathering/pending-gathering';

import { GatheringService } from '../../providers/gathering-service';
import { AuthService } from '../../providers/auth-service';
import { CONFIG } from '../../providers/config';

/** 
 * History
 * History of meetings
 */
@Component({
  templateUrl: 'history.html'
})
export class History {

  public list : RadyMeetings[];

  constructor(
    public app: App,
    public alertCtrl: AlertController,
    public authService: AuthService,
    public gatheringService: GatheringService
  ) {
    this.list = null;  
  }

  ionViewDidLoad() {
    this.fetch();
  }

  startGathering(meetings: RadyMeetings) {
    this.alertCtrl.create({
      title: 'Start gathering',
      message: 'Are you sure?',
      buttons: [
        { text: 'Cancel' },
        { text: 'Accept', handler: () => {
          this.gatheringService.initiator = true;
          this.gatheringService.status = 'pending';
          this.gatheringService.meetings = meetings;
          this.app.getRootNav().setRoot(PendingGathering);
        }}
      ]
    }).present();
  }

  fetch() {
    this.authService.get(CONFIG.API_URL + 'meetings/')
      .map(res => res.json())
      .map((res) => {
        return res.sort((a, b) => {
          return b.id - a.id;
        }).slice(0, 10);
      })
      .toPromise()
      .then((data) => {
        this.list = data;
      })
      .catch((err) => {
        console.log('[History] fetch error: ' + JSON.stringify(err));
      });
  }
}
