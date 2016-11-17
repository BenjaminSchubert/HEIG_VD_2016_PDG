import { Component } from '@angular/core';
import { NavController, Tabs } from 'ionic-angular';
import { Validators, FormBuilder } from '@angular/forms';

import { MainTabs } from '../main-tabs/main-tabs';

import { RadyModule } from '../../lib/validators';

@Component({
  templateUrl: 'edit-profile.html'
})
export class EditProfile {

  form;
  constructor(public navCtrl: NavController, private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
    //TODO : GET CURRENT USER

  	// create the form with validation
    this.form = this.formBuilder.group({
      username: [''],
      email: [''],
      phone: [''],
      country: [''],
      password: [''],
      passwordConfirmation: ['']
  	}, { validator: Validators.compose([
      RadyModule.Validators.email('email', 'is not valid'),
      RadyModule.Validators.phone('phone', 'country', 'is not valid'),
      RadyModule.Validators.areEqual(['password', 'passwordConfirmation'], 'passwords are not equal'),
      RadyModule.Validators.required(['username', 'email', 'password', 'passwordConfirmation'], 'is required')])
    });
  }

  goToContactList(){
    this.navCtrl.setRoot(MainTabs);
  }

  save(){
    //TODO : SAVE USER LOCALY
    //TODO : SAVE USER ON SEVER
    this.goToContactList();
  }

  get errors() {
    return JSON.stringify(this.form.errors);
  }

}
