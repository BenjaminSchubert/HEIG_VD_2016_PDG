import { Component } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';
import { Validators, FormBuilder, FormGroup } from '@angular/forms';

import { RadyModule } from '../../lib/validators';
import { AuthService } from '../../providers/auth-service';

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
  	          private formBuilder: FormBuilder,
              private authService: AuthService,
              private alertCtrl: AlertController) {}

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
      RadyModule.Validators.areEqual(['password', 'passwordConfirmation'], 'is not equal with password'), 
      RadyModule.Validators.required(['username', 'email', 'password', 'passwordConfirmation'], 'is required')]) 
    });
  }

  get errors() {
    return JSON.stringify(this.form.errors);
  }

  doRegister() {
    // check if the form is valid
    if(this.form.valid) {

      // create the payload
      let informations = {
        username: this.form.get('username').value,
        email: this.form.get('email').value,
        password: this.form.get('password').value
      };
      if(this.form.get('phone').value.length > 0) {
        informations['phone'] = this.form.get('phone').value;
        informations['country'] = this.form.get('country').value;
      }

      // try the registration
      this.authService.register(informations)

        // on success, show an alert and go back to SignIn
        .then(() => {
          this.alertCtrl.create({
            title: 'Registration done!',
            message: 'You can now sign in with your new account.',
            buttons: [{
              text: 'Go back to Sign In',
              handler: () => { this.navCtrl.pop(); }
            }],
            enableBackdropDismiss: false
          }).present();
        })
        
        // on error, show an alert with the error
        .catch((err) => {
          console.log(JSON.stringify(err));
          this.alertCtrl.create({
            title: 'Registration error',
            message: informations.email + ' is already taken.\nPlease use an other email.', 
            buttons: ['OK'],
            enableBackdropDismiss: false 
          }).present();
        });
    }
  }
}
