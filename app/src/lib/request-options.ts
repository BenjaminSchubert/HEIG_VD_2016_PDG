import { Injectable } from "@angular/core";
import { BaseRequestOptions, Headers } from "@angular/http";

@Injectable()
export class ExtendedRequestOptions extends BaseRequestOptions {
    constructor() {
        super();
        if (this.headers === null) {
            this.headers = new Headers();
        }
        this.headers.append("Content-Type", "application/json");
        this.headers.append("Accept", "application/json");
    }
}
