import { Component } from '@angular/core';
import { NavController, App } from 'ionic-angular';

import { RadyModels } from '../../models/user'

import { AddContact } from '../add-contact/add-contact';

@Component({
  templateUrl: 'contact-list.html'
})
export class ContactList {


  items: RadyModels.User[];
  checked : boolean = true;


  constructor(public navCtrl: NavController,
              public app: App) {
    this.initializeItems();
  }

  initializeItems() {
    this.items = [
      new RadyModels.User('Sauron'),
      new RadyModels.User('Frodon'),
      new RadyModels.User('Gandalf')
    ]
  }

  getItems(ev: any) {
    // Reset items back to all of the items
    this.initializeItems();

    // set val to the value of the searchbar
    let val = ev.target.value;

    // if the value is an empty string don't filter the items
    if (val && val.trim() != '') {
      this.items = this.items.filter((item) => {
        return (item.username.toLowerCase().indexOf(val.toLowerCase()) > -1);
      })
    }
  }


  ionViewDidLoad() {
    console.log('Hello ContactList Page');
  }

  goToAddContact() {
    // getRootNav() needed to get out of the Tabs
    this.app.getRootNav().push(AddContact);
  }

  goToWaitingForParticipant() {

  }

  isSomeChecked(){
    return this.items.some((o:any)=> o.checked === true);
  }

}
