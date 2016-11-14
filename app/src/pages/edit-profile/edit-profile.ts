import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder } from '@angular/forms';

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
      username: ['', Validators.required],
      email: ['', Validators.compose([Validators.required, RadyModule.Validators.email])],
      phone: ['', RadyModule.Validators.phone],
      password: ['', Validators.required],
      passwordConfirmation: ['', Validators.required]
  	}, { validator: RadyModule.Validators.areEqual(['password', 'passwordConfirmation']) });
  }

  save(){
    //TODO : SAVE USER LOCALY
    //TODO : SAVE USER ON SEVER
  }

}
