import { Subscription } from "rxjs/Subscription";
import { AbstractControl, FormBuilder } from "@angular/forms";


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
