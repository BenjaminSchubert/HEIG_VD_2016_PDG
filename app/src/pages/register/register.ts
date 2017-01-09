import "rxjs/add/operator/catch";
import { Component } from "@angular/core";
import { FormBuilder, Validators } from "@angular/forms";
import { Response } from "@angular/http";
import { NavController, AlertController } from "ionic-angular";
import { AuthService } from "../../providers/auth-service";
import { AccountFormComponent } from "../../lib/form-component";
import { MainTabs } from "../main-tabs/main-tabs";
import { RadyValidators } from "../../lib/validators";


/**
 * Registration form
 *
 * @author Patrick Champion
 */
@Component({
    templateUrl: "register.html",
})
export class Register extends AccountFormComponent {
    constructor(builder: FormBuilder,
                public navCtrl: NavController,
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
        let form = super.buildForm();

        form.get("password").setValidators(Validators.required);
        form.get("passwordConfirmation").setValidators(Validators.compose([
            Validators.required,
            RadyValidators.match(form.get("password"), "passwords do not match."),
        ]));

        return form;
    }

}
