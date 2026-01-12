import os

from botflow import FlowManager, FlowSpec, TextStepSpec, run_application, run_flow_manager

os.environ['BOTFLOW_RESOURCES_DIR'] = './resources'
os.environ['BOTFLOW_LANG'] = 'en_US'


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
