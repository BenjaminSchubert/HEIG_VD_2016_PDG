import "rxjs/add/operator/debounceTime";
import { Component } from "@angular/core";
import { App } from "ionic-angular";
import { EditProfile } from "../edit-profile/edit-profile";
import { SignIn } from "../sign-in/sign-in";
import { AuthService } from "../../providers/auth-service";
import { AccountService } from "../../providers/account-service";


@Component({
    templateUrl: "settings.html",
})
export class Settings {
    private hiding = false;

    constructor(private app: App,
                private authService: AuthService,
                private service: AccountService) {
    }

    public ionViewWillEnter() {
        this.service.fetch().subscribe();
    }

    public editProfile() {
        this.app.getRootNav().push(EditProfile).then();
    }

    public hide(event: any) {
        if (!this.hiding) {
            this.hiding = true;
            // We need to debounce due to https://github.com/driftyco/ionic/issues/7806 and other changes like that
            this.service.hide().debounceTime(10000).subscribe(() => this.hiding = false);
        }
    }

    public logout() {
        return this.authService.logout()
            .then(() => this.app.getRootNav().push(SignIn))
            .then(() => this.app.getRootNav().remove(0, this.app.getRootNav().getActive().index));
    }

    public sendEmail() {
        window.open("mailto:rady@benschubert.me", "_system");
    }

}
