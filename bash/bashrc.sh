# Note: This file is loaded on all environments, even production.

alias dj="python manage.py"
alias djrun="python manage.py runserver 0.0.0.0:8000"
alias djtest="python manage.py test --settings=config.settings.dev"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
