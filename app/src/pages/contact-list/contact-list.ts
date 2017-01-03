import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { AddContact } from '../add-contact/add-contact';

import { RadyFriend } from '../../models/friend';
import { ContactsService } from '../../providers/contacts-service';

@Component({
  templateUrl: 'contact-list.html'
})
export class ContactList {

  // list shown in the page
  items: RadyFriend[];

  constructor(public navCtrl: NavController,
              public app: App,
              public contactsService: ContactsService) {
    // nothing
  }

  ionViewDidLoad() {
    
    // fetch and init
    this.contactsService.fetch().then(() => this.initializeItems())
      .catch((err) => console.log('[ContactList] fetching error: ' + JSON.stringify(err)));
  }

  // TEST
  diag(item) {
    return JSON.stringify(item);
  }

  friendRequestReceived() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_accepted == false && item.initiator == false;
      });
    }
    return [];
  }

  friends() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_accepted == true && item.is_blocked == false;
      });
    }
    return [];
  }

  friendRequestSent() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_accepted == false && item.initiator == true;
      });
    }
    return [];
  }
  
  blockedFriends() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_blocked == true;
      });
    }
    return [];
  }

  /**
   * Initialize the shown list
   */
  initializeItems() {
    
    // copy the original list
    this.items = Object.assign([], this.contactsService.contacts);
  }

  /**
   * Searchbar event implementation
   */
  getItems(ev: any) {
    // Reset items back to all of the items
    this.initializeItems();

    // set val to the value of the searchbar
    let val = ev.target.value;

    // if the value is an empty string don't filter the items
    if (val && val.trim() != '') {
      this.items = this.items.filter((item) => {
        return (item.friend.username.toLowerCase().indexOf(val.toLowerCase()) > -1);
      })
    }
  }

  // nav to AddContact
  goToAddContact() {
    // getRootNav() needed to get out of the Tabs
    this.app.getRootNav().push(AddContact);
  }

  // nav to ...
  goToWaitingForParticipant() {

  }

  /**
   * Check if one or more checkbox is/are checked
   */
  isSomeChecked() {
    if(this.items != null) {
      for(let i of this.items) {
        if(i.checked)
          return true;
      }
    }
    return false;
  }
}
