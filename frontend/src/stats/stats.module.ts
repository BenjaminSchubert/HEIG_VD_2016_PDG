import { NgModule } from "@angular/core";
import { StatsComponent } from "./stats.component";
import { UtilsModule } from "../utils/utils.module";
import { StatisticsService } from "./stats.service";


/**
 * This module contains components to display statistics.
 */
@NgModule({
    declarations: [StatsComponent],
    imports: [UtilsModule],
    providers: [StatisticsService],
})
export class StatsModule {
}
