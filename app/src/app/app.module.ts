import { NgModule } from '@angular/core';
import { IonicApp, IonicModule } from 'ionic-angular';

import { RadyApp } from './app.component';

import { Splashscreen } from '../pages/splashscreen/splashscreen';
import { SignIn } from '../pages/sign-in/sign-in';

// put here the components
var components: any = [
  RadyApp,
  Splashscreen,
  SignIn
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
