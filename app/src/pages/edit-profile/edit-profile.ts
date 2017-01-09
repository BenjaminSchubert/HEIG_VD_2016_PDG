import { Component } from "@angular/core";
import { NavController } from "ionic-angular";
import { FormBuilder } from "@angular/forms";
import { Response } from "@angular/http";
import { MainTabs } from "../main-tabs/main-tabs";
import { AccountFormComponent } from "../../lib/form-component";
import { AccountService } from "../../providers/account-service";
import { IAccount } from "../../lib/stubs/account";


@Component({
    templateUrl: "edit-profile.html",
})
export class EditProfile extends AccountFormComponent {
    public user: IAccount;

    constructor(builder: FormBuilder, public service: AccountService, public navCtrl: NavController) {
        super(builder);
        this.subscriptions.push(this.service.$.subscribe((a: IAccount) => {
            this.user = a;
            if (this.user !== null) {
                this.form.patchValue(this.user);
            }
        }));
    }

    public ionViewWillEnter() {
        this.service.fetch().subscribe();
        super.ionViewWillEnter();
    }

    goToContactList() {
        this.navCtrl.setRoot(MainTabs);
    }

    public submit() {
        let value = JSON.stringify(this.form.value, (k, v) => v !== null ? v : undefined);
        this.service.update(<any> value).subscribe(
            () => this.goToContactList(),
            (err: Response) => this.handleError(err.json(), this.form),
        );
    }

}
