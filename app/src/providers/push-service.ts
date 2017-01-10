import { Injectable } from "@angular/core";
import { Response } from "@angular/http";
import { Push } from "ionic-native";
import { AuthService } from "./auth-service";
import { NotificationService } from "./notification-service";
import { FCM_REGISTRATION_URL } from "../app/api.routes";


/**
 * PushService
 *
 * Init and listen push notifications
 *
 * @author Patrick Champion
 */
@Injectable()
export class PushService {
    private registered: boolean;

    constructor(private authService: AuthService,
                private notificationService: NotificationService) {
    }

    /**
     * Initialize the service
     *
     * Must be called one time, when the platform is ready
     */
    public initialize() {
        let push = Push.init({
            android: {
                senderID: "395862006671",
            },
            ios: {
                alert: "true",
                badge: true,
                sound: "false",
            },
            windows: {},
        });

        push.on("registration", (data) => {
            this.register(data.registrationId);
        });

        push.on("notification", (data) => {
            if (this.authService.authenticated) {
                this.notificationService.notify(data);
            }
        });

        push.on("error", (data) => {
            console.log("[Rady][PushService] error: \n" + JSON.stringify(data));
        });
    }

    /**
     * Register the FCM token
     */
    private register(token) {
        console.log("[Rady][PushService] trying registration");

        if (this.authService.authenticated) {
            this.authService.post(FCM_REGISTRATION_URL, {registration_id: token})
                .subscribe(
                    () => console.log("[Rady][PushService] registered"),
                    (err: Response) => {
                        console.log("[Rady][PushService] error : " + JSON.stringify(err));
                        // retry 20 seconds after
                        setTimeout(() => this.register(token), 10000);
                    },
                );
        } else {
            setTimeout(() => this.register(token), 10000);
        }
    }

}
