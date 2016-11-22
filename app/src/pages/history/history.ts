import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

import { RadyHistory } from '../../models/history';

@Component({
  selector: 'page-history',
  templateUrl: 'history.html'
})
export class History {



  initializeItems() {
    
  }

  constructor(public navCtrl: NavController) {



  }


  ionViewDidLoad() {
    console.log('Hello History Page');
  }

}
