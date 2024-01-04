module.exports = {
    env: {
        browser: true,
        es2021: true,
        jquery: true,
        jest: true,
    },
    plugins: ["react"],
    extends: [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
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
        ecmaFeatures: {
            jsx: true
        }
    },
    rules: {},
    settings: {
        react: {
            version: "detect"
        }
    }
};
