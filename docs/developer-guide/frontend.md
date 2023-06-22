# Frontend development

## Follow the development guide

To ensure we are working in a way that is compatible with the front end technology aspects of the [GOV.UK Service Manual](https://www.gov.uk/service-manual/technology) **all front end development should follow The National Archives [front end development guide](https://github.com/nationalarchives/front-end-development-guide)** on GitHub. This will ensure user interfaces are robust, inclusive and meet relevant regulations. 

If you have any questions about any aspect of frontend development seek advice from the Lead Frontend Developer or another Frontend Developer.

## Setting up the front end development environment

### Working with SASS/CSS

- Ensure you have NodeJS & NPM installed.
```
    npm install 
```
- To watch and build the public facing site and wagtail editor SASS, run `npm run compile:css`
- To modify styles, navigate to the `sass` folder in your editor.

### Working with JavaScript

Webpack is used for JavaScript module bundling with entry points and outputs defined within `webpack.config.js`. When defining new
entry points remember to avoid, where possible, sending JavaScript to a given page where it is not required.

- Install dependencies with `npm install`
    - _For development_: Kick off a Webpack watch task with `npm start`. This will produce development assets (by overriding the production mode set in `webpack.config.js`).
    - _For production_: bundle assets with `npx webpack --config webpack.config.js`

### JavaScript testing

Jest is used for JavaScript testing. Tests should be added as siblings of the target file and given the same name with a `.test.js` suffix. Let's aim for 100% coverage. Where necessary Jest can be set to run in a browser-like environment by setting the Jest environment to `jsdom` via a docblock at the top of the file.

- Run Jest unit tests with `npm test`