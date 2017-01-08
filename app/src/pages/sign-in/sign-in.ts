import { Component } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';

import { RadyModule } from '../../lib/validators';
import { AuthService } from '../../providers/auth-service';

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
  			      private formBuilder: FormBuilder,
              private authService: AuthService,
              private alertCtrl: AlertController) {
    
    // create the form with validation
    this.form = this.formBuilder.group({
      email: [''], 
      password: ['']
    }, { validator: Validators.compose([
      RadyModule.Validators.email('email', 'is not valid'),
      RadyModule.Validators.required(['email', 'password'], 'is required')]) 
    });
  }

  ionViewDidLoad() {
  }

  get errors() {
    return JSON.stringify(this.form.errors);
  }

  doSignIn() {
    // check if the form is valid
    if(this.form.valid) {

      // create the payload
      let credentials = {
        email: this.form.get('email').value,
        password: this.form.get('password').value
      };

      // try the log in
      this.authService.authentificate(credentials)

        // on success, go to MainTabs
        .then(() => {
          this.navCtrl.setRoot(MainTabs);
        })
        
        // on error, show an alert with the error
        .catch((err) => {
          console.log(JSON.stringify(err));
          this.alertCtrl.create({
            title: 'Sign In error',
            message: 'Unable to login with provided credentials.\nPlease check your email and password.', 
            buttons: ['OK'],
            enableBackdropDismiss: false
          }).present();
        });
    }
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
