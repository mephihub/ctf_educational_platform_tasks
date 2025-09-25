#!/usr/bin/env python3


import argparse
import traceback
from pathlib import Path
import os
import json
import yaml
from collections import defaultdict
from dockerfile_parse import DockerfileParser
from datetime import datetime
from enum import Enum
from threading import Lock, current_thread
DC_REQUIRED_OPTIONS = ["services"]
DC_ALLOWED_OPTIONS = DC_REQUIRED_OPTIONS + ["volumes", "version"]

CONTAINER_REQUIRED_OPTIONS = ["restart", "container_name"]
CONTAINER_ALLOWED_OPTIONS = [
    "restart",
    "pids_limit",
    "mem_limit",
    "cpus",
    "build",
    "image",
    "ports",
    "volumes",
    "environment",
    "env_file",
    "healthcheck",
    "depends_on",
    "sysctls",
    "security_opt",

    "read_only",
    "tmpfs",
    "cap_drop",
    "user",
]
SERVICE_REQUIRED_OPTIONS = ["pids_limit", "mem_limit", "cpus"]
SERVICE_ALLOWED_OPTIONS = CONTAINER_ALLOWED_OPTIONS
DATABASES = [
    "redis",
    "postgres",
    "mysql",
    "mariadb",
    "mongo",
    "mssql",
    "clickhouse",
    "tarantool",
]
PROXIES = ["nginx", "envoy"]
CLEANERS = ["dedcleaner"]

REQUIRED_PATHS = [
    "DESCRIPTION.md",
    "task.yml",
]

DIFFICULTIES = ["easy", "medium", "hard"]
REQUIRED_TASK_KEYS = ['description', 'host-data']
REQUIRED_DESC_KEYS = ['name']
REQUIRED_HOST_DATA_KEYS = ['type', 'flag']
OUT_LOCK = Lock()
DISABLE_LOG = False



class ColorType(Enum):
    INFO = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"

    def __str__(self):
        return self.value

def colored_log(*messages, color: ColorType = ColorType.INFO):
    ts = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
    print(
        f"{color}{color.name} [{current_thread().name} {ts}]{ColorType.ENDC}", *messages
    )



BASE_DIR = Path(__file__).resolve().absolute().parent
TASKS_DIR = BASE_DIR / 'tasks'

class BaseValidator:
    def _log(self, message: str):
        with OUT_LOCK:
            if not DISABLE_LOG:
                colored_log(f"{self}: {message}")

    def _fatal(self, cond, message):
        global DISABLE_LOG

        with OUT_LOCK:
            if not cond:
                if not DISABLE_LOG:
                    colored_log(f"{self}: {message}", color=ColorType.FAIL)
                DISABLE_LOG = True
                raise AssertionError

    def _warning(self, cond: bool, message: str) -> bool:
        with OUT_LOCK:
            if not cond and not DISABLE_LOG:
                colored_log(f"{self}: {message}", color=ColorType.WARNING)
        return not cond

    def _error(self, cond, message) -> bool:
        with OUT_LOCK:
            if not cond and not DISABLE_LOG:
                colored_log(f"{self}: {message}", color=ColorType.FAIL)
        return not cond


class Task(BaseValidator):
    def __init__(self,BASE_DIR : Path,  name: str, category: str, topic: str):
        self._name = name
        self._category = category
        self._topic = topic
        self._path = BASE_DIR / category / topic / name
        task_conf_path = self._path / 'task.yml'
        with open(task_conf_path, 'r') as f:
            task_conf = yaml.safe_load(f)
        for key in REQUIRED_TASK_KEYS:
            if self._error(key in task_conf.keys(), f"required key {key} not in task.yml"):
                return 0
        if self._error(type(task_conf['description']) != list, 'description should be dictionary') or self._error(type(task_conf['host-data']) != list, 'host-data should be dictionary'):
            return 0
        for key in REQUIRED_DESC_KEYS:
            if self._error(key in task_conf['description'].keys(), f"required key {key} not in task.yml"):
                return 0
        for key in REQUIRED_HOST_DATA_KEYS:
            if self._error(key in task_conf['host-data'].keys(), f"required key {key} not in task.yml"):
                return 0
        if task_conf['host-data']['type'] == 'remote':
            if self._error((self._task.path / 'deploy').exists(), 'No deploy directory for remote task'):
                return 0
        self.task_conf = task_conf

    @property
    def name(self):
        return self._name
    
    @property
    def topic(self):
        return self._topic
    
    @property
    def category(self):
        return self._category

    @property
    def path(self):
        return self._path

    def __str__(self):
        return f"task {self._name}"

class StructureValidator(BaseValidator):
    def __init__(self, d: Path, task: Task):
        self._dir = d
        self._was_error = False
        self._task = task
        self.task_conf = task.task_conf

    def _error(self, cond, message):
        err = super()._error(cond, message)
        self._was_error |= err
        return err

    def validate(self):
        for file in REQUIRED_PATHS:
            path = self._task.path / file
            if self._error(path.exists(), f"{file} not found in service"):
                return 0
            
        self.validate_dir(self._task.path)
        return not self._was_error

    def validate_dir(self, d: Path):
        if not d.exists():
            return
        for f in d.iterdir():
            if f.is_file():
                self.validate_file(f)
            elif f.name[0] != ".":
                self.validate_dir(f)

    def validate_file(self, f: Path):
        path = f.relative_to(self._dir)

        self._error(f.name != ".gitkeep", f"{path} found, should be named .keep")

        if f.name == "docker-compose.yml":
            if not self._warning(self.task_conf['host-data']['type'] == 'local', 'You have docker-compose.yml but your task is local'):
                with f.open() as file:
                    dc = yaml.safe_load(file)

                    if self._error(isinstance(dc, dict), f"{path} is not dict"):
                        return

                    for opt in DC_REQUIRED_OPTIONS:
                        if self._error(opt in dc, f"required option {opt} not in {path}"):
                            return

                    if "version" in dc:
                        if self._error(
                            isinstance(dc["version"], str),
                            f"version option in {path} is not string",
                        ):
                            return

                        try:
                            dc_version = float(dc["version"])
                        except ValueError:
                            self._error(False, f"version option in {path} is not float")
                            return

                        self._error(
                            2.4 <= dc_version < 3,
                            f"invalid version in {path}, need >=2.4 and <3 (or no version at all), got {dc_version}",
                        )

                    for opt in dc:
                        self._error(
                            opt in DC_ALLOWED_OPTIONS,
                            f"option {opt} in {path} is not allowed",
                        )

                    services = []
                    databases = []
                    proxies = []
                    dependencies = defaultdict(list)

                    if self._error(
                        isinstance(dc["services"], dict),
                        f"services option in {path} is not dict",
                    ):
                        return

                    for container, container_conf in dc["services"].items():
                        if self._error(
                            isinstance(container_conf, dict),
                            f"config in {path} for container {container} is not dict",
                        ):
                            continue

                        for opt in CONTAINER_REQUIRED_OPTIONS:
                            self._error(
                                opt in container_conf,
                                f"required option {opt} not in {path} for container {container}",
                            )

                        self._error(
                            "restart" in container_conf
                            and container_conf["restart"] == "unless-stopped",
                            f'restart option in {path} for container {container} must be equal to "unless-stopped"',
                        )

                        for opt in container_conf:
                            self._error(
                                opt in CONTAINER_ALLOWED_OPTIONS,
                                f"option {opt} in {path} is not allowed for container {container}",
                            )

                        if self._error(
                            "image" not in container_conf or "build" not in container_conf,
                            f"both image and build options in {path} for container {container}",
                        ):
                            continue

                        if self._error(
                            "image" in container_conf or "build" in container_conf,
                            f"both image and build options not in {path} for container {container}",
                        ):
                            continue

                        if "image" in container_conf:
                            image = container_conf["image"]
                        else:
                            build = container_conf["build"]
                            if isinstance(build, str):
                                dockerfile = f.parent / build / "Dockerfile"
                            else:
                                context = build["context"]
                                if "dockerfile" in build:
                                    dockerfile = f.parent / context / build["dockerfile"]
                                else:
                                    dockerfile = f.parent / context / "Dockerfile"

                            if self._error(
                                dockerfile.exists(), f"no dockerfile found in {dockerfile}"
                            ):
                                continue

                            with dockerfile.open() as file:
                                dfp = DockerfileParser(fileobj=file)
                                image = dfp.baseimage

                            if self._error(
                                image is not None, f"no image option in {dockerfile}"
                            ):
                                continue

                        if "depends_on" in container_conf:
                            for dependency in container_conf["depends_on"]:
                                dependencies[container].append(dependency)

                        is_task = True
                        for database in DATABASES:
                            if database in image:
                                databases.append(container)
                                is_task = False

                        for proxy in PROXIES:
                            if proxy in image:
                                proxies.append(container)
                                is_task = False

                        for cleaner in CLEANERS:
                            if cleaner in image:
                                is_task = False

                        if is_task:
                            services.append(container)
                            for opt in SERVICE_REQUIRED_OPTIONS:
                                self._error(
                                    opt in container_conf,
                                    f"required option {opt} not in {path} for service {container}",
                                )

                            for opt in container_conf:
                                self._error(
                                    opt in SERVICE_ALLOWED_OPTIONS,
                                    f"option {opt} in {path} is not allowed for service {container}",
                                )

                    for service in services:
                        for database in databases:
                            self._warning(
                                service in dependencies and database in dependencies[service],
                                f"service {service} may need to depends_on database {database}",
                            )

                    for proxy in proxies:
                        for service in services:
                            self._warning(
                                proxy in dependencies and service in dependencies[proxy],
                                f"proxy {proxy} may need to depends_on service {service}",
                        )

    def __str__(self):
        return f"Structure validator for {self._task.name}"

def dir_check(p : Path) -> bool:
    return p.name[0] != '.' and p.is_dir()

def get_tasks(TASKS_DIR: Path, remote_only: bool = False ) -> list[Task]:
    result = []
    if os.getenv("TASK") in ["all", None]:
        for category_name in TASKS_DIR.iterdir():
            if dir_check(category_name):
                topics_dir = TASKS_DIR / category_name.name
                for topic_name in topics_dir.iterdir():
                    if dir_check(topic_name):
                        tasks_dir = topics_dir / topic_name.name
                        for task in tasks_dir.iterdir():
                            if dir_check(task):
                                t = Task(TASKS_DIR, task.name, category_name.name, topic_name.name)
                                if not remote_only:
                                    result.append(t)
                                elif t.task_conf['host-data']['type'] == 'remote':
                                    result.append(t)
    else:
        try:
            a = json.loads(os.environ['TASK'])
            result = [Task(TASKS_DIR, a['name'], a['category'], a['topic'])]
        except:
            colored_log("Invalid TASK env structure", color=ColorType.FAIL)
            exit(1)
    with OUT_LOCK:
        colored_log("Got services:", ", ".join(map(str, result)))
    return result
def list_tasks(_args: argparse.Namespace):
    tasks = get_tasks(TASKS_DIR, _args.remote)
    if outfile := os.getenv("GITHUB_OUTPUT"):
        data = {
            "include": [{"task": json.dumps({'name': task.name, 'category': task.category, 'topic': task.topic})} for task in tasks],
        }
        print(f"matrix={json.dumps(data)}")
        with open(outfile, "a") as f:
            f.write(f"matrix={json.dumps(data)}")


def validate_structure(_args):
    was_error = False
    for task in get_tasks(TASKS_DIR):
        validator = StructureValidator(TASKS_DIR, task)
        if not validator.validate():
            was_error = True

    if was_error:
        with OUT_LOCK:
            colored_log("Structure validator: failed", color=ColorType.FAIL)
            raise AssertionError

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate tasks for platform."
    )
    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser(
        "list",
        help="List tasks to test",
    )
    list_parser.add_argument('--remote', action='store_true')
    list_parser.set_defaults(func=list_tasks)
    
    validate_parser = subparsers.add_parser(
        "validate",
        help="Run structure validation",
    )
    validate_parser.set_defaults(func=validate_structure)
    parsed = parser.parse_args()
    if "func" not in parsed:
        print("Type -h")
        exit(1)

    try:
        parsed.func(parsed)
    except AssertionError:
        exit(1)
    except Exception as e:
        tb = traceback.format_exc()
        print("Got exception, report it:", e, tb)
        exit(1)
