import { platformBrowser } from "@angular/platform-browser";
import { enableProdMode } from "@angular/core";
import { RadyModuleNgFactory } from "../compiled/src/rady.module.ngfactory";


if (process.env.ENV === "production") {
    // Production
    enableProdMode();
}

/**
 * Bootstraps the application
 */
platformBrowser().bootstrapModuleFactory(RadyModuleNgFactory).then(() => {
    let loading = document.getElementById("loading-screen");

    if (loading === null) { return; }

    function cleanup() {
        document.styleSheets[0].disabled = true;

        if (loading !== null) {
            loading.remove();
        }
    }

    loading.addEventListener("webkitTransitionEnd", cleanup, false);
    loading.addEventListener("oTransitionEnd", cleanup, false);
    loading.addEventListener("transitionend", cleanup, false);
    loading.addEventListener("msTransitionEnd", cleanup, false);

    loading.classList.add("hidden");
});
