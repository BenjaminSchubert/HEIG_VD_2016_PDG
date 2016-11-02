import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder } from '@angular/forms';

import { Register } from '../register/register';

/**
 * SignIn
 * Sign-in form 
 * Patrick Champion - 29.10.2016 
 */
@Component({
  templateUrl: 'sign-in.html'
})
export class SignIn {

  // attributes
  form;

  constructor(public navCtrl: NavController,
  			  private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
  	// create the form with validation
  	this.form = this.formBuilder.group({
  		email: ['', Validators.required], 
  		password: ['', Validators.required]
  	});
  }

  doSignIn() {

  }

  // Go to the Register page
  goToRegister() {
    this.navCtrl.push(Register);
  }

  goToForgottenPassword() {
  	
  }
}
