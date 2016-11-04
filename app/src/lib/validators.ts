import { AbstractControl } from '@angular/forms';

/** 
 * Validators
 * Custom validators
 * Patrick Champion - 02.11.2016
 */
export module RadyModule {

	// Validator result type
	export type ValidatorResult = { [key: string]: boolean; };

	export class Validators {

		/**
		 * Email validator
		 * Check if the control is a valid email
		 * @param control 
		 */
		public static email(control: AbstractControl): ValidatorResult {
			return null;
		}

		/**
		 * Phone validator
		 * Check if the control the a valid phone
		 * @param control
		 */
		public static phone(control: AbstractControl): ValidatorResult {
			return null;
		}

		/** 
		 * areEqual validator
		 * Check if controls are equal
		 * @param controls
		 */
		public static areEqual(controls: string[]) {
			return (control: AbstractControl): ValidatorResult => {
				return null;
			}
		}
	}
}