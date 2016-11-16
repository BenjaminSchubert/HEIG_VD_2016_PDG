import { NgModule } from '@angular/core';
import { IonicApp, IonicModule } from 'ionic-angular';

import { RadyApp } from './app.component';

import { Splashscreen } from '../pages/splashscreen/splashscreen';
import { SignIn } from '../pages/sign-in/sign-in';
import { Register } from '../pages/register/register';
import { ForgottenPassword } from '../pages/forgotten-password/forgotten-password';

import { MainTabs } from '../pages/main-tabs/main-tabs'
import { Settings } from '../pages/settings/settings'
import { ContactList } from '../pages/contact-list/contact-list'
import { History } from '../pages/history/history'
import { EditProfile } from '../pages/edit-profile/edit-profile'

import { AddContact } from '../pages/add-contact/add-contact';
import { AddContactFromList } from '../pages/add-contact-from-list/add-contact-from-list';
import { AddContactFromScanner } from '../pages/add-contact-from-scanner/add-contact-from-scanner';
import { MyQrCode } from '../pages/my-qr-code/my-qr-code';

// put here the components
var components: any = [
  RadyApp,
  Splashscreen,
  SignIn,
  Register,
  ForgottenPassword,
  Settings,
  ContactList,
  History,
  EditProfile,
  MainTabs,
  AddContact,
  AddContactFromList,
  AddContactFromScanner,
  MyQrCode
]

@NgModule({
  declarations: components,
  imports: [
    IonicModule.forRoot(RadyApp,{tabsPlacement: 'top'})
  ],
  bootstrap: [IonicApp],
  entryComponents: components,
  providers: []
})
export class AppModule {}
