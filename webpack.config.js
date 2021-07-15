const path = require('path');

module.exports = {
    mode: 'production',
    entry: {
        image_viewer: './scripts/src/image-viewer.js',
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'templates/static/scripts'),
    },
    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    }
};
