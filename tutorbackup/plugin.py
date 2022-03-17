from glob import glob
import os
from shutil import make_archive

import pkg_resources
import click
from tutor import config as tutor_config
from tutor.commands import compose
from tutor.commands.local import local as local_command_group


templates = pkg_resources.resource_filename(
    "tutorbackup", "templates"
)

config = {}

hooks = {}


@local_command_group.command(help="Back up MySQL, MongoDB, and Caddy")
@click.pass_context
def backup(context):
    config = tutor_config.load(context.obj.root)

    context.invoke(
        compose.execute,
        args=[
            "mysql",
            "bash",
            "-e",
            "-c",
            f"mysqldump --all-databases -u {config['MYSQL_ROOT_USERNAME']} --password='{config['MYSQL_ROOT_PASSWORD']}' > /var/lib/mysql/dump.sql",  # noqa: E501
        ]
    )
    click.echo(f"Backed up MySQL to {context.obj.root}/data/mysql/dump.sql")

    context.invoke(
        compose.execute,
        args=[
            "mongodb",
            "mongodump",
            "--out=/data/db/dump.mongodb",
        ],
    )
    click.echo(f"Backed up MongoDB to {context.obj.root}/data/mongodb/dump.mongodb")

    make_archive('mybackup', 'zip', os.path.abspath(context.obj.root))


def patches():
    all_patches = {}
    patches_dir = pkg_resources.resource_filename(
        "tutorbackup", "patches"
    )
    for path in glob(os.path.join(patches_dir, "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
