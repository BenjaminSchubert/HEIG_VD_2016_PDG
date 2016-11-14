import { FormGroup } from '@angular/forms';
import libphonenumber from 'google-libphonenumber';

/** 
 * Validators
 * Custom validators
 * Patrick Champion - 02.11.2016
 */
export module RadyModule {

	// Validator result type
	export type ValidatorResult = { [control: string]: string; };

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
				for(let control of controls) {
					if(group.get(control).value.length == 0)
						errors[control] = msg;
				}
				return Object.keys(errors).length === 0 ? null : errors;
			}
		}

		/**
		 * Email validator
		 * Check if the control is a valid email
		 * Thanks: http://stackoverflow.com/questions/40168655/email-validation-ionic2
		 * @param emailcontrol
		 * @param msg
		 */
		public static email(emailcontrol: string, msg: string) {
			return (group: FormGroup): ValidatorResult => {
				if(group.get(emailcontrol).value.length === 0)
					return null;
				let errors = {};
				let regExp = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
			    if(!regExp.test(group.get(emailcontrol).value))
			    	errors[emailcontrol] = msg;
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
				if(group.get(phonecontrol).value.length === 0)
					return null;
				let errors = {};
				try {
				    const phoneUtil = libphonenumber.PhoneNumberUtil.getInstance();
					const phoneNumber = phoneUtil.parse(group.get(phonecontrol).value, group.get(countrycontrol).value);
					if(!phoneUtil.isValidNumber(phoneNumber))
						errors[phonecontrol] = msg;
				} catch(e) {
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
				let value = group.get(controls[0]).value;
				for(let i = 1; i < controls.length; ++i) {
					if(value !== group.get(controls[i]).value)
						return {'mismatch': msg};
				}
				return null;
			}
		}
	}
}