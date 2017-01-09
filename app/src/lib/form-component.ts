import { Subscription } from "rxjs/Subscription";
import { AbstractControl, FormBuilder, Validators, FormGroup } from "@angular/forms";
import { RadyValidators } from "./validators";
import { countries } from "../lib/countries";


export abstract class BaseFormComponent {
    protected form: AbstractControl;

    protected errorMessages: {[key: string]: (err: {} | string) => string} = {
        "email": () => "This is not a valid email.",
        "match": (err: {message: string}) => err.message,
        "phone": () => "This is not a valid phone number",
        "required": () => "This field is required",
        "serverError": (err: string) => err,
    };
    protected subscriptions: Subscription[];

    protected abstract buildForm(): AbstractControl;

    constructor(protected builder: FormBuilder) {
        this.subscriptions = [];
        this.form = this.buildForm();
    }

    public ionViewWillEnter() {
        this.form.reset();
    }

    public ionViewWillUnload() {
        this.subscriptions.forEach((s: Subscription) => s.unsubscribe());
        this.subscriptions = [];
    }

    // tslint:disable-next-line:no-any
    public display_error(errors: any): string {
        // tslint:disable-next-line:triple-equals
        if (errors == null) {
            return;
        }

        for (let entry in errors) {
            if (this.errorMessages[entry] !== undefined) {
                return this.errorMessages[entry](errors[entry]);
            }
        }
        this.signalUndefinedError(errors);
        return "Undefined error";
    }

    // tslint:disable-next-line:no-any
    protected handleError(error: any, ctrl: AbstractControl) {
        console.log("ERRORS " + JSON.stringify(error));
        for (let entry in error) {
            if (ctrl.get(entry) !== null) {
                ctrl.get(entry).setErrors({"serverError": error[entry]});
            } else {
                ctrl.setErrors({"serverError": error[entry]});
            }
        }
    }

    // tslint:disable-next-line:no-any
    protected signalUndefinedError(error: any) {
        console.log("Undefined error message for " + JSON.stringify(error));
    }
}


export abstract class AccountFormComponent extends BaseFormComponent {
    public countries = countries;

    public get countryCodes() {
        return Object.keys(this.countries);
    }

    protected buildForm() {
        let form = this.builder.group({
            country: [null],
            email: [null, Validators.compose([RadyValidators.email(), Validators.required])],
            password: [null],
            passwordConfirmation: [null],
            phone_number: [null],
            username: [null, Validators.required],
        });

        form.get("phone_number").setValidators(RadyValidators.phone(form.get("country")));

        this.subscriptions.push(
            form.get("phone_number").valueChanges.subscribe((value: string) => {
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
            form.get("password").valueChanges.subscribe(
                () => form.get("passwordConfirmation").updateValueAndValidity()
            ),
        );

        return form;
    }
}
