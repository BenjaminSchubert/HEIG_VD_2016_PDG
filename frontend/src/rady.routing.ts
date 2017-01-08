import { Routes, RouterModule } from "@angular/router";
import { StatsComponent } from "./stats/stats.component";
import { LoginComponent } from "./auth/login.component";
import { LogoutGuard, AdminGuard } from "./auth/guards/login.guard";
import { UserComponent } from "./users/user.component";


/**
 * Defines routes for the Rady application.
 */
const routes: Routes = [
    {
        children: [
            {
                canActivate: [AdminGuard],
                component: UserComponent,
                path: "users",
            },
            {
                canActivate: [AdminGuard],
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
