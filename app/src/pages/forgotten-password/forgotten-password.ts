import { Component } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';

import { RadyModule } from '../../lib/validators';

/** 
 * ForgottenPassword
 * Reset password form
 * Patrick Champion - 02.11.2016
 */
@Component({
  templateUrl: 'forgotten-password.html'
})
export class ForgottenPassword {

  // attributes
  form: FormGroup;

  constructor(public navCtrl: NavController,
  			  private formBuilder: FormBuilder,
  			  private alertCtrl: AlertController) {

    // create the form with validation
    this.form = this.formBuilder.group({
      email: ['']
    }, { validator: Validators.compose([
      //RadyModule.Validators.email('email', 'is not valid'),
      RadyModule.Validators.required(['email'], 'is required')])
    });
  }

  ionViewDidLoad() {
  }

  get errors() {
    return JSON.stringify(this.form.errors);
  }

  doResetPassword() {

  	// show an alert to validate the resetting
  	this.alertCtrl.create({
  		title: 'Email sent!',
  		message: 'All informations for resetting your password have been sent to your email address.',
  		buttons: [{
  			text: 'Go back to Sign In',
  			handler: () => { this.navCtrl.pop(); }
  		}],
  		enableBackdropDismiss: false
  	}).present();
  }
}
