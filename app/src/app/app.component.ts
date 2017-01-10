import { Platform, AlertController, Nav } from "ionic-angular";
import { Component, ViewChild, AfterViewInit } from "@angular/core";
import { StatusBar } from "ionic-native";
import { GatheringService } from "../providers/gathering-service";
import { GeolocationService } from "../providers/geolocation-service";
import { NotificationService } from "../providers/notification-service";
import { ContactsService } from "../providers/contacts-service";
import { PushService } from "../providers/push-service";
import { AuthService } from "../providers/auth-service";
import { MainTabs } from "../pages/main-tabs/main-tabs";
import { SignIn } from "../pages/sign-in/sign-in";
import { PendingGathering } from "../pages/pending-gathering/pending-gathering";
import { RunningGathering } from "../pages/running-gathering/running-gathering";


/**
 * RadyApp
 *
 * @author Patrick Champion
 */
@Component({
    template: `<ion-nav [root]="rootPage"></ion-nav>`,
})
export class RadyApp extends AfterViewInit {
    @ViewChild(Nav) public nav: Nav;

    public rootPage = SignIn;

    constructor(private platform: Platform,
                private alertCtrl: AlertController,
                private authService: AuthService,
                private pushService: PushService,
                private notificationService: NotificationService,
                private geolocationService: GeolocationService,
                private gatheringService: GatheringService,
                private contactsService: ContactsService) {
        super();

        // global try-catch
        try {

            // Set the default notification handler
            this.notificationService.setDefaultHandler((n) => {
                this.alertCtrl.create({
                    buttons: ["OK"],
                    enableBackdropDismiss: false,
                    message: n.message,
                    title: n.title,
                }).present().then();
            });

            // redefine the console.log behavior for device testing
            // /!\ comments those lines for production /!\
            let logger = function (nS) {
                return function (text) {
                    nS.notify({
                        title: "CONSOLE.LOG",
                        message: text
                    });
                };
            };
            console.log = logger(this.notificationService);//*/

            platform.ready().then(() => {
                // Okay, so the platform is ready and our plugins are available.
                // Here you can do any higher level native things you might need.
                StatusBar.styleDefault();
                this.authService.initialize()
                    .then(() => this.pushService.initialize())
                    .then(() => this.authService.refresh().toPromise())
                    .then(() => this.nav.setRoot(MainTabs))
                    .catch((err: any) => {
                        if (err.token !== true) {
                            console.log("[Rady][RadyApp] got : " + JSON.stringify(err));
                            this.notifyBadError();
                        }
                        this.rootPage = SignIn;
                        this.nav.setRoot(SignIn).then();
                    });

                this.geolocationService.initialize();
            });
        } catch (err) {
            console.log("[Rady][RadyApp] got : " + JSON.stringify(err));
            this.notifyBadError();
        }
    }

    public ngAfterViewInit() {
        this.gatheringService.configureNotificationHandlers(this.nav, this.alertCtrl, PendingGathering,
            RunningGathering, MainTabs);
        this.contactsService.configureNotificationHandlers(this.notificationService);
    }

    private notifyBadError() {
        this.alertCtrl.create({
            buttons: [{
                handler: () => this.platform.exitApp(),
                text: "OK",
            }],
            enableBackdropDismiss: false,
            // tslint:disable-next-line:max-line-length
            message: "Something bad happened launching the application. We are sorry. If this error persists, please contact the developers",
            title: "Oh Snap !",
        }).present().then();
    }
}
