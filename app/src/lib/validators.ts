import "rxjs/add/operator/take";
import { FormGroup, Validators as NGValidators, AbstractControl } from '@angular/forms';
import libphonenumber from 'google-libphonenumber';

/**
 * Validators
 * Custom validators
 * Patrick Champion - 02.11.2016
 */
export module RadyModule {

    // Validator result type
    export type ValidatorResult = {[control: string]: string;};

    export class Validators {

        /**
         * Required validator
         * Check if the required controls are not empty
         * @param controls
         * @param msg
         */
        public static required(controls: string[], msg: string) {
            return (group: FormGroup): ValidatorResult => {
                let errors = {};
                for (let control of controls) {
                    if (group.get(control).value.length === 0)
                        errors[control] = msg;
                }
                return Object.keys(errors).length === 0 ? null : errors;
            }
        }

        /**
         * Phone validator
         * Check if the control the a valid phone
         * Thanks: http://stackoverflow.com/questions/40251781/how-do-i-use-google-phonenumber-lib-in-ionic-project
         * @param phonecontrol
         * @param countrycontrol
         * @param msg
         */
        public static phone(phonecontrol: string, countrycontrol: string, msg: string) {
            return (group: FormGroup): ValidatorResult => {
                if (group.get(phonecontrol).value.length === 0)
                    return null;
                let errors = {};
                try {
                    const phoneUtil = libphonenumber.PhoneNumberUtil.getInstance();
                    const phoneNumber = phoneUtil.parse(group.get(phonecontrol).value, group.get(countrycontrol).value);
                    if (!phoneUtil.isValidNumber(phoneNumber))
                        errors[phonecontrol] = msg;
                } catch (e) {
                    errors[phonecontrol] = msg;
                }
                return Object.keys(errors).length === 0 ? null : errors;
            }
        }

        /**
         * areEqual validator
         * Check if controls are equal
         * Thanks: https://angular.io/docs/ts/latest/api/forms/index/FormGroup-class.html
         * @param controls
         * @param msg
         */
        public static areEqual(controls: string[], msg: string) {
            return (group: FormGroup): ValidatorResult => {
                let errors = {};
                let value = group.get(controls[0]).value;
                for (let i = 1; i < controls.length; ++i) {
                    if (value !== group.get(controls[i]).value)
                        errors[controls[i]] = msg;
                }
                return Object.keys(errors).length === 0 ? null : errors;
            }
        }
    }
}


export class RadyValidators {
    /**
     * Check if the provided value is a valid email
     */
    public static email() {
        let validator = NGValidators.pattern(
            // tslint:disable-next-line:max-line-length
            /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/,
        );

        return (control: AbstractControl) => {
            if (validator(control) !== null) {
                return {"email": "not valid"};
            }
            return null;
        };
    }

    /**
     * Check that the two provided control values are the same.
     *
     * @param other name of the control for which to check for equality
     * @param message to return on error
     */
    public static match(other: AbstractControl, message: string) {
        return (c: AbstractControl) => {
            if (other.value !== c.value) {
                return {match: {valid: false, message: message}};
            }
            return null;
        };
    }

    /**
     * Check that the given value is a valid phone
     */
    public static phone(country: AbstractControl) {
        const phoneUtil = libphonenumber.PhoneNumberUtil.getInstance();

        return (c: AbstractControl) => {
            if (!c.value || !country.value) {
                return null;
            }
            try {
                if (phoneUtil.isValidNumber(phoneUtil.parse(c.value, country.value))) {
                    return null;
                }
                // tslint:disable-next-line:no-empty
            } catch (e) {
            }

            return { phone: false };
        };

    }

}
