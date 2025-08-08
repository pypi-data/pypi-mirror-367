import click

from arm_cli.container.container import container
from arm_cli.self.self import self
from arm_cli.system.system import system


@click.version_option()
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """Experimental CLI for deploying robotic applications"""
    pass


# Add command groups
cli.add_command(container)
cli.add_command(self)
cli.add_command(system)

if __name__ == "__main__":
    cli()
