import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Settings } from '../settings/settings'
import { ContactList } from '../contact-list/contact-list'
import { History } from '../history/history'
import { EditProfile } from '../edit-profile/edit-profile'

@Component({
  templateUrl: 'main-tabs.html'
})
export class MainTabs {

  tab1Root: any = Settings;
  tab2Root: any = ContactList;
  tab3Root: any = History;
  tab4Root: any = EditProfile;

  constructor(public navCtrl: NavController) {

  }

}
