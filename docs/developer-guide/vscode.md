# Working with VS Code

[VSCode](https://code.visualstudio.com/) is a great editor, but due to the way project is set up, getting richer editor integration requires some hoop-jumping. Because projects are run under Docker, VSCode doesn't simply have access to the Python virtual environment, so some very useful features are disabled.

!!! warning
The following steps require the official VSCode distribution, rather than offshoots like [VSCodium](https://vscodium.com/).

## Virtual environment integration

The VSCode integration with Docker requires the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This extension allows VSCode to install itself inside a container, and thus access its filesystem and virtual environments.

When opening a project with a dev container configuration, VSCode will prompt you whether you want to switch to it. To switch manually, open the command palette and select "Remote Containers - Reopen in Container". This will reload your VSCode window, build and then start the project containers. Once it's finished, you'll be presented with a regular-looking VSCode editor, but with the Python integration correctly installed and configured. Should you make any changes to the dev container configuration or `Dockerfile`, you'll want to use "Remote Containers - Rebuild and Reopen in Container" instead.

To install additional extensions into the container automatically, add its id to `defaultExtensions` in your VSCode settings.

## Debugger

Now that VSCode has full access to your project and virtual environment, it's time for the main event: the debugger! VSCode's debugger allows you to set breakpoints and step through code, all on your running Django application.

At the top of the "Run and Debug" tab should now be a green triangle. Click it to start debugging. This will start the Django development server in a new terminal tab showing the logs. For more about the debugger, [read the docs](https://code.visualstudio.com/Docs/editor/debugging).
