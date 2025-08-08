import argparse
import os
import sys
import time
import threading
import signal
import logging
import queue
import datetime
import subprocess

from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent
from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def set_color(color):
    return f'\033[1;{(30 + color)}m'


def reset_color():
    return '\033[0m'


def on_wsl():
    return os.name != 'nt' and 'WSLENV' in os.environ


# Setup logger
FORMAT_STYLE = (
    '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s' + reset_color()
)
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(
    format=FORMAT_STYLE, level=logging.INFO, datefmt=DATE_FORMAT
)
formatter = logging.Formatter(FORMAT_STYLE, datefmt=DATE_FORMAT)


class WatchFilesRecursively(threading.Thread):
    def __init__(self, paths, exclude_paths):
        threading.Thread.__init__(self)
        self.paths = paths
        self.exclude_paths = exclude_paths
        self.update_queue = queue.Queue()
        self._stop_thread = threading.Event()
        self._observer = None
        self._observer_started = False

        # Event handler
        self.watch_dirs = []
        self._event_handler = FileSystemEventHandler()
        self._event_handler.on_modified = self._notify_watchers

        self.watch_file_dirs = []
        self._event_handler_file = FileSystemEventHandler()
        self._event_handler_file.on_modified = self._callback_file_watchers

    def join(self):
        self.stop()
        super().join()

    def stop(self):
        self.update_queue.put(None)
        self._stop_thread.set()

    def _notify_watchers(self, event=None):
        if isinstance(event, DirModifiedEvent):
            pass
        elif isinstance(event, FileModifiedEvent):
            if event.src_path not in self.exclude_paths:
                self.update_queue.put(datetime.datetime.now())

    def _callback_file_watchers(self, event):
        if (
            not event.is_directory
            and event.src_path in self.watch_file_dirs
            and event.src_path not in self.exclude_paths
        ):
            self._notify_watchers(event)

    def _restart_file_watcher(self):
        """Starts or restarts the file watcher"""
        if self._observer:
            try:
                self._observer.stop()
            except SystemExit as system_exit:
                raise system_exit
            except Exception:
                pass
            self._observer_started = False

        self._observer = Observer()
        for path in self.paths:
            if os.path.isfile(path):
                file_name = path
                self.watch_file_dirs.append(file_name)
                watch_dir = os.path.dirname(file_name)
                if watch_dir not in self.watch_file_dirs:
                    self.watch_file_dirs.append(watch_dir)
                    self._observer.schedule(
                        self._event_handler_file, watch_dir, recursive=False
                    )
            else:
                watch_dir = path
                if watch_dir not in self.watch_dirs:
                    self.watch_dirs.append(watch_dir)
                    self._observer.schedule(
                        self._event_handler, watch_dir, recursive=True
                    )
        try:
            self._observer.start()
            self._observer_started = True
        except SystemExit as system_exit:
            raise system_exit
        except Exception:
            self._observer_started = False

    def run(self):
        """Start file watcher"""
        while not self._stop_thread.is_set():
            if not self._observer_started:
                self._restart_file_watcher()
            # self._notify_watchers()
            self._stop_thread.wait(60)


def sync(command, verbose):
    logging.info(set_color(YELLOW) + 'Sync start ..')
    try:
        output = subprocess.check_output(command, shell=True)
        if verbose:
            print(output.decode())
        logging.info(set_color(GREEN) + 'Sync complete')
    except subprocess.CalledProcessError as error:
        logging.info(set_color(RED) + 'Sync failed')
        return error.returncode
    return 0


def wsl_path(path):
    output = subprocess.check_output(f'wslpath -w {path}', shell=True)
    return output.split()[0].decode()


def cli():
    parser = argparse.ArgumentParser(description='Automated file sync.')

    parser.add_argument(
        '-e',
        '--exclude',
        action='append',
        nargs=1,
        metavar=('exclude'),
        default=[],
        help='exclude path from observation',
    )
    if on_wsl():
        parser.add_argument(
            '--wsl',
            action='store_true',
            help='switch from WSL to fsync on Windows',
        )
    parser.add_argument(
        '-p',
        '--path',
        action='append',
        nargs=1,
        metavar=('path'),
        default=[],
        help='add path to observation',
    )
    parser.add_argument(
        '-d',
        '--delay',
        default=0.5,
        type=float,
        help='observing delay of sync command',
    )
    parser.add_argument(
        '-i',
        '--ignore',
        action='store_true',
        help='avoid path discovery from cp, scp and rsync',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose output'
    )

    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        help='command (automatically triggered on observe)',
    )

    args = parser.parse_args()

    if args.exclude:
        args.exclude = list(map(lambda x: os.path.abspath(x[0]), args.exclude))
    if args.verbose and args.exclude:
        print('Excluded paths:')
        for path in args.exclude:
            print(f'- {path}')

    if args.path:
        args.path = list(map(lambda x: os.path.abspath(x[0]), args.path))
    paths_to_observe = args.path
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if args.verbose and paths_to_observe:
        print('Paths to observe:')
        for path in paths_to_observe:
            print(f'- {path}')

    if not args.ignore:
        discover_paths_to_observe = []
        if args.command[0] in (
            'cp',
            'rsync',
            'scp',
        ):
            # Simplified source path discovery
            for argument in args.command[:-1]:
                if os.path.isdir(argument) or os.path.isfile(argument):
                    discover_paths_to_observe.append(os.path.abspath(argument))
                elif discover_paths_to_observe:
                    print(discover_paths_to_observe)
                    break
            if args.verbose and discover_paths_to_observe:
                print(f"Path discovery of '{args.command[0]}':")
                for path in discover_paths_to_observe:
                    print(f'- {path}')
        paths_to_observe += discover_paths_to_observe

    execute_cmd = ' '.join(args.command)
    if args.verbose:
        print(f'Command: {execute_cmd}')

    if on_wsl() and args.wsl:
        paths_to_observe_win = [wsl_path(path) for path in paths_to_observe]
        paths_args = (
            ' ' + ' '.join([f'-p={dir}' for dir in paths_to_observe_win])
            if paths_to_observe_win
            else ''
        )
        exclude_win = [wsl_path(path) for path in args.exclude]
        exclude_args = (
            ' ' + ' '.join([f'-e={dir}' for dir in exclude_win])
            if exclude_win
            else ''
        )
        verbose_args = ' -v' if args.verbose else ''
        try:
            subprocess.check_output('''cmd.exe /c "where fync"''', shell=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Missing 'fync' on Windows")
        if args.verbose:
            print('Switch to fync on Windows')
        command_win = (
            f'cmd.exe /c "fync -i -d={args.delay}{verbose_args}'
            f'{exclude_args}{paths_args} wsl {execute_cmd}"'
        )
        try:
            subprocess.check_output(command_win, shell=True)
        except KeyboardInterrupt:
            pass
        exit()

    watcher = WatchFilesRecursively(paths_to_observe, args.exclude)
    watcher.start()

    # Handle termination
    def terminate_gracefully(signum, frame):
        raise SystemExit(130)

    signal.signal(signal.SIGINT, terminate_gracefully)
    signal.signal(signal.SIGTERM, terminate_gracefully)

    try:
        while True:
            if watcher.update_queue.empty():
                exit_code = sync(execute_cmd, args.verbose)
                if exit_code != 0:
                    raise SystemExit(exit_code)

            # Get latest update
            last = watcher.update_queue.get()
            while not watcher.update_queue.empty():
                last = watcher.update_queue.get()

            remaining_delay = (
                args.delay - (datetime.datetime.now() - last).total_seconds()
            )
            if remaining_delay > 0:
                time.sleep(remaining_delay)
    except SystemExit as error:
        watcher.stop()
        logging.info('Service stopped')
        return error.code
