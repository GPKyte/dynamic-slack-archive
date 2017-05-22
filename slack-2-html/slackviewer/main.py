import os
import click
import shutil
import slackviewer

from jinja2 import \
    Environment, \
    PackageLoader, \
    select_autoescape

from slackviewer.archive import \
    extract_archive, \
    get_users, \
    get_channels, \
    compile_channels


def envvar(name, default):
    """Create callable environment variable getter

    :param str name: Name of environment variable
    :param default: Default value to return in case it isn't defined
    """
    return lambda: os.environ.get(name, default)


def flag_ennvar(name):
    return os.environ.get(name) == '1'


@click.command()
@click.option("-z", "--archive", type=click.Path(), required=True,
              default=envvar('SEV_ARCHIVE', ''))
def main(archive):
    if not archive:
        raise ValueError("Empty path provided for archive")

    arch_path = extract_archive(archive)
    user_data = get_users(arch_path)
    channel_data = get_channels(arch_path)
    channels = compile_channels(arch_path, user_data, channel_data)

    path = os.path.join(os.path.split(arch_path)[0], 'archive-webview')
    if not os.path.isdir(path):
        os.makedirs(path)
    env = Environment(loader = PackageLoader('slackviewer', 'templates'),
                      autoescape=select_autoescape(['html', 'xml']))
    css_src = os.path.join(slackviewer.__path__[0], "templates/viewer.css")
    css_des = os.path.join(path, 'viewer.css')
    shutil.copy2(css_src, css_des)

    template = env.get_template('viewer.html')
    for name in sorted(channels):
        page = template.render(messages=channels[name],
                               channels=sorted(channels.keys()),
                               name=name)
        channel_file = "{}.html".format(os.path.join(path, name))
        with open(channel_file, "w") as file:
            file.write(page.encode('ascii', 'ignore'))
    print ("Finished creating web files for archive")
