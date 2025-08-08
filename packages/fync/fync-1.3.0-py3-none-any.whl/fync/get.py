import argparse
import configparser
import getpass
import os
from pathlib import Path
import tempfile
import urllib
import urllib.parse
import urllib.request
import shutil

config = configparser.ConfigParser()
file_path = Path.home().joinpath('.fync-get')


def url_request(url, opener):
    urllib.request.install_opener(opener)
    try:
        temp_file = tempfile.NamedTemporaryFile(
            dir='.', prefix='fync_download_', delete=False
        )
        temp_filename = temp_file.name
        temp_file.close()

        temporary_filename, headers = urllib.request.urlretrieve(
            url, temp_file.name
        )
        filename = headers.get_filename()
        if not filename:
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)

        filename_to_use = filename
        postfix_num = 1
        while os.path.exists(filename_to_use):
            name, ext = os.path.splitext(filename)
            filename_to_use = f'{name}.{postfix_num}{ext}'
            postfix_num += 1

        shutil.move(temporary_filename, filename_to_use)
        return filename_to_use
    except urllib.error.URLError as e:
        print(f'Error downloading {url}: {e}')
    except PermissionError as e:
        print(f'Error Permission handling: {e}')
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    return None


def download_bearer(url, token):
    print('Download (Authorization Bearer) ..')
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', f'Bearer {token}')]
    result = url_request(url, opener)
    print(
        'Download (Authorization Bearer) '
        + (f"done: '{result}'" if result else 'failed')
    )
    return result


def download_basic(url, username, password):
    print('Download (Authorization Basic) ..')
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)
    result = url_request(url, opener)
    print(
        'Download (Authorization Basic) '
        + (f"done: '{result}'" if result else 'failed')
    )
    return result


def save_credentials(section, credentials):
    config.read(file_path)
    if section not in config:
        config.add_section(section)
    for credential, value in credentials.items():
        config[section][credential] = value
    with open(file_path, 'w') as configfile:
        config.write(configfile)


def cli():
    parser = argparse.ArgumentParser(
        description='Authenticated file download.'
    )
    parser.add_argument(
        'urls', nargs=argparse.REMAINDER, help='URLs to download from.'
    )
    parser.add_argument(
        '--update', action='store_true', help='Update credentials'
    )
    args = parser.parse_args()

    if not args.urls:
        parser.print_help()
        return

    config.read(file_path)

    for url in args.urls:
        parsed_url = urllib.parse.urlparse(url)
        section = f'credentials-{parsed_url.netloc}'

        update_credentials = args.update
        authorization = None
        try:
            authorization = config[section].get('authorization')
            username = config[section]['username']
            password = config[section]['password']
        except KeyError:
            update_credentials = True

        if update_credentials:
            username = input(f'({parsed_url.netloc}) Username: ')
            password = getpass.getpass(f'({parsed_url.netloc}) Password: ')
            save = input(f'({parsed_url.netloc}) Save credentials? [y/N]: ')
            if save.lower().startswith('y'):
                save_credentials(
                    section, {'username': username, 'password': password}
                )

        authorization_modes = ['basic', 'bearer']
        if authorization in authorization_modes:
            authorization_modes.remove(authorization)
            authorization_modes.insert(0, authorization)
        for auth in authorization_modes:
            if auth == 'bearer':
                result = download_bearer(url, password)
            elif auth == 'basic':
                result = download_basic(url, username, password)
            if result:
                save_credentials(section, {'authorization': auth})
                break

        if not result:
            exit(1)
