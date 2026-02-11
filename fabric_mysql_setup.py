import os
import subprocess
import platform

RUN_LOCAL = os.environ.get('RUN_LOCAL', '0') == '1' or os.environ.get('FABRIC_HOST', '').lower() in ('', 'local')
SKIP_INSTALL = os.environ.get('SKIP_INSTALL', '0') == '1'
DB_NAME = 'igaime_db'
ENV = os.environ.copy()

if RUN_LOCAL:
    IS_MAC = platform.system() == 'Darwin'
    HOME = os.path.expanduser('~')
else:
    from fabric import Connection
    with open('password.txt') as f:
        password = f.read().strip()
    HOST = os.environ.get('FABRIC_HOST', '127.0.0.1')
    connection = Connection(host=HOST, user='igaime', connect_kwargs={'password': password})

    def _is_mac():
        r = connection.run('uname -s', hide=True)
        return r.stdout.strip() == 'Darwin'

    def _home():
        r = connection.run('echo $HOME', hide=True)
        return r.stdout.strip()

    IS_MAC = _is_mac()
    HOME = _home()


def _run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, env=ENV)
    if check and r.returncode != 0:
        raise SystemExit(r.returncode)
    return r.returncode == 0


def _mysql_installed():
    r = subprocess.run('which mysql', shell=True, capture_output=True, text=True, env=ENV)
    return r.returncode == 0


def install_mysql():
    if SKIP_INSTALL:
        print('SKIP_INSTALL=1, skipping MySQL install.')
        return
    if RUN_LOCAL:
        if IS_MAC:
            if _mysql_installed():
                print('MySQL already installed, skipping.')
            else:
                print('Installing MySQL via Homebrew (may take a few minutes)...')
                if not _run('brew install mysql', check=False):
                    print('Install failed (e.g. another brew process). Run manually: brew install mysql && brew services start mysql')
                elif not _run('brew services start mysql', check=False):
                    print('Start MySQL manually: brew services start mysql')
        else:
            _run('sudo apt-get update')
            _run('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server')
            _run('sudo systemctl start mysql')
            _run('sudo systemctl enable mysql')
    else:
        if IS_MAC:
            connection.run('brew update')
            connection.run('brew install mysql')
            connection.run('brew services start mysql')
        else:
            connection.sudo('apt-get update', password=password)
            connection.sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server', password=password)
            connection.sudo('systemctl start mysql', password=password)
            connection.sudo('systemctl enable mysql', password=password)


def create_database():
    if RUN_LOCAL and not _mysql_installed():
        print('MySQL not installed. Run: brew install mysql && brew services start mysql')
        print('Then run this script again (or with SKIP_INSTALL=1).')
        return
    cmd = f'mysql -e "CREATE DATABASE IF NOT EXISTS {DB_NAME};"'
    if RUN_LOCAL:
        if not _run(cmd, check=False):
            print('MySQL not running? Start it: brew services start mysql')
            return
    elif IS_MAC:
        connection.run(cmd)
    else:
        connection.sudo(cmd, password=password)


def run_dump():
    dump_path = f'{HOME}/dump.sql'
    if RUN_LOCAL and not os.path.isfile(dump_path):
        print(f'No {dump_path} found, skipping dump. Create the file to load it.')
        return
    if RUN_LOCAL and not _mysql_installed():
        return
    cmd = f'mysql {DB_NAME} < {dump_path}'
    if RUN_LOCAL:
        if not _run(cmd, check=False):
            print(f'Dump failed (check {dump_path} exists and MySQL is running).')
        return
    elif IS_MAC:
        connection.run(cmd)
    else:
        connection.sudo(cmd, password=password)


if __name__ == '__main__':
    install_mysql()
    create_database()
    run_dump()
    print('Done.')
