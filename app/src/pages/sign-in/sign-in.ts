import { Component } from "@angular/core";
import { NavController, AlertController } from "ionic-angular";
import { Validators, FormBuilder } from "@angular/forms";
import { BaseFormComponent } from "../../lib/form-component";
import { RadyValidators } from "../../lib/validators";
import { AuthService } from "../../providers/auth-service";
import { Register } from "../register/register";
import { ForgottenPassword } from "../forgotten-password/forgotten-password";
import { MainTabs } from "../main-tabs/main-tabs";


/**
 * Sign-in form
 *
 * @author Patrick Champion
 */
@Component({
    templateUrl: "sign-in.html",
})
export class SignIn extends BaseFormComponent {
    constructor(builder: FormBuilder,
                private navCtrl: NavController,
                private authService: AuthService,
                private alertCtrl: AlertController) {
        super(builder);
    }

    protected buildForm() {
        return this.builder.group({
            email: [null, Validators.compose([RadyValidators.email(), Validators.required])],
            password: [null, Validators.required],
        });
    }

    public login() {
        this.authService.login(this.form.value).subscribe(
            () => this.navCtrl.setRoot(MainTabs),
            () => this.alertCtrl.create({
                buttons: ["OK"],
                enableBackdropDismiss: false,
                message: "Unable to login with provided credentials.\nPlease try again.",
                title: "Sign In error",
            }).present(),
        );
    }

    public goToRegister() {
        this.navCtrl.push(Register);
    }

    public goToForgottenPassword() {
        this.navCtrl.push(ForgottenPassword);
    }

}
