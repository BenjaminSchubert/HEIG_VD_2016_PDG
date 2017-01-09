import "rxjs/add/operator/catch";

import { Component } from "@angular/core";
import { Validators, FormBuilder, FormGroup } from "@angular/forms";
import { Response } from "@angular/http";
import { NavController, AlertController } from "ionic-angular";

import { countries } from "../../lib/countries";
import { RadyValidators } from "../../lib/validators";
import { AuthService } from "../../providers/auth-service";
import { BaseFormComponent } from "../../lib/form-component";
import { MainTabs } from "../main-tabs/main-tabs";


/**
 * Registration form
 *
 * @author Patrick Champion
 */
@Component({
    templateUrl: "register.html",
})
export class Register extends BaseFormComponent {
    public countries = countries;

    public get countryCodes() {
        return Object.keys(this.countries);
    }

    constructor(public navCtrl: NavController,
                builder: FormBuilder,
                private authService: AuthService,
                private alertCtrl: AlertController) {
        super(builder);
    }

    public register() {
        this.authService.register(this.form.value)
            .do(() => this.authService.login(
                {email: this.form.get("email").value, password: this.form.get("password").value}),
            )
            .subscribe(
                () => {
                    this.alertCtrl.create({
                        buttons: [{
                            handler: () => this.navCtrl.setRoot(MainTabs),
                            text: "OK",
                        }],
                        enableBackdropDismiss: false,
                        message: "You can now find your friend !",
                        title: "Welcome!",
                    }).present();
                },
                (err: Response) => {
                    this.handleError(err.json(), this.form);
                    this.alertCtrl.create({
                        buttons: ["BACK"],
                        enableBackdropDismiss: true,
                        message: "Could not register with the given information",
                        title: "Registration error",
                    }).present();
                },
            );
    }

    protected buildForm() {
        let form = this.builder.group({
            country: [null],
            email: [null, Validators.compose([RadyValidators.email(), Validators.required])],
            password: [null],
            passwordConfirmation: [null],
            phone: [null],
            username: [null, Validators.required],
        });

        form.get("passwordConfirmation").setValidators(Validators.compose([
            Validators.required,
            RadyValidators.match(form.get("password"), "passwords do not match."),
        ]));

        form.get("phone").setValidators(RadyValidators.phone(form.get("country")));

        this.subscriptions.push(
            form.get("phone").valueChanges.subscribe((value: string) => {
                if (!value) {
                    this.form.get("country").clearValidators();
                    this.form.get("country").setValue(undefined);
                } else {
                    // tslint:disable-next-line:triple-equals
                    if ((<FormGroup> this.form.get("country")).controls == null) {
                        this.form.get("country").setValidators(Validators.required);
                        this.form.get("country").markAsTouched();
                        this.form.get("country").markAsDirty();
                        this.form.get("country").updateValueAndValidity();
                    }
                }
            }),
            form.get("password").valueChanges.subscribe(() => form.get("passwordConfirmation").updateValueAndValidity()),
        );

        return form;
    }
}
