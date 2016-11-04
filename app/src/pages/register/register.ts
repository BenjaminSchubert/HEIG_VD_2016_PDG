import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder } from '@angular/forms';

import { RadyModule } from '../../lib/validators';

/**
 * Register
 * Registration form
 * Patrick Champion - 31.10.2016
 */
@Component({
  templateUrl: 'register.html'
})
export class Register {

  // attributes
  form;

  constructor(public navCtrl: NavController,
  	          private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
  	// create the form with validation
  	this.form = this.formBuilder.group({
      username: ['', Validators.required],
      email: ['', Validators.compose([Validators.required, RadyModule.Validators.email])], 
      phone: ['', RadyModule.Validators.phone], 
      password: ['', Validators.required],
      passwordConfirmation: ['', Validators.required]
  	}, { validator: RadyModule.Validators.areEqual(['password', 'passwordConfirmation']) });
  }

  doRegister() {
    
  }
}
