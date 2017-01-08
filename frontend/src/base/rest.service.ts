import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { Http, Response } from "@angular/http";


/**
 * This base service class allows to retrieve data from a server and dispatch it.
 */
export abstract class RestService<T> {
    /**
     * Observable of the data we get from the server
     */
    public $: Observable<T>;

    protected _$: BehaviorSubject<T>;
    protected data: T;

    constructor(protected URL: string, protected http: Http) {
        this._$ = new BehaviorSubject(null);
        this.$ = this._$.asObservable();
        this.fetch();
    }

    /**
     * Fetch the service's data and make it available through $
     */
    protected fetch(): void {
        this.http.get(this.URL).subscribe((res: Response) => {
            this.data = res.json();
            this._$.next(this.data);
        });
    }
}
