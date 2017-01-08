import { Component } from "@angular/core";
import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AccountService } from "./account.service";
import { Response } from "@angular/http";
import { noop } from "../base";


/**
 * Component to login a user
 */
@Component({
    styleUrls: ["./login.scss"],
    templateUrl: "./login.html",
})
export class LoginComponent {
    /**
     * Form for login
     */
    public form: FormGroup;

    /**
     * Map of error to error messages
     */
    protected errorMessages: {[key: string]: (err: {} | string) => string } = {
        // tslint:disable-next-line:no-any
        required: (err: any) => "This field is required",
        serverError: (err: string) => err,
    };

    constructor(public account: AccountService, private builder: FormBuilder) {
        this.form = this.builder.group({
            password: ["", Validators.required],
            username: ["", Validators.required],
        });
    }

    /**
     * Login the user with the value contained in `form`
     */
    public login() {
        this.account.login(this.form.value).subscribe(
            noop,
            (err: Response) => this.handleError(err.json(), this.form),
        );
    }

    /**
     * Nicely displays form's errors
     *
     * @param errors to display
     * @returns {string[]}
     */
    // tslint:disable-next-line:no-any
    public display_error(errors: any): string[] {
        if (errors === null) {
            return;
        }

        let messages: string[] = [];

        for (let entry in errors) {
            if (this.errorMessages[entry] !== undefined) {
                messages.push(this.errorMessages[entry](errors[entry]));
            }
        }
        if (!messages.length) {
            return ["Undefined error"];
        }

        return messages;
    }

    /**
     * Set the errors given in parameter to the correct control
     *
     * @param error to dispatch
     * @param ctrl root
     */
    // tslint:disable-next-line:no-any
    protected handleError(error: any, ctrl: FormGroup) {
        for (let entry in error) {
            if (ctrl.get(entry) !== null) {
                ctrl.get(entry).setErrors({"serverError": error[entry]});
            } else {
                ctrl.setErrors({"serverError": error[entry]});
            }
        }
    }


}
