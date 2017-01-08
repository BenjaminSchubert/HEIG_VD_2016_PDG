import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { UtilsModule } from "./utils/utils.module";
import { AuthModule } from "./auth/auth.module";
import { RadyComponent } from "./rady.component";
import { routing } from "./rady.routing";
import { StatsModule } from "./stats/stats.module";
import { UserModule } from "./users/user.module";


/**
 * Main module for the Rady Frontend
 */
@NgModule({
    bootstrap: [RadyComponent],
    declarations: [RadyComponent],
    imports: [
        BrowserModule, routing,
        UtilsModule.forRoot(),
        AuthModule.forRoot(),
        StatsModule,
        UserModule,
    ],
})
export class RadyModule {
}
