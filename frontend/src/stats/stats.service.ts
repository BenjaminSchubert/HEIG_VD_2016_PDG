import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { IStatistics } from "./stubs";
import { STATS_URL } from "../api.routes";


/**
 * This is a service that allows to fetch statistics
 */
@Injectable()
export class StatisticsService {
    /**
     * Observable of the statistics
     */
    public $: Observable<IStatistics>;

    private _$: BehaviorSubject<IStatistics>;

    constructor(private http: Http) {
        this._$ = new BehaviorSubject(null);
        this.$ = this._$.asObservable();
        this.fetch();
    }

    private fetch(): void {
        this.http.get(STATS_URL).subscribe((res: Response) => this._$.next(res.json()));
    }
}
