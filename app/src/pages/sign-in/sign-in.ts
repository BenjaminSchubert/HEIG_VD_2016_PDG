import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';

import { RadyModule } from '../../lib/validators';

import { Register } from '../register/register';
import { ForgottenPassword } from '../forgotten-password/forgotten-password';
import { MainTabs } from '../main-tabs/main-tabs';

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
  form: FormGroup;

  constructor(public navCtrl: NavController,
  			  private formBuilder: FormBuilder) {}

  ionViewDidLoad() {
  	// create the form with validation
  	this.form = this.formBuilder.group({
  		email: [''], 
  		password: ['']
  	}, { validator: Validators.compose([
      RadyModule.Validators.email('email', 'is not valid'),
      RadyModule.Validators.required(['email', 'password'], 'is required')]) 
    });
  }

  get errors() {
    return JSON.stringify(this.form.errors);
  }

  doSignIn() {
    // TODO : ADD USER IN "SESSION"
    this.navCtrl.setRoot(MainTabs);
  }

  // Go to the Register page
  goToRegister() {
    this.navCtrl.push(Register);
  }

  // Go to the ForgottenPassword page
  goToForgottenPassword() {
  	this.navCtrl.push(ForgottenPassword);
  }
}
