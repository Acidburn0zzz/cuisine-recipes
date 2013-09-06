from cuisine import *

from recipes import ssh


def version():
    """Print the OS version. For testing purpose."""

    # switch to plain password ssh auth for root
    ssh.use_root_password()

    version = run('cat /proc/version')
    print version


def create_user():
    """Create the ubuntu user. Add them to sudoer."""

    # switch to root plain password ssh
    ssh.use_root_password()

    # ubuntu user
    user_ensure(name='ubuntu', home='/home/ubuntu', shell='/bin/bash')

    # sudoer
    file_update(
        '/etc/sudoers',
        lambda _: text_ensure_line(
            _,
            "%ubuntu ALL=(ALL) NOPASSWD:ALL")
    )


def scramble_password():
    # TODO
    return


def fix_locales():
    """Fix locales to avoid nasty warning messages on upgrades/install."""
    # for ubuntu user
    locale_ensure('en_US.UTF-8')

    # do it again for root :/
    with mode_sudo():
        locale_ensure('en_US.UTF-8')

    return

    # above is ok but errors may still be emitted - you can do it the hard way (not tested):
    path = '/etc/default/locale'
    if not text_get_line(path, 'LC_ALL=en_US.UTF-8'):
        # Add lines
        file_update(
            path,
            lambda _:text_ensure_line(_,
            'LC_ALL="en_US.UTF-8"',
            'LANG="en_US.UTF-8"',
            'LANGUAGE="en_US.UTF-8"')
        )

        # Configure
        sudo('dpkg-reconfigure locales')
        sudo('locale-gen en_US.UTF-8')


def automatic_updates():
    # TODO automatic updates
    return


def scripts():
    """Deploy user scripts."""
    package_ensure('unzip')

    deploy_script = '/home/ubuntu/deploy.sh'
    file_upload(deploy_script, './files/scripts/deploy.sh')
    file_ensure(location=deploy_script, mode=700)

    # Note: script should copy backup to remote host
    backup_script = '/home/ubuntu/backup.sh'
    file_upload(backup_script, './files/scripts/backup.sh')
    file_ensure(location=backup_script, mode=700)
    dir_ensure('/home/ubuntu/backups', mode=700)
