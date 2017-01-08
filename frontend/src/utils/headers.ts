import { BaseRequestOptions } from "@angular/http";

/**
 * Extended RequestOptions to add a content-type and Accept header automatically
 * to each request.
 */
export class ExtendedRequestOptions extends BaseRequestOptions {
    constructor() {
        super();
        this.headers.append("Content-Type", "application/json");
        this.headers.append("Accept", "application/json");
    }
}
