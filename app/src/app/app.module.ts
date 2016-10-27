import { NgModule } from '@angular/core';
import { IonicApp, IonicModule } from 'ionic-angular';
import { RadyApp } from './app.component';

import { Splashscreen } from '../pages/splashscreen/splashscreen';

var components: any = [
  RadyApp,
  Splashscreen
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
