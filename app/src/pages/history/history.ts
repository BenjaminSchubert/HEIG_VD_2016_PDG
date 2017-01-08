import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

import { RadyHistory } from '../../models/history';
import { RadyUser } from '../../models/user';
import { RadyLocation } from '../../models/location';

@Component({
  selector: 'page-history',
  templateUrl: 'history.html'
})
export class History {

  historyList : RadyHistory[];

  // Load the historyList for the current user
  initializeItems() {
    this.historyList = [
      new RadyHistory(
        [
          new RadyUser('Sauron'),
          new RadyUser('Frodon'),
          new RadyUser('Gandalf')
        ]
        , new RadyLocation(12,29)
        , "20/02/1992"
      ),
      new RadyHistory(
        [
          new RadyUser('Pipin'),
          new RadyUser('Merry'),
          new RadyUser('Frodon')
        ]
        , new RadyLocation(10.23,82.83)
        , "31/01/1999"
      ),
      new RadyHistory(
        [
          new RadyUser('Gandalf'),
          new RadyUser('Sauron')
        ]
        , new RadyLocation(123,29.13)
        , "10/06/2016"
      )
    ]
  }

  constructor(public navCtrl: NavController) {
    // Load history
    this.initializeItems();

  }


  ionViewDidLoad() {
  }

  goToGathering(history : RadyHistory){
    
  }

}
