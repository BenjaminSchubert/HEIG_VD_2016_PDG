import { NgModule, ModuleWithProviders } from "@angular/core";
import { LoginComponent } from "./login.component";
import { UtilsModule } from "../utils/utils.module";
import { AccountService } from "./account.service";
import { LoginGuard, LogoutGuard } from "./guards/login.guard";


/**
 * This module provides authentication-related utilities.
 *
 * It gives two guards to make sure the current user is logged in, respectively logged out.
 * It provides a view to allow for login of the user.
 * It provides a service to handle authentication.
 */
@NgModule({
    declarations: [LoginComponent],
    exports: [LoginComponent],
    imports: [UtilsModule],
})
export class AuthModule {
    public static forRoot(): ModuleWithProviders {
        return {
            ngModule: AuthModule,
            providers: [
                AccountService, LoginGuard, LogoutGuard,
            ],
        };
    }
}
