const path = require("path");

module.exports = {
    mode: "production",
    entry: {
        beta_banner: "./scripts/src/beta-banner.js",
        cookie_consent: "./scripts/src/ds-cookie-consent.js",
        gtm_script: "./scripts/src/gtm-script.js",
        image_viewer: "./scripts/src/image-viewer.js",
        home_page: "./scripts/src/home-page.js",
        explorer: "./scripts/src/explorer.js",
        article: "./scripts/src/article.js",
        article_index_page: "./scripts/src/article-index-page.js",
        image_browse: "./scripts/src/image-browse.js",
        details: "./scripts/src/details.js",
        sign_in: "./scripts/src/sign-in.js",
        global_search: "./scripts/src/global-search.js",
        catalogue_search: "./scripts/src/catalogue-search.js",
        hamburger_menu: "./scripts/src/hamburger-menu.js",
        record_article_page: "./scripts/src/record-article-page.js",
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "templates/static/scripts"),
    },
    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["@babel/preset-env"],
                    },
                },
            },
        ],
    },
    target: ["web", "es5"],
};
