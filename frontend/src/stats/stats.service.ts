import { Observable } from "rxjs/Observable";
import { Injectable } from "@angular/core";
import { Http } from "@angular/http";
import { IStatistics } from "./stubs";
import { STATS_URL } from "../api.routes";
import { RestService } from "../base/rest.service";


/**
 * This is a service that allows to fetch statistics
 */
@Injectable()
export class StatisticsService extends RestService<IStatistics> {
    constructor(http: Http) {
        super(STATS_URL, http);
        let updateInterval = 1000 * 60 * 5; // Update every 5 minutes
        Observable.timer(updateInterval, updateInterval).subscribe(() => this.fetch());
    }
}
