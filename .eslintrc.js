module.exports = {
    env: {
        browser: true,
        es2021: true,
        jquery: true,
        jest: true,
    },
    extends: ["eslint:recommended"],
    overrides: [
        {
            env: {
                node: true,
            },
            files: [".eslintrc.{js}"],
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
};
