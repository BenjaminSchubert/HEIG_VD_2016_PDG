import { Component } from "@angular/core";
import { NavController, App } from "ionic-angular";
import { EditProfile } from "../edit-profile/edit-profile";
import { SignIn } from "../sign-in/sign-in";
import { AuthService } from "../../providers/auth-service";
import { AccountService } from "../../providers/account-service";


@Component({
    templateUrl: "settings.html",
})
export class Settings {
    constructor(private navCtrl: NavController,
                private app: App,
                private authService: AuthService,
                private service: AccountService) {
    }

    public ionViewWillEnter() {
        this.service.fetch().subscribe();
    }

    public editProfile() {
        this.app.getRootNav().push(EditProfile).then();
    }

    public hide() {
        this.service.hide().subscribe();
    }

    public logout() {
        return this.authService.logout()
            .then(() => this.app.getRootNav().push(SignIn))
            .then(() => {
                const index = this.app.getRootNav().getActive().index;
                this.app.getRootNav().remove(0, index);
            });
    }

    public sendEmail() {
        window.open("mailto:rady@benschubert.me", "_system");
    }

}
