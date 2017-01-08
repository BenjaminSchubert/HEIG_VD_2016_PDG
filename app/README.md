# Rady mobile app

Follow these steps to have a clean install:
- `npm uninstall -g ionic cordova && npm cache clean && npm install -g ionic cordova`
- `rm -rf node_modules/ && npm install`
- `ionic state reset`

Follow these steps to run the app:
- `ionic run android --device --prod`