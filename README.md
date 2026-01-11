# Botflow

Botflow is a lightweight Python framework for building automation workflows and bots with a focus on simplicity, modularity, and ease of integration.

## Features

- **Workflow Management**: Define complex bot workflows with simple, declarative syntax
- **Multi-language Support**: Built-in i18n support with locale management
- **Resource Management**: Centralized handling of themes, assets, and locales
- **Bundle Support**: PyInstaller integration for creating standalone executables
- **Qt Integration**: PySide6 support for GUI-based automation
- **Configuration**: Flexible runtime configuration with environment variables

## Quick Start

1. Install Botflow via pip:

   ```bash
   pip install botflow
   ```

2. Create a simple bot workflow:

   ```python
   from botflow import run_application, run_flow_manager, FlowManager, TextStepSpec, FlowSpec

    RESOURCES_DIR = 'resources'


    async def greet_user(ctx):
        name = ctx.data.get('greet_step')
        ctx.logger.info(f'Hello, {name}!')


    flow = FlowSpec(
        name='simple_flow',
        steps=[
            TextStepSpec(
                key='greet_step',
                title='Greet User',
                placeholder='Enter your name',
            ),
        ],
        on_finish=[greet_user]
    )


    if __name__ == '__main__':
        run_application()
        flow_manager = FlowManager(flow)
        run_flow_manager(flow_manager, window_title='Simple Flow Manager')
    ```

3. Run your bot:

    ```bash
    python your_bot_script.py
    ```

## How to create a bundle

To create a standalone executable bundle of your Botflow application, you can use PyInstaller. Follow these steps:

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Create a spec file for your application. You can generate a default spec file using:

   ```bash
   pyinstaller your_bot_script.py
   ```

3. If you are using your own resources (like themes, locales, etc.), make sure to include them in the spec file. You can modify the `datas` section of the spec file to include your resources directory:

   ```bash
   pyinstaller your_bot_script.py --add-data "path/to/your/resources:resources"
   ```

4. If you want to specify a custom resources directory for your bundle, you can set the `BUNDLE_RESOURCES_DIR` variable in your main script:

   ```python
   BUNDLE_RESOURCES_DIR = 'path/to/your/bundle/resources'
   ```

