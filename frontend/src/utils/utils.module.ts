import { NgModule, ModuleWithProviders } from "@angular/core";
import { CommonModule } from "@angular/common";
import { HttpModule, RequestOptions, XSRFStrategy, CookieXSRFStrategy } from "@angular/http";
import { RouterModule } from "@angular/router";
import { ReactiveFormsModule } from "@angular/forms";
import { ExtendedRequestOptions } from "./headers";


/**
 * Set the XSRF strategy of the application
 */
export function getXSRFStrategy(): CookieXSRFStrategy {
    return new CookieXSRFStrategy("csrftoken", "X-CSRFToken");
}


/**
 * This module contains utilities used across the application.
 */
@NgModule({
    exports: [CommonModule, ReactiveFormsModule, RouterModule],
    imports: [HttpModule],
})
export class UtilsModule {
    public static forRoot(): ModuleWithProviders {
        return {
            ngModule: UtilsModule,
            providers: [
                {provide: XSRFStrategy, useFactory: getXSRFStrategy},
                {provide: RequestOptions, useClass: ExtendedRequestOptions},
            ],
        };
    }
}
