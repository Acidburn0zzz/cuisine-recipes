from cuisine import *


def ufw():
    """Configure and enable ufw (uncomplicated firewall)"""
    package_ensure('ufw')

    status = sudo('ufw status | head -1')

    if 'inactive' in status:
        with mode_sudo():
            file_update(
                '/etc/default/ufw',
                lambda _: 'IPV6=no' if _ == 'IPV6=yes' else _
            )
        sudo('ufw allow ssh')
        sudo('ufw allow http')
        sudo('ufw allow https')
        sudo('ufw --force enable')


def iptables():
    """Configure iptables. Depending on your tastes, you may prefer using ufw/"""
    # https://help.ubuntu.com/community/IptablesHowTo
    # https://www.digitalocean.com/community/articles/how-to-set-up-a-firewall-using-ip-tables-on-ubuntu-12-04
    status = sudo('iptables -L | grep ssh')
    if 'ssh' not in status:
        sudo('iptables -A INPUT -p tcp --dport ssh -j ACCEPT')
        sudo('iptables -A INPUT -p tcp --dport 80 -j ACCEPT')
        sudo('iptables -A INPUT -p tcp --dport 443 -j ACCEPT')
        sudo('iptables -A INPUT -j DROP')
        sudo('iptables -I INPUT 1 -i lo -j ACCEPT')
        sudo('iptables-save > /etc/iptables.rules')

        iptablesload = '/etc/network/if-pre-up.d/iptablesload'
        file_upload(iptablesload, './files/iptables/iptablesload.txt')
        file_ensure(iptablesload, owner='root', group='root', mode=755)

        iptablessave = '/etc/network/if-post-down.d/iptablessave'
        file_upload(iptablessave, './files/iptalbes/iptablessave.txt')
        file_ensure(iptablessave, owner='root', group='root', mode=755)


