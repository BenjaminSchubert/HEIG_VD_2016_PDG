import { Component } from "@angular/core";
import { NavController, AlertController } from "ionic-angular";
import { Validators, FormBuilder } from "@angular/forms";
import { RadyValidators } from "../../lib/validators";
import { BaseFormComponent } from "../../lib/form-component";
import { AuthService } from "../../providers/auth-service";


/**
 * ForgottenPassword
 *
 * @author Patrick Champion
 */
@Component({
    templateUrl: "forgotten-password.html",
})
export class ForgottenPassword extends BaseFormComponent {
    constructor(builder: FormBuilder,
                private service: AuthService,
                private navCtrl: NavController,
                private alertCtrl: AlertController) {
        super(builder);
    }

    public resetPassword() {
        this.service.resetPassword(this.form.value).subscribe(
            () => {
                this.alertCtrl
                    .create({
                        buttons: [{
                            handler: () => this.navCtrl.pop(),
                            text: "Go back to Sign In",
                        }],
                        enableBackdropDismiss: false,
                        message: "All information for resetting your password have been sent to your email address.",
                        title: "Email sent!",
                    })
                    .present()
                    .then();
            },
        );
    }

    protected buildForm() {
        return this.builder.group({
            email: [null, Validators.compose([Validators.required, RadyValidators.email()])],
        });
    }
}
