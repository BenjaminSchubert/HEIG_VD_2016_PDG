import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';


@Component({
  selector: 'page-contact-list',
  templateUrl: 'contact-list.html'
})
export class ContactList {

  constructor(public navCtrl: NavController) {}

  ionViewDidLoad() {
    console.log('Hello ContactList Page');
  }

}
