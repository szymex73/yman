from time import sleep

import click
import json
import os
from click.shell_completion import CompletionItem
from click.types import ParamType

from .procfs import Process
from .yakuake import Yakuake

APP_NAME = 'yman'


class Config:
    def __init__(self):
        self.yakuake = Yakuake()
        self.conf_dir = click.get_app_dir(APP_NAME)
        self.session_dir = os.path.join(self.conf_dir, 'sessions')

        self.session_names = []

        self.env = self._dump_environ()

        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)

        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)

    @staticmethod
    def _dump_environ():
        return Process(os.getpid()).env

    def load_sessions(self):
        for fn in os.listdir(self.session_dir):
            if not fn.endswith('.json'):
                continue
            self.session_names.append(fn.replace('.json', ''))


def diff_env(base_env: dict[str, str], new_env: dict[str, str]):
    return {k: v for k, v in new_env.items() if k not in base_env}


pass_config = click.make_pass_decorator(Config, ensure=True)


class SessionNameType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        if not ctx.obj:
            ctx.obj = Config()
            ctx.obj.load_sessions()
        return [
            CompletionItem(name) for name in ctx.obj.session_names
        ]


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Config()
    ctx.obj.load_sessions()


@cli.command()
@click.argument('name')
@click.option('--skip/--keep', default=True, help="include the tab yman is ran from")
@pass_config
def store(ctx: Config, name: str, skip: bool):
    """
    Store the currently running sessions
    """
    if os.path.exists(os.path.join(ctx.session_dir, f'{name}.json')):
        click.echo(f'Session named {name} already exists', err=True)
        exit(1)

    click.echo(f'Storing current session as {name} (skipping current terminal: {"yes" if skip else "no"})')

    session_data = {
        "tabs": []
    }

    tabs = ctx.yakuake.get_tab_session_map(skip)
    for tab_id, session_id in tabs.items():
        session = ctx.yakuake.get_session(session_id)

        # Workaround for when there isn't a child process running in the shell and we want to dump the environment
        no_cmd = False
        if session.pid == session.fg_pid:
            session.send_text('sleep 1\n')
            sleep(0.05)  # Wait a bit for the process to start running
            no_cmd = True

        proc = Process(session.fg_pid)

        # Small workaround for when the session is running yman
        if len(proc.cmdline) > 1:
            if proc.cmdline[1][-4:] == 'yman':
                no_cmd = True

        session_data['tabs'].append({
            'title': session.title,
            'dir': proc.cwd,
            'index': tab_id,
            'command': '' if no_cmd else proc.cmdline,
            'env': diff_env(ctx.env, proc.env)
        })

    f = open(os.path.join(ctx.session_dir, f'{name}.json'), 'w')
    f.write(json.dumps(session_data))
    f.close()
    click.echo(f'Successfully stored current session as {name}')


@cli.command()
@click.argument('name', type=SessionNameType())
@pass_config
def restore(ctx: Config, name: str):
    """
    Restore saved sessions
    """
    if not os.path.exists(os.path.join(ctx.session_dir, f'{name}.json')):
        click.echo(f'Session named {name} does not exist', err=True)
        exit(1)

    click.echo(f'Restoring session {name}')

    curr_session = ctx.yakuake.get_current_session_id()

    session_data = json.load(open(os.path.join(ctx.session_dir, f'{name}.json'), 'r'))
    for tab_data in sorted(session_data['tabs'], key=lambda x: x['index']):
        ctx.yakuake.start_terminal(
            title=tab_data['title'],
            directory=tab_data['dir'],
            command=' '.join(tab_data['command']),
            env=tab_data['env']
        )

    ctx.yakuake.raise_session(curr_session)


@cli.command('list')
@pass_config
def list_sessions(ctx: Config):
    """
    List saved sessions
    """
    click.echo('Saved sessions:')
    for session_name in ctx.session_names:
        click.echo(f'- {session_name}')


@cli.command()
@click.argument('name', type=SessionNameType())
@pass_config
def remove(ctx: Config, name: str):
    """
    Remove saved sessions
    """
    if not os.path.exists(os.path.join(ctx.session_dir, f'{name}.json')):
        click.echo(f'Session named {name} does not exist', err=True)
        exit(1)

    if click.confirm(f'Are you sure you want to remove session {name}?', abort=True, default=False):
        os.remove(os.path.join(ctx.session_dir, f'{name}.json'))


if __name__ == '__main__':
    cli()
