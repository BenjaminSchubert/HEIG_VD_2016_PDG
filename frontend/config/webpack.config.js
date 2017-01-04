const path = require("path");
const webpackMerge = require("webpack-merge");

const getCommonConfig = require("./webpack.common");
const getDevConfig = require("./webpack.debug");
const getProdConfig = require("./webpack.prod");


const root = path.resolve(__dirname, "..");
const environment =
    process.env.NODE_ENV ? process.env.NODE_ENV : "development";


const appConfig = {
    outDir: path.join(root, "dist/"),
    index: "index.html",
    mainModule: "rady.module.ts#RadyModule",
    src: "src/",
    main: "main.ts",
    vendors: "vendors.ts",
    polyfills: "polyfills.ts",
    tsconfig: "tsconfig.json",
};


function getMixin() {
    switch (environment) {
        case "development": return getDevConfig(root, appConfig);
        case "production": return getProdConfig(root, appConfig);
        default: {
            throw new Error("Invalid build target:", environment);
        }
    }
}

var baseConfig = getCommonConfig(root, appConfig);

module.exports = webpackMerge(baseConfig, getMixin());
