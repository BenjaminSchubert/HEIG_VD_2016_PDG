const path = require("path");

const webpack = require("webpack");
const CompressionPlugin = require("compression-webpack-plugin");
const ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = function(projectRoot, appConfig) {
    return {
        devtool: "source-map",

        output: {
            path: path.resolve(projectRoot, appConfig.outDir),
            filename: '[name].[hash].js',
            sourceMapFilename: "[name].[hash].map",
        },

        plugins: [
            new webpack.DefinePlugin({
                'process.env.NODE_ENV': JSON.stringify('production')
            }),

            new ExtractTextPlugin("style.[hash].css"),

            new webpack.optimize.UglifyJsPlugin({
                mangle: { screw_ie8 : true },
                compress: { screw_ie8: true },
                sourceMap: true
            }),

            new CompressionPlugin({
                asset: '[path].gz[query]',
                algorithm: 'gzip',
                test: /\.(js|html|css|map)$/,
                threshold: 10240,
                minRatio: 0.8
            }),

            new webpack.LoaderOptionsPlugin({
                minimize: true,
                debug: false,
            })
        ]

    }
};
