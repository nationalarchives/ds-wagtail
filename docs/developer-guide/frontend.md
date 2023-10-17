# Frontend development

## Follow the development guide

To ensure we are working in a way that is compatible with the front end technology aspects of the [GOV.UK Service Manual](https://www.gov.uk/service-manual/technology).

There are currently two guides for front-end development, as the content is in the process of being moved across. The original **[front end development guide](https://github.com/nationalarchives/front-end-development-guide)** on GitHub has lots of useful advice, but is in the process of moving to **The National Archives [developer handbook](https://nationalarchives.github.io/developer-handbook/technology/)**. Following these guides will ensure user interfaces are robust, inclusive and meet relevant regulations.

If there are any contradictions between the two, the [developer handbook](https://nationalarchives.github.io/developer-handbook/technology/) is the one that should be followed.

If you have any questions about any aspect of frontend development seek advice from the Lead Frontend Developer or another Frontend Developer.

## Setting up the front end development environment

There are two ways to develop the frontend; through the `dev` container or on the host machine.

### Dev container

`fab dev` will get you into the command line for the `dev` container.

From here you have a few commands you can use:

- `build` - Compile all the application JavaScript and CSS
- `build-js` - Compile the application JavaScript
- `build-css` - Compile the application CSS
- `dev` - Compile the application JavaScript and CSS and watch for changes (runs in the background)
- `dev-js` - Compile the application JavaScript and watch for changes
- `dev-css` - Compile the application CSS and watch for changes

### Host machine

#### Setup

1. Install [nvm](https://github.com/nvm-sh/nvm) (Node version manager)
1. Run `nvm use` to pick up the version of NodeJS defined in `.nvmrc`. If prompted, run  `nvm install` to install it first.
1. Run `npm install` to install the project dependencies

#### Use

You can now run one of the following commands:

- `npm run compile` - Compile all the application JavaScript and CSS
- `npm run compile:js` - Compile the application JavaScript
- `npm run compile:css` - Compile the application CSS
- `npm run dev:js` - Compile the application JavaScript and watch for changes
- `npm run dev:css` - Compile the application CSS and watch for changes

## Working with SASS/CSS

To modify styles, navigate to the `sass` folder in your editor.

## Working with JavaScript

Webpack is used for JavaScript module bundling with entry points and outputs defined within `webpack.config.js`.

When defining new entry points remember to avoid, where possible, sending JavaScript to a given page where it is not required.

### JavaScript testing

Jest is used for JavaScript testing. Tests should be added as siblings of the target file and given the same name with a `.test.js` suffix.

Let's aim for 100% coverage. Where necessary Jest can be set to run in a browser-like environment by setting the Jest environment to `jsdom` via a docblock at the top of the file.

Run Jest unit tests with `npm run test`
