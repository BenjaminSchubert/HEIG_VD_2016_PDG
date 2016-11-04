import { NgModule } from '@angular/core';
import { IonicApp, IonicModule } from 'ionic-angular';

import { RadyApp } from './app.component';

import { Splashscreen } from '../pages/splashscreen/splashscreen';
import { SignIn } from '../pages/sign-in/sign-in';
import { Register } from '../pages/register/register';
import { ForgottenPassword } from '../pages/forgotten-password/forgotten-password';

// put here the components
var components: any = [
  RadyApp,
  Splashscreen,
  SignIn,
  Register,
  ForgottenPassword
]

@NgModule({
  declarations: components,
  imports: [
    IonicModule.forRoot(RadyApp)
  ],
  bootstrap: [IonicApp],
  entryComponents: components,
  providers: []
})
export class AppModule {}
