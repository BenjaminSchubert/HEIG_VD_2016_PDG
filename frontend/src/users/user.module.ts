import { NgModule } from "@angular/core";
import { UtilsModule } from "../utils/utils.module";
import { UserService } from "./user.service";
import { UserComponent } from "./user.component";


/**
 * This module contains components to manage users.
 */
@NgModule({
    declarations: [UserComponent],
    imports: [UtilsModule],
    providers: [UserService],
})
export class UserModule {
}
