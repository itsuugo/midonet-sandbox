# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
from datetime import datetime

import humanize
from docopt import docopt
from tabulate import tabulate
from midonet_sandbox.assets.assets import BASE_ASSETS_PATH, Assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.composer import Composer
from midonet_sandbox.utils import configure_logging
from midonet_sandbox.wrappers.docker_wrapper import Docker

cli = """Midonet Sandbox Manager

Usage:
    sandbox-manage [options] build <image>... [--publish]
    sandbox-manage [options] run <flavour> --name=<name> [--override=<override>]
    sandbox-manage [options] stop <name> [--remove]
    sandbox-manage [options] flavours-list [--details]
    sandbox-manage [options] images-list
    sandbox-manage [options] sandbox-list [--details]

Options:
    -h --help                       show this screen
    -l <level>, --log=<level>       verbose mode [default: INFO]
    -c <config>, --config=<config>  configuration file [default: ~/.midonet-sandboxrc]
"""

_ACTIONS_ = (
    'build', 'run', 'stop', 'flavours-list', 'images-list', 'sandbox-list')

log = logging.getLogger('midonet-sandbox.main')


def main():
    options = docopt(cli)

    configure_logging(options['--log'])
    Config.instance(options['--config'])

    log.debug('Base assets directory: {}'.format(BASE_ASSETS_PATH))

    for action in _ACTIONS_:
        if options[action]:
            action = action.replace('-', '_')
            globals()[action](options)
            break


def build(options):
    images = options['<image>']
    publish = options['--publish']

    for image in images:
        if ':' not in image:
            image = '{}:master'.format(image)

        Builder().build(image, publish)


def flavours_list(options):
    assets = Assets()
    details = options['--details']

    flavours = list()
    for flavour in assets.list_flavours():
        if details:
            components = assets.get_components_by_flavour(flavour)
            flavours.append([flavour, components])
        else:
            flavours.append([flavour])

    headers = ['Flavours']
    if details:
        headers = ['Flavours', 'Components']

    print(tabulate(flavours, headers=headers, tablefmt='psql'))


def run(options):
    flavour = options['<flavour>']
    name = options['--name']

    Composer().run(flavour, name)
    sandbox_list({'--details':True})


def stop(options):
    name = options['<name>']
    remove = options['--remove']

    Composer().stop(name, remove)


def images_list(options):
    docker = Docker(Config.instance_or_die().get_default_value('docker_socket'))
    images = list()

    for image in docker.list_images('sandbox/'):
        images.append([','.join(image['RepoTags']),
                       humanize.naturaltime(
                           datetime.now() -
                           datetime.fromtimestamp(image['Created']))])

    print(tabulate(images, headers=['Image', 'Created'], tablefmt='psql'))


def sandbox_list(options):
    details = options['--details']

    sandboxes = list()
    for sandbox in Composer().list_running_sandbox():
        if details:
            for container in Composer().get_sandbox_detail(sandbox):
                sandboxes.append(container)
        else:
            sandboxes.append([sandbox])

    headers = ['Sandbox']
    if details:
        headers = ['Sandbox', 'Name', 'Image', 'Ports', 'Ip']

    print(tabulate(sandboxes, headers=headers, tablefmt='psql'))

