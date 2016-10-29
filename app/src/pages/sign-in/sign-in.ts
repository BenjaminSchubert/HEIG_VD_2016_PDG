import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder } from '@angular/forms';

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
  signIn;

  constructor(public navCtrl: NavController,
  			  private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
  	// create the form with validation
  	this.signIn = this.formBuilder.group({
  		username: ['', Validators.required],
  		password: ['', Validators.required]
  	});
  }

  doSignIn() {

  }

  goToRegister() {

  }

  goToForgottenPassword() {
  	
  }
}
