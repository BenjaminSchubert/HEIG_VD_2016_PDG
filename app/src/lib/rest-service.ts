import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { Response } from "@angular/http";
import { AuthService } from "../providers/auth-service";


export class RestService<T> {
    public $: Observable<T>;
    private _$: BehaviorSubject<T>;

    constructor(protected http: AuthService, protected readonly url) {
        this._$ = new BehaviorSubject(null);
        this.$ = this._$.asObservable();
    }

    public fetch() {
        return this.http.get(this.url).do((res: Response) => this._$.next(res.json()));
    }

    public update(value: T) {
        return this.http
            .put(this.url, value)
            .do((res: Response) => this._$.next(res.json()));
    }
}
