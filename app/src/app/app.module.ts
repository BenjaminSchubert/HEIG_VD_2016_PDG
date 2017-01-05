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

import { CreateGathering, CreateGatheringModalFixed } from '../pages/create-gathering/create-gathering';
import { PendingGathering } from '../pages/pending-gathering/pending-gathering';
import { RunningGathering } from '../pages/running-gathering/running-gathering';

import { AuthService } from '../providers/auth-service';
import { PushService } from '../providers/push-service';
import { NotificationService } from '../providers/notification-service';
import { ContactsService } from '../providers/contacts-service';
import { MeService } from '../providers/me-service';
import { GatheringService } from '../providers/gathering-service';

// put here the components
let COMPONENTS_LIST: any = [
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
  MyQrCode,
  CreateGathering, CreateGatheringModalFixed,
  PendingGathering,
  RunningGathering
]

// put here the providers
let PROVIDERS_LIST: any = [
  AuthService,
  PushService,
  NotificationService,
  ContactsService,
  MeService,
  GatheringService
]

@NgModule({
  declarations: COMPONENTS_LIST,
  imports: [
    IonicModule.forRoot(RadyApp,{tabsPlacement: 'top'})
  ],
  bootstrap: [IonicApp],
  entryComponents: COMPONENTS_LIST,
  providers: PROVIDERS_LIST
})
export class AppModule {}
