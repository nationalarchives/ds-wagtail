module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    extends: ["eslint:recommended"],
    overrides: [
        {
            env: {
                node: true,
            },
            files: [".eslintrc.{js,cjs}"],
            parserOptions: {
                sourceType: "script",
            },
        },
    ],
    parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
    },
    rules: {},
    ignorePatterns: [
        "templates/static/scripts/**/*.js",
        ".*.js",
        "*.test.js",
        "*.config.js",
        "static",
    ],
};
