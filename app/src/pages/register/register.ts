import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';

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
  form: FormGroup;

  constructor(public navCtrl: NavController,
  	          private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
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

  get errors() {
    return JSON.stringify(this.form.errors);
  }

  doRegister() {
    
  }
}
