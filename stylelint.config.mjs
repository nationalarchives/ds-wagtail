import data from "./node_modules/@nationalarchives/frontend/config/stylelint.config.js";

data.ignoreFiles = [
  "app/**/*.css",
  "templates/static/css/**/*.css",
  "templates/static/cookie-consent/**/*.css",
  "sass/tna-toolkit/**/*.scss",
];

export default data;
