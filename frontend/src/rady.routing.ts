import { Routes, RouterModule } from "@angular/router";
import { StatsComponent } from "./stats/stats.component";
import { LoginComponent } from "./auth/login.component";
import { LogoutGuard, LoginGuard } from "./auth/guards/login.guard";


/**
 * Defines routes for the Rady application.
 */
const routes: Routes = [
    {
        children: [
            {
                canActivate: [LoginGuard],
                component: StatsComponent,
                path: "stats",

            },
            {
                canActivate: [LogoutGuard],
                component: LoginComponent,
                path: "login",
            },
            {
                path: "",
                pathMatch: "full",
                redirectTo: "stats",
            },
        ],
        path: "",
    },
    {path: "**", redirectTo: ""},
];


/**
 * Export routes for the main application.
 */
export const routing = RouterModule.forRoot(routes);
