const path = require("path");
const webpack = require('webpack');
const ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = function(projectRoot, appConfig) {
    return {
        devtool: "eval-cheap-module-source-map",

        plugins: [
            new webpack.DefinePlugin({
                'process.env.NODE_ENV': JSON.stringify('development')
            }),

            new ExtractTextPlugin("style.css"),
        ],

        output: {
          path: path.resolve(projectRoot, appConfig.outDir),
          filename: '[name].js',
          sourceMapFilename: '[name].map',
        },
    }
};
