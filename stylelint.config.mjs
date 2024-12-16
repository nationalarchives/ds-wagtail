import data from "./node_modules/@nationalarchives/frontend/config/stylelint.config.js";

data.ignoreFiles = [
  "app/**/*",
  "static/css/dist/**/*",
  "templates/static/css/**/*",
  "templates/static/cookie-consent/**/*",
  "static/cookie-consent/**/*",
  "sass/tna-toolkit/**/*.scss",
  "static/admin/css/**/*",
  "static/table_block/css/vendor/**/*",
  "static/rest_framework/**/*",
  "static/wagtailadmin/css/**/*",
];

export default data;
