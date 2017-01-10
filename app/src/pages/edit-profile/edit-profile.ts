import { Component } from "@angular/core";
import { AlertController, NavController } from "ionic-angular";
import { FormBuilder } from "@angular/forms";
import { Response } from "@angular/http";
import { MainTabs } from "../main-tabs/main-tabs";
import { AccountFormComponent } from "../../lib/form-component";
import { AccountService } from "../../providers/account-service";
import { IAccount } from "../../lib/stubs/account";
import { RadyValidators } from "../../lib/validators";


@Component({
    templateUrl: "edit-profile.html",
})
export class EditProfile extends AccountFormComponent {
    public user: IAccount;

    constructor(builder: FormBuilder,
                private service: AccountService,
                private navCtrl: NavController,
                private alertCtrl: AlertController) {
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

    public submit() {
        let value = JSON.stringify(this.form.value, (k, v) => v !== null ? v : undefined);
        // tslint:disable-next-line:no-any
        this.service.update(<any> value).subscribe(
            () => {
                this.alertCtrl.create({
                    buttons: [{
                        handler: () => this.navCtrl.setRoot(MainTabs),
                        text: "OK",
                    }],
                    enableBackdropDismiss: false,
                    title: "Profile Updated!",
                }).present().then();
            },
            (err: Response) => {
                this.handleError(err.json(), this.form);
                this.alertCtrl.create({
                    buttons: ["OK"],
                    enableBackdropDismiss: true,
                    message: "Please verify your data",
                    title: "Could not save",
                }).present().then();
            },
        );
    }

    protected buildForm() {
        let form = super.buildForm();

        form.get("passwordConfirmation").setValidators(
            RadyValidators.match(form.get("password"), "passwords do not match."),
        );

        this.subscriptions.push(
            form.get("password").valueChanges.subscribe(() => {
                form.get("passwordConfirmation").markAsPristine();
                form.get("passwordConfirmation").markAsDirty();
                form.get("passwordConfirmation").updateValueAndValidity();
            }),
        );

        return form;
    }

}
