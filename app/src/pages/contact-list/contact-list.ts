import { Component } from '@angular/core';
import { NavController, App, AlertController, ActionSheetController } from 'ionic-angular';

import { AddContact } from '../add-contact/add-contact';
import { CreateGathering } from '../create-gathering/create-gathering';

import { RadyFriend } from '../../models/friend';
import { ContactsService } from '../../providers/contacts-service';
import { AuthService } from '../../providers/auth-service';
import { GatheringService } from '../../providers/gathering-service';
import { MeService } from '../../providers/me-service';
import { CONFIG } from '../../providers/config';

@Component({
  templateUrl: 'contact-list.html'
})
export class ContactList {

  // list shown in the page
  items: RadyFriend[];

  constructor(public navCtrl: NavController,
              public app: App,
              public contactsService: ContactsService,
              public alertCtrl: AlertController,
              public actionSheetCtrl: ActionSheetController,
              public authService: AuthService,
              public gatheringService: GatheringService,
              public meService: MeService) {
    // nothing
  }

  ionViewDidLoad() {
    
    // fetch and init
    this.contactsService.fetch().then(() => this.initializeItems())
      .catch((err) => console.log('[ContactList] contacts fetching error: ' + JSON.stringify(err)));

    this.meService.fetch().catch((err) => console.log('[ContactList] me fetching error: ' + JSON.stringify(err)));
  }

  friendRequestReceived() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_accepted == false && item.initiator == false && item.is_hidden == false;
      });
    }
    return [];
  }

  popupRequestReceived(item) {
    this.alertCtrl.create({
      title: 'Accept ' + item.friend.username + ' ?',
      message: 'Click OK to accept the friend request',
      buttons: [
        { text: 'Cancel' },
        { text: 'Hide', handler: () => {

          // hide friend
          this.authService.http().patch(
            CONFIG.API_URL + 'users/friends/' + item.id + '/',
            { is_hidden: true },
            this.authService.createOptions([
              { name: 'Content-Type', value: 'application/json' }
            ])
          )
          .toPromise()
          .then(() => this.contactsService.fetch().then(() => this.initializeItems())) // refresh
          .catch((err) => console.log('[ContactList] hiding error: ' + err));
        }},
        { text: 'OK', handler: () => {

          // accept friend request
          this.authService.http().patch(
            CONFIG.API_URL + 'users/friends/' + item.id + '/',
            { is_accepted: true },
            this.authService.createOptions([
              { name: 'Content-Type', value: 'application/json' }
            ])
          )
          .toPromise()
          .then(() => this.contactsService.fetch().then(() => this.initializeItems())) // refresh
          .catch((err) => console.log('[ContactList] accepting error: ' + err));
        }}
      ],
      enableBackdropDismiss: false
    }).present();
  }

  friends() {
    if(this.items != null) {
      return this.items.filter((item) => {
        return item.is_accepted == true && item.is_blocked == false && item.is_hidden == false;
      });
    }
    return [];
  }

  actionsSheetFriends(item) {
    this.actionSheetCtrl.create({
      title: item.friend.username,
      cssClass: 'action-sheets-basic-page',
      buttons: [
        { text: 'Block', handler: () => {

           // block friend
           this.authService.http().patch(
            CONFIG.API_URL + 'users/friends/' + item.id + '/',
            { is_blocked: true },
            this.authService.createOptions([
              { name: 'Content-Type', value: 'application/json' }
            ])
          )
          .toPromise()
          .then(() => this.contactsService.fetch().then(() => this.initializeItems())) // refresh
          .catch((err) => console.log('[ContactList] blocking error: ' + err));
        }},
        { text: 'Remove', role: 'destructive', handler: () => {

          // TODO remove friend 
        }},
        { text: 'Cancel', role: 'cancel' }
      ]
    }).present();
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

  popupBlockedFriends(item) {
    this.alertCtrl.create({
      title: 'Unblock ' + item.friend.username + ' ?',
      message: 'Click OK to unblock',
      buttons: [
        { text: 'Cancel' },
        { text: 'OK', handler: () => {

          // unblock friend
          this.authService.http().patch(
            CONFIG.API_URL + 'users/friends/' + item.id + '/',
            { is_blocked: false },
            this.authService.createOptions([
              { name: 'Content-Type', value: 'application/json' }
            ])
          )
          .toPromise()
          .then(() => this.contactsService.fetch().then(() => this.initializeItems())) // refresh
          .catch((err) => console.log('[ContactList] unblocking error: ' + err));
        }}
      ],
      enableBackdropDismiss: false
    }).present();
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

  // nav to CreateGathering
  goToWaitingForParticipant() {

    // Reset gathering
    this.gatheringService.status = 'create';
    this.gatheringService.initiator = true;
    this.gatheringService.meetings = {};
    this.gatheringService.meetings.organiser = this.meService.me;
    this.gatheringService.meetings.participants = this.items.filter((i) => {
      return i.checked; 
    }).map((i) => {
      return { user: i.friend };
    });

    // getRootNav() needed to get out of the Tabs
    this.app.getRootNav().push(CreateGathering);
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
