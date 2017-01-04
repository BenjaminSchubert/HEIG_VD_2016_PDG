/**
 * Polyfills needed by the application
 */

import "reflect-metadata";
import "zone.js/dist/zone";

if (process.env.ENV === "production") {
    // Production
} else {
    // Development
    Error["stackTraceLimit"] = Infinity;
    // tslint:disable-next-line: no-require-imports no-var-requires
    require("zone.js/dist/long-stack-trace-zone");
}
