import { NgModule, ErrorHandler } from '@angular/core';
import { RequestOptions } from "@angular/http";
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';

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

import { CreateGathering } from '../pages/create-gathering/create-gathering';
import { CreateGatheringModalFixed } from '../pages/create-gathering-modal-fixed/create-gathering-modal-fixed';
import { PendingGathering } from '../pages/pending-gathering/pending-gathering';
import { RunningGathering } from '../pages/running-gathering/running-gathering';

import { AuthService } from '../providers/auth-service';
import { PushService } from '../providers/push-service';
import { NotificationService } from '../providers/notification-service';
import { ContactsService } from '../providers/contacts-service';
import { MeService } from '../providers/me-service';
import { GatheringService } from '../providers/gathering-service';
import { GeolocationService } from '../providers/geolocation-service';
import { CompassService } from '../providers/compass-service';
import { LeafletHelper } from '../providers/leaflet-helper';
import { ExtendedRequestOptions } from "../lib/request-options";
import { AccountService } from "../providers/account-service";

// put here the components
let COMPONENTS_LIST: any = [
  RadyApp,
  SignIn,
  Register,
  ForgottenPassword,
  Settings,
  ContactList,
  History,
  EditProfile,
  MainTabs,
  AddContact,
  CreateGathering,
  CreateGatheringModalFixed,
  PendingGathering,
  RunningGathering
]


// put here the providers
let PROVIDERS_LIST: any = [
    { provide: ErrorHandler, useClass: IonicErrorHandler },
    { provide: RequestOptions, useClass: ExtendedRequestOptions },
    AuthService,
    AccountService,
  PushService,
  NotificationService,
  ContactsService,
  MeService,
  GeolocationService,
  CompassService,
  LeafletHelper,
    GatheringService,
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
export class RadyAppModule {}
