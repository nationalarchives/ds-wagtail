#!/bin/bash

chmod +x -fR /home/app/.local/bin/dev
echo "export PATH=\"/home/app/.local/bin/dev:\$PATH\"\n$(cat ~/.bashrc)" > ~/.bashrc

mkdir -p /app/templates/static/assets
cp -R /app/node_modules/@nationalarchives/frontend/nationalarchives/assets/* /app/templates/static/assets

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

alias dj="python manage.py"
alias djrun="python manage.py runserver 0.0.0.0:8000"
alias djtest="python manage.py test --settings=config.settings.dev"

poetry run python /app/manage.py migrate
poetry run python /app/manage.py createsuperuser --no-input
poetry run python /app/manage.py runserver 0.0.0.0:8080
