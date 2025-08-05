import hashlib
import json
import os
from datetime import datetime
from enum import Enum
from warnings import warn


class TaskType(Enum):
    ONDEMAND = "ondemand"
    SCHEDULE = "schedule"
    KEEPALIVE = "keepalive"


class TaskExec(Enum):
    SYSTEM = "system"
    STOP = "stop"
    TALEND = "talend"
    SHELL = "shell"


class ParseWarning(Warning): ...


class ParseError(Exception): ...


class Task:
    def __init__(self, json_file: str):
        with open(json_file, "r", encoding="utf-8") as fp:
            try:
                json_content = json.load(fp)
            except json.JSONDecodeError as ex:
                raise ParseError(f"Parser: {type(ex).__name__} ({ex.args})") from ex

        if not "type" in json_content:
            warn("Parser: type not specified; set to 'ondemand'.", ParseWarning)
            self.type = TaskType.ONDEMAND
        elif json_content["type"] not in [t.value for t in TaskType]:
            warn(
                f"Parser: type unknown: '{json_content['type']}'; set to 'ondemand'.",
                ParseWarning,
            )
            self.type = TaskType.ONDEMAND
        else:
            self.type = TaskType(json_content["type"])

        if not "exec" in json_content:
            warn("Parser: exec not specified; set to 'system'.", ParseWarning)
            self.exec = TaskExec.SYSTEM
        elif json_content["exec"] not in [te.value for te in TaskExec]:
            warn(
                f"Parser: exec unknown: '{json_content['exec']}'; set to 'system'.",
                ParseWarning,
            )
            self.exec = TaskExec.SYSTEM
        else:
            self.exec = TaskExec(json_content["exec"])

        if not "args" in json_content:
            if self.exec == TaskExec.SYSTEM:
                raise ParseError("Parser: args not specified in task file with exec 'system'.")
            else:
                self.args = []
        else:
            self.args = json_content["args"]

        self.package: str | None = None
        self.java_exec = None
        if self.exec == TaskExec.TALEND:
            if "package" in json_content:
                self.package = str(json_content["package"])
                if not os.path.isfile(self.package):
                    raise ParseError(f"Parser: package file not found: '{self.package}'.")

                package_md5 = hashlib.md5()
                with open(self.package, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        package_md5.update(chunk)
                self.package_md5 = package_md5.hexdigest()

            else:
                raise ParseError("Parser: package not specified in task file with exec 'talend'.")

            if "java" in json_content:
                self.java_exec = str(json_content["java"])
            else:
                self.java_exec = "java"

        if self.type == TaskType.SCHEDULE:
            if not "schedule" in json_content:
                raise ParseError("Parser: schedule not specified in task file of type 'schedule'.")
            self.schedule = str(json_content["schedule"])
            if len(self.schedule.split()) != 5:
                raise ParseError(f"Parser: Malformated schedule: '{self.schedule}'.")
        else:
            self.schedule = None

        self.cwd = str(json_content["cwd"]) if "cwd" in json_content else None
        self.env = {**json_content["env"]} if "env" in json_content else {}
        self.info = str(json_content["info"]) if "info" in json_content else ""
        self.tokens = list(json_content["tokens"]) if "tokens" in json_content else []

        if "shell" in json_content:
            shell = bool(json_content["shell"])
            if shell and self.exec in [TaskExec.SYSTEM, TaskExec.SHELL]:
                warn(f"Parser: Legacy task setting 'shell: true' found; set 'exec' to '{TaskExec.SHELL.value}'.", ParseWarning)
                self.exec = TaskExec.SHELL
            elif shell:
                raise ParseError(f"Parser: Parser: Legacy field 'shell' found and 'exec' value '{self.exec.value}' is incompatible.")

        self.runtime = {}  # Store runtime data, i. e. for talend jobs

    def schedule_matches(self, dt: datetime):
        def fill_ranges(arr: list) -> list:
            res = []
            for item in arr:
                split_item = item.split("-")
                if len(split_item) == 1:
                    res.append(item)
                if len(split_item) == 2:
                    for new_item in range(int(split_item[0]), int(split_item[1]) + 1):
                        res.append(str(new_item))
                if len(split_item) > 2:
                    raise RuntimeError(f"Malformed schedule element: '{item}'.")
            return res

        if self.schedule is None:
            return False

        schedule_parts = self.schedule.split()

        if not (schedule_parts[0] == "*" or str(dt.minute) in fill_ranges(schedule_parts[0].split(","))):
            return False

        if not (schedule_parts[1] == "*" or str(dt.hour) in fill_ranges(schedule_parts[1].split(","))):
            return False

        if not (schedule_parts[2] == "*" or str(dt.day) in fill_ranges(schedule_parts[2].split(","))):
            return False

        if not (schedule_parts[3] == "*" or str(dt.month) in fill_ranges(schedule_parts[3].split(","))):
            return False

        weekdays = fill_ranges(schedule_parts[4].split(","))
        if "0" in weekdays:
            weekdays.append("7")
        if not (schedule_parts[4] == "*" or str(dt.isoweekday()) in weekdays):
            return False

        return True
