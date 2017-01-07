import { platformBrowser } from '@angular/platform-browser';
import { enableProdMode } from '@angular/core';

import { RadyAppModuleNgFactory } from './app.module.ngfactory';

enableProdMode();
platformBrowser().bootstrapModuleFactory(RadyAppModuleNgFactory);
