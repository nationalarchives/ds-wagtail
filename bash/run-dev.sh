#!/bin/bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install
npm install
npm run dev:css &
npm run dev:js &
poetry run python manage.py collectstatic --no-input
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000