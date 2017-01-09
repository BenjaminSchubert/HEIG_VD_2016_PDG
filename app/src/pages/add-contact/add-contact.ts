import { Component } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';

import { AddContactFromList } from '../add-contact-from-list/add-contact-from-list';
import { AddContactFromScanner } from '../add-contact-from-scanner/add-contact-from-scanner';
import { MyQrCode } from '../my-qr-code/my-qr-code';

import { AuthService } from '../../providers/auth-service';
import { CONFIG } from '../../providers/config';

/**
 * AddContact
 * Adding a new contact from differents sources
 * Patrick Champion - 15.11.2016
 */
@Component({
  templateUrl: 'add-contact.html'
})
export class AddContact {

  // list of found users
  added: any[];
  users: any[];
  message: string;
  searchFocus: boolean;

  constructor(public navCtrl: NavController,
              public authService: AuthService,
              public alertCtrl: AlertController) {
    this.added = [];
    this.users = [];
    this.message = "";
    this.searchFocus = false;
  }

  ionViewDidLoad() {

  }

  goToAddContactFromList() {
    this.navCtrl.push(AddContactFromList);
  }

  goToAddContactFromScanner() {
    this.navCtrl.push(AddContactFromScanner);
  }

  goToMyQrCode() {
    this.navCtrl.push(MyQrCode);
  }

  doSearch(ev) {

    // Get the search value
    let value: string = ev.target.value;

    // If there is a value
    if(value.length > 0) {

      // Get the search filter
      let filter = '?username=' + value;

      // Ask the API for matching user
      this.authService.get(CONFIG.API_URL + 'users/' + filter)
      .map(res => res.json())
      .subscribe(
        (data) => this.users = data,
        (err) => this.message = "An error occured during the searching process, please try again later."
      );
    }
  }

  doAddContact(user) {

    // Ask the user for confirmation before the adding
    this.alertCtrl.create({
      title: 'Confirmation',
      message: 'Send a friend request to ' + user.username + ' ?',
      buttons: [
        {text: 'Cancel'},
        {
          text: 'Yes',
          handler: () => {

            // Send the friend request
            this.authService.post(
              CONFIG.API_URL + "/users/friends/",
              JSON.stringify({ 'friend': user.id }),
            )
            .map(res => res.json())
            .subscribe(
              () => this.added[this.added.length] = user,
              (err) => this.message = 'An error occured during the adding process, please try again later.'
            );
          }
        }
      ],
      enableBackdropDismiss: false
    }).present();
  }
}
