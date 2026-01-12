# Botflow

Botflow is a lightweight Python framework for building automation workflows and bots with a focus on simplicity, modularity, and ease of integration.

## Features

- **Workflow Management**: Define complex bot workflows with simple, declarative syntax
- **Multi-language Support**: Built-in i18n support with locale management
- **Resource Management**: Centralized handling of styles, assets, and locales
- **Bundle Support**: PyInstaller integration for creating standalone executables
- **Qt Integration**: PySide6 support for GUI-based automation
- **Configuration**: Flexible runtime configuration with environment variables

## Quick Start

1. Install Botflow via pip:

    ```bash
    pip install botflow-gui
    ```

2. Create a simple bot workflow:

    ```python
    from botflow import FlowManager, FlowSpec, TextStepSpec, run_application, run_flow_manager

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

3. (Optional) If you want to customize the resources directory or language, set the following environment variables in your script before importing Botflow:

    ```python
    import os

    os.environ['BOTFLOW_RESOURCES_DIR'] = './custom_resources'
    os.environ['BOTFLOW_LANG'] = 'en_US'
    ```

    - When you use your own resources directory, Botflow will look for styles, locales, and other assets in the specified path and after that in the default package resources. So you can replace the default resources by providing your own.

        ```python
        from botflow.resolver import find_resource_file

        resource_path = find_resource_file('styles/flow_manager.qss')
        ```

4. Run your bot:

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

3. If you are using your own resources (like styles, locales, etc.), make sure to include them in the spec file. You can modify the `datas` section of the spec file to include your resources directory:

    ```bash
    pyinstaller your_bot_script.py --add-data "path/to/your/resources:resources"
    ```

4. If you want to specify a custom resources directory for your bundle, you can set the `BUNDLE_RESOURCES_DIR` variable in your main script (If you don't set it, it defaults to 'BOTFLOW_RESOURCES_DIR' path if set):

    ```python
    os.environ['BOTFLOW_BUNDLE_RESOURCES_DIR'] = './custom_resources'
    ```

