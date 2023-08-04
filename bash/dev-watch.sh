#!/bin/bash

. $HOME/.nvm/nvm.sh
nvm install
nvm use
npm install
npm run dev:css &
npm run dev:js &
