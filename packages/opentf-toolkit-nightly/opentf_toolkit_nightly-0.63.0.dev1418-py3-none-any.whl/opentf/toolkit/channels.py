# Copyright (c) 2021 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Toolkit helpers for channels plugins."""


from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Union

from copy import deepcopy
from datetime import datetime
from shlex import quote

import fnmatch
import ntpath
import os
import re

from opentf.commons import (
    EXECUTIONRESULT,
    WORKFLOWRESULT,
    make_event,
    make_uuid,
)
from opentf.toolkit import core

## workflow commands

SETOUTPUT_COMMAND = re.compile(r'^::set-output\s+name=([a-zA-Z_][a-zA-Z0-9_-]*)::(.*)$')
ATTACH_COMMAND = re.compile(r'^::attach(\s+.*?)?::(.*?)\s*$')
UPLOAD_COMMAND = re.compile(r'^::upload(\s+.*?)?::(.*?)\s*$')
DOWNLOAD_COMMAND = re.compile(r'^::download(\s+.*?)?::(.*?)\s*$')
DEBUG_COMMAND = re.compile(r'^::debug::(.*)$')
WARNING_COMMAND = re.compile(r'^::warning(\s+(.*)+)?::(.*)$')
ERROR_COMMAND = re.compile(r'^::error(\s+(.*)+)?::(.*)$')
STOPCOMMANDS_COMMAND = re.compile(r'^::stop-commands::(\w+)$')
ADDMASK_COMMAND = re.compile(r'^::add-mask::(.*)$')
PUT_FILE_COMMAND = re.compile(r'^::put\s+file=(.*?)\s*::(.*?)\s*$')

## step sequence IDs

CHANNEL_REQUEST = -1
CHANNEL_RELEASE = -2
CHANNEL_NOTIFY = -3
CHANNEL_TERMINATE = -4  # kill
CHANNEL_FORCEKILL = -9  # kill -9

DEFAULT_CHANNEL_LEASE = 60  # how long to keep the offer, in seconds

## shells

# For cmd:
#
# - /D: ignore registry autorun commands
# - /E:ON: enable command extensions
# - /V:OFF: disable delayed environment expansion
# - /S: strip " quote characters from command
# - /C: run command then terminate
#
# For bash:
#
# - --noprofile: ignore /etc/profile & al.
# - --norc: ignore /etc/bash.bashrc & al.
# - -e: exit at first error
# - -o pipefail: exit if one of the commands in the pipe fails

SHELL_DEFAULT = {'linux': 'bash', 'macos': 'bash', 'windows': 'cmd'}
SHELL_TEMPLATE = {
    'bash': 'bash --noprofile --norc -eo pipefail {0}',
    'cmd': '%ComSpec% /D /E:ON /V:OFF /S /C "CALL {0}"',
    'python': 'python {0}',
    'powershell': '''powershell -command ". './{0}'"''',
    'pwsh': '''pwsh -command ". './{0}'"''',
}

SCRIPTPATH_DEFAULT = {'linux': '/tmp', 'macos': '/tmp', 'windows': '%TEMP%'}
SCRIPTFILE_DEFAULT = {
    'linux': '{root}/{job_id}_{step_sequence_id}.sh',
    'macos': '{root}/{job_id}_{step_sequence_id}.sh',
    'windows': '{root}\\{job_id}_{step_sequence_id}.cmd',
}

LINESEP = {'linux': '\n', 'macos': '\n', 'windows': '\r\n'}
RUNNER_OS = {'windows', 'macos', 'linux'}

WORKSPACE_TEMPLATE = {
    'linux': '`pwd`/{workspace}',
    'macos': '`pwd`/{workspace}',
    'windows': '%CD%\\{workspace}',
}
VARIABLES_TEMPLATE = {
    'linux': '{root}/{job_id}_dynamic_env.sh',
    'macos': '{root}/{job_id}_dynamic_env.sh',
    'windows': '{root}\\{job_id}_dynamic_env.cmd',
}

PROLOG_SCRIPTS = {
    'windows': (
        'call "%OPENTF_VARIABLES%"',
        '@start /b cmd /c "@timeout /T 2 >nul & @del /q "{root}\\{job_id}_*.cmd""',
        # '@del /q "{root}\\{job_id}_*.cmd"',
        '@if "%OPENTF_WORKSPACE:~-2,2%" NEQ "\\." (@if exist "%OPENTF_WORKSPACE%" @rmdir /s/q "%OPENTF_WORKSPACE%")',
        '@cd "%OPENTF_WORKSPACE%"',
    ),
    'linux': (
        '. "$OPENTF_VARIABLES"',
        'rm "{root}/{job_id}"_*.sh',
        'if [[ ${OPENTF_WORKSPACE} && "${OPENTF_WORKSPACE: -2}" != "/." ]]; then rm -rf "$OPENTF_WORKSPACE"; fi',
        'cd "$OPENTF_WORKSPACE"',
    ),
    'macos': (
        '. "$OPENTF_VARIABLES"',
        'rm "{root}/{job_id}"_*.sh',
        'if [[ ${OPENTF_WORKSPACE} && "${OPENTF_WORKSPACE: -2}" != "/." ]]; then rm -rf "$OPENTF_WORKSPACE"; fi',
        'cd "$OPENTF_WORKSPACE"',
    ),
}

LOAD_VARIABLES = 0
REMOVE_SCRIPTS = 1
REMOVE_WORKSPACE = 2
MOVE_TO_WORKSPACE = 3

HOOKS_ANNOTATIONS = 'opentestfactory.org/hooks'

OPENTF_VARIABLES_TYPE = 'application/vnd.opentestfactory.opentf-variables'
OPENTF_VARIABLES_REGEX = re.compile(r'^(export|set)\s(\"?.+)$')
OPENTF_VARIABLES_NAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')


## Lease helpers


class Offer(NamedTuple):
    """An offer for a job."""

    job_id: str
    metadata: Dict[str, Any]
    candidates: List[str]
    tags: Set[str]


class Lease(NamedTuple):
    """A lease for a job."""

    job_id: str
    expire: datetime
    offer: Dict[str, Any]
    tags: Set[str]


## Variables helpers


def make_variable_linux(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for linux runners."""

    def pseudoquote(val: str):
        if '"' in val:
            val = val.replace('"', '\\"')
        if ' ' in val or '\t' in val or '\n' in val:
            val = f'"{val}"'
        return val

    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            value = quote(value)
        else:
            value = pseudoquote(value)
    else:
        value = pseudoquote(variable)
    return f'export {name}={value}'


def make_variable_windows(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for windows runners."""
    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            for symbol in '^&<>':
                value = value.replace(symbol, f'^{symbol}')
            value = value.replace('%', '%%')
    else:
        value = variable
    return f'@set "{name}={value}"'


def _add_default_variables(
    script: List[str], job_id: str, runner_os: str, root: str
) -> None:
    """Prepare default variables."""
    script.append(
        VARIABLE_MAKER[runner_os](
            'OPENTF_VARIABLES',
            VARIABLES_TEMPLATE[runner_os].format(job_id=job_id, root=root),
        )
    )
    script.append(VARIABLE_MAKER[runner_os]('OPENTF_ACTOR', 'dummy'))
    script.append(VARIABLE_MAKER[runner_os]('CI', 'true'))


def get_opentf_variables_path(metadata: Dict[str, Any]) -> str:
    return VARIABLES_TEMPLATE[metadata['channel_os']].format(
        job_id=metadata['job_id'], root=metadata['channel_temp']
    )


def _read_opentf_variables(lines: List[str]) -> Dict[str, str]:
    variables = {}
    for line in lines:
        if '=' not in line:
            continue
        line = line.strip()
        if set_export := OPENTF_VARIABLES_REGEX.match(line):
            line = set_export.group(2)
            if line.startswith('"'):
                line = line[1:-1]
        key, _, value = line.partition('=')
        if OPENTF_VARIABLES_NAME_REGEX.match(key):
            variables[key] = value
    return variables


def _get_opentf_variables(path: str) -> Dict[str, str]:
    with open(path, 'r') as f:
        variables = _read_opentf_variables(f.readlines())
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return variables


def process_opentf_variables(result: Dict[str, Any]) -> None:
    """Process OPENTF_VARIABLES attachment if available.

    If OPENTF_VARIABLES is in the attachments, move its content to
    the variables field of the result.
    """
    if attachments := result['metadata'].get('attachments'):
        variables = {}
        for path, data in attachments.copy().items():
            if data.get('type') == OPENTF_VARIABLES_TYPE:
                variables = _get_opentf_variables(path)
                del result['metadata']['attachments'][path]
                result['attachments'].remove(path)
                if not result['metadata']['attachments']:
                    del result['metadata']['attachments']
                if not result['attachments']:
                    del result['attachments']
        result['variables'] = variables


# Workflow commands helpers


def _make_attachment_url(
    metadata: Dict[str, Any],
    remote: str,
    separator: str,
    is_artifact: bool = False,
    name: Optional[str] = None,
) -> Tuple[str, str]:
    """Prepare attachment URL.

    Attachment URLs are of the form:

    ```
    /tmp/{workflow_id}-{uuid}_WR_{name}                # artifacts
    /tmp/{job_id}-{uuid}_{step_sequence_id}_{name}     # attachments
    ```
    """
    uuid = make_uuid()
    prefix = metadata['workflow_id'] if is_artifact else metadata['job_id']
    suffix = 'WR' if is_artifact else metadata['step_sequence_id']
    url = f'/tmp/{prefix}-{uuid}_{suffix}_{name or remote.split(separator)[-1]}'
    return url, uuid


class CommandException(Exception):
    pass


def _get_cmd_params(args: str) -> Dict[str, str]:
    """Extract workflow command parameters."""
    details = {}
    if args:
        for parameter in args.strip().split(','):
            if '=' not in parameter:
                raise CommandException(
                    f'Invalid workflow command parameter: {parameter}.'
                )
            key, _, value = parameter.strip().partition('=')
            details[key] = value
    return details


## masks helpers


class JobState:
    def __init__(self) -> None:
        self.stop_command: Optional[str] = None
        self.masks: List[str] = []
        self.output_commands: List[str] = []
        self.attachments: List[str] = []
        self.attachments_metadata: Dict[str, Any] = {}
        self.artifacts_resp: bool = False


def mask(line: str, state: JobState) -> str:
    """Remove masked values."""
    for masked in state.masks:
        line = line.replace(masked, '***')
    return line


def _as_log(line: str, jobstate: JobState):
    if wcmd := DEBUG_COMMAND.match(line):
        return f'DEBUG,{mask(wcmd.group(1), jobstate)}'
    if wcmd := WARNING_COMMAND.match(line):
        return f'WARNING,{mask(wcmd.group(3), jobstate)}'
    if wcmd := ERROR_COMMAND.match(line):
        return f'ERROR,{mask(wcmd.group(3), jobstate)}'
    return mask(line, jobstate).rstrip()


## artifacts


def process_upload(result: Dict[str, Any]) -> Dict[str, Any]:
    """Process ExecutionResult event containing .metadata.upload flag.

    Remove the artifact-related items from `result` (URLs starting with
    `/tmp/{workflow_id}_WR_`).

    # Required parameters

    - result: a dictionary (an ExecutionResult command)

    # Returned value

    A WorkflowResult event.
    """

    def _filter_items(key: str) -> Tuple[List[str], Dict[str, Any]]:
        metadata = {}
        items = [item for item in result['attachments'] if item[pos:].startswith(key)]
        if items:
            metadata = {
                k: v for k, v in result['metadata']['attachments'].items() if k in items
            }
        return items, metadata

    del result['metadata']['upload']
    pos = len('/tmp/')
    upload, upload_metadata = _filter_items(result['metadata']['workflow_id'])
    attach, attach_metadata = _filter_items(result['metadata']['job_id'])

    if attach:
        result['attachments'] = attach
        result['metadata']['attachments'] = attach_metadata
    else:
        del result['attachments']
        del result['metadata']['attachments']

    metadata = {
        'attachments': upload_metadata,
        'name': result['metadata'].get('step_id'),
        'namespace': result['metadata']['namespace'],
        'workflow_id': result['metadata']['workflow_id'],
        'job_id': result['metadata']['job_id'],
    }
    return make_event(WORKFLOWRESULT, metadata=metadata, attachments=upload)


def _download_artifacts(
    artifacts: List[str],
    targeted_remote_path: str,
    remote_path: str,
    params: Dict[str, str],
    _put: Callable[[str, str], None],
    is_windows: bool,
) -> bool:
    """Download artifacts matching a pattern.

    # Required parameters

    - artifacts: a list of artifact names
    - targeted_remote_path: a string
    - remote_path: a string
    - params: a dictionary
    - _put: a function copying a local file to a remote environment
    - is_windows: a boolean

    # Returned value

    A boolean indicating if artifacts were uploaded.
    """
    filename, pattern = params.get('file'), params.get('pattern')
    if filename and pattern:
        raise CommandException('Cannot specify both "file" and "pattern".')
    if not filename and not pattern:
        pattern = '*'
    found = False
    for artifact in artifacts:
        artifact_name = artifact.split('_')[-1]
        if filename and filename == artifact_name:
            found = True
            if not remote_path:
                targeted_remote_path = core.join_path(
                    targeted_remote_path, artifact_name, is_windows
                )
            _put(targeted_remote_path, artifact)
        elif pattern and fnmatch.fnmatch(artifact_name, pattern):
            found = True
            pattern_path = core.join_path(
                targeted_remote_path, artifact_name, is_windows
            )
            _put(pattern_path, artifact)
    return found


def process_output(
    event: Dict[str, Any],
    resp: Optional[int],
    stdout: List[str],
    stderr: List[str],
    jobstate: JobState,
    _get: Callable[[str, str], None],
    _put: Callable[[str, str], None],
    variables: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Process output, filling structures.

    `event` is expected to have its metadata enriched with the following
    fields:

    - channel_os: the runner OS
    - channel_temp: the temporary directory on the runner

    # Required parameters

    - event: an ExecutionCommand event
    - resp: an integer
    - stdout: a list of strings
    - stderr: a list of strings
    - jobstate: a JobState object
    - _get: a function copying a remote file to a local path
    - _put: a function copying a local file to a remote environment

    # Returned value

    An ExecutionResult event.

    # Functions arguments

    ## get

    - destination_url: a string
    - remote_path: a string (file location on execution environment)

    May raise exceptions.

    ## put

    - remote_path: a string (file location on execution environment)
    - source_url: a string

    May raise exceptions.
    """

    def _get_targeted_path(remote_path: str) -> str:
        working_directory = core.join_path(
            metadata['job_id'], event.get('working-directory'), is_windows
        )
        return core.join_path(working_directory, remote_path, is_windows)

    def _attach(remote: str, args: str, is_artifact: bool = False) -> int:
        if is_windows:
            remote = ntpath.normpath(remote)
        try:
            params = _get_cmd_params(args)
            attachment_url, uuid = _make_attachment_url(
                metadata, remote, separator, is_artifact, name=params.get('name')
            )
            params['uuid'] = uuid
            _get(remote, attachment_url)
            attachments_metadata[attachment_url] = params
            attachments.append(attachment_url)
            return resp
        except CommandException as err:
            logs.append(f'ERROR,{err.args[0]}')
        except Exception as err:
            logs.append(f'ERROR,Could not read {remote}: {err}.')
        return 2

    def _putfile(remote_path: str, data: str) -> int:
        targeted_remote_path = _get_targeted_path(remote_path)
        try:
            file_ = f'/tmp/in_{metadata["workflow_id"]}_{data}'
            if not os.path.exists(file_):
                logs.append(f'ERROR,Invalid "resources.files" reference "{data}".')
                return 2
            _put(targeted_remote_path, file_)
            return resp
        except Exception as err:
            logs.append(
                f'ERROR,Could not send file "{data}" to remote path "{remote_path}": {err}.'
            )
            return 2

    def _download(remote_path: str, args: str) -> int:
        try:
            artifacts = metadata.get('artifacts', [])
            targeted_remote_path = _get_targeted_path(remote_path)
            params = _get_cmd_params(args)
            if _download_artifacts(
                artifacts, targeted_remote_path, remote_path, params, _put, is_windows
            ):
                return resp
            logs.append('ERROR,No artifact matching requested name/pattern found.')
        except CommandException as err:
            logs.append(f'ERROR,{err.args[0]}')
        except Exception as err:
            logs.append(
                f'ERROR,Could not send artifacts to remote path "{remote_path}": {err}.'
            )
        return 2

    metadata: Dict[str, Any] = event['metadata']
    is_windows: bool = metadata['channel_os'] == 'windows'
    separator = '\\' if is_windows else '/'
    outputs = {}
    logs: List[str] = []
    attachments: List[str] = []
    attachments_metadata: Dict[str, Any] = {}

    is_channel_notify = False
    step_sequence_id = metadata['step_sequence_id']
    if resp is None:
        resp, is_channel_notify = 0, True
    if not is_channel_notify and jobstate.output_commands:
        stdout.extend(jobstate.output_commands)
        jobstate.output_commands.clear()

    for line in stdout:
        # Parsing stdout for workflow commands
        if jobstate.stop_command:
            if line == jobstate.stop_command:
                jobstate.stop_command = None
            continue

        if is_channel_notify and SETOUTPUT_COMMAND.match(line):
            jobstate.output_commands.append(line)
            continue

        if wcmd := ATTACH_COMMAND.match(line):
            resp = _attach(wcmd.group(2), wcmd.group(1))
        elif wcmd := UPLOAD_COMMAND.match(line):
            jobstate.artifacts_resp = True
            resp = _attach(wcmd.group(2), wcmd.group(1), is_artifact=True)
        elif wcmd := DOWNLOAD_COMMAND.match(line):
            resp = _download(wcmd.group(2), wcmd.group(1))
        elif wcmd := PUT_FILE_COMMAND.match(line):
            resp = _putfile(wcmd.group(2), wcmd.group(1))
        elif wcmd := SETOUTPUT_COMMAND.match(line):
            outputs[wcmd.group(1)] = wcmd.group(2)
        elif wcmd := STOPCOMMANDS_COMMAND.match(line):
            jobstate.stop_command = f'::{wcmd.group(1)}::'
        elif wcmd := ADDMASK_COMMAND.match(line):
            jobstate.masks.append(wcmd.group(1))
        else:
            logs.append(_as_log(line, jobstate))

    for line in stderr:
        logs.append(mask(line, jobstate).rstrip())

    if is_channel_notify:
        notify = make_event(EXECUTIONRESULT, metadata=deepcopy(metadata), status=resp)
        notify['metadata']['step_sequence_id_origin'] = metadata['step_sequence_id']
        notify['metadata']['step_sequence_id'] = CHANNEL_NOTIFY
        notify['logs'] = logs
        if notify['metadata'].get('artifacts'):
            del notify['metadata']['artifacts']
        if attachments:
            jobstate.attachments.extend(attachments)
            jobstate.attachments_metadata.update(attachments_metadata)
        return notify

    if metadata.get('artifacts'):
        del metadata['artifacts']

    opentf_variables = None
    if step_sequence_id != CHANNEL_RELEASE:
        if variables:
            opentf_variables = _read_opentf_variables(variables)
        else:
            _attach(
                get_opentf_variables_path(metadata), f'type={OPENTF_VARIABLES_TYPE}'
            )

    result = make_event(EXECUTIONRESULT, metadata=metadata, status=resp)
    if outputs:
        result['outputs'] = outputs
    if logs:
        result['logs'] = logs
    if attachments or jobstate.attachments:
        result['attachments'] = jobstate.attachments + attachments
        result['metadata']['attachments'] = {
            **jobstate.attachments_metadata,
            **attachments_metadata,
        }
        jobstate.attachments.clear()
        jobstate.attachments_metadata = {}
    if jobstate.artifacts_resp:
        result['metadata']['upload'] = resp
        jobstate.artifacts_resp = False
    if opentf_variables:
        result['variables'] = opentf_variables
    return result


def _export_opentf_workspace(runner_os: str, workspace: str, script: List[str]) -> None:
    opentf_workspace = WORKSPACE_TEMPLATE[runner_os].format(workspace=workspace)
    if runner_os == 'windows':
        script.append('@type nul >>"%OPENTF_VARIABLES%"')
        script.append(
            f'@echo set "OPENTF_WORKSPACE={opentf_workspace}" >>"%OPENTF_VARIABLES%"'
        )
    else:
        script.append('touch "$OPENTF_VARIABLES"')
        script.append(
            f'echo export OPENTF_WORKSPACE="{opentf_workspace}" >> "$OPENTF_VARIABLES"'
        )


def _create_workspace(runner_os: str, workspace: str, script: List[str]) -> None:
    if runner_os == 'windows':
        script.append(f'@if not exist {workspace} @mkdir {workspace}')
    else:
        script.append(f'mkdir -p {workspace}')
    _export_opentf_workspace(runner_os, workspace, script)


def _must_keep_workspace(metadata: Dict[str, Any]) -> bool:
    hooks_annotations = metadata.get('annotations', {}).get(HOOKS_ANNOTATIONS, {})
    if hooks_annotations.get('channel') == 'teardown':
        return hooks_annotations.get('keep-workspace')
    return False


def _must_remove_workspace(metadata: Dict[str, Any]) -> bool:
    hooks_annotations = metadata.get('annotations', {}).get(HOOKS_ANNOTATIONS, {})
    if hooks_annotations.get('channel') == 'teardown':
        return hooks_annotations.get('keep-workspace') is False
    return False


def _maybe_change_directory(
    command: Dict[str, Any], runner_os: str, script: List[str], prefix: str
) -> None:
    if 'working-directory' not in command:
        return
    path = command['working-directory']
    if runner_os == 'windows':
        path = path.replace('/', '\\')
    if ' ' in path:
        path = '"' + path.strip('"') + '"'
    script.append(f'{prefix}cd {path}')


def _maybe_create_workspace(
    metadata: Dict[str, Any], runner_os: str, step_sequence_id: int, script: List[str]
) -> None:
    hooks_annotations = metadata.get('annotations', {}).get(HOOKS_ANNOTATIONS, {})
    if hooks_annotations.get('channel') == 'setup':
        if workspace := hooks_annotations.get('use-workspace'):
            _create_workspace(runner_os, workspace, script)
            if runner_os == 'windows':
                script.append(
                    f'@echo Using workspace \'{workspace}\' on execution environment'
                )
            else:
                script.append(
                    f'echo "Using workspace \'{workspace}\' on execution environment"'
                )
        elif step_sequence_id == 0:
            _export_opentf_workspace(runner_os, '.', script)
    elif step_sequence_id == 0:
        _create_workspace(runner_os, metadata['job_id'], script)


def _make_prolog(
    runner_os: str,
    job_id: str,
    step_sequence_id: int,
    root: str,
    script: List[str],
    command: Dict[str, Any],
) -> None:
    local_variables_names = (
        command['metadata'].get('annotations', {}).get('local_variables_names', [])
    )
    for name, value in command.get('variables', {}).items():
        if name not in local_variables_names:
            script.append(VARIABLE_MAKER[runner_os](name, value))

    script.append(PROLOG_SCRIPTS[runner_os][LOAD_VARIABLES])
    for name, value in command.get('variables', {}).items():
        if name in local_variables_names:
            script.append(VARIABLE_MAKER[runner_os](name, value))

    if step_sequence_id != CHANNEL_RELEASE and _must_remove_workspace(
        command['metadata']
    ):
        script.append(PROLOG_SCRIPTS[runner_os][REMOVE_WORKSPACE])
        _export_opentf_workspace(runner_os, '.', script)
    elif step_sequence_id == CHANNEL_RELEASE:
        # on windows, the script ends if it is removed, so script
        # removal should be the last operation
        if not _must_keep_workspace(command['metadata']):
            script.append(PROLOG_SCRIPTS[runner_os][REMOVE_WORKSPACE])
        else:
            if runner_os == 'windows':
                script.append(
                    '@echo Keeping workspace \'%OPENTF_WORKSPACE%\' on execution environment'
                )
            else:
                script.append(
                    'echo "Keeping workspace \'$OPENTF_WORKSPACE\' on execution environment"'
                )

        script.append(
            PROLOG_SCRIPTS[runner_os][REMOVE_SCRIPTS].format(root=root, job_id=job_id)
        )
    else:
        script.append(PROLOG_SCRIPTS[runner_os][MOVE_TO_WORKSPACE])


def _make_altshell_script(
    command: Dict[str, Any], path: str, runner_os: str
) -> List[str]:
    """Generate script for non-default shells.

    Creates a file in the execution environment and then use the
    custom shell to run the script.

    # Required parameters

    - command: an ExecutionCommand event
    - path: a string
    - runner_os: a string

    # Returned value

    A list of two strings: the first is a file creation command, the
    second is a command to run the script.
    """
    shell = command['shell']
    shell_script = command['scripts']
    if shell in ('powershell', 'pwsh'):
        path += '.ps1'
        shell_script = (
            ["$ErrorActionPreference = 'stop'"]
            + shell_script
            + [
                'if ((Test-Path -LiteralPath variable:\\LASTEXITCODE)) { exit $LASTEXITCODE }'
            ]
        )
    content = LINESEP[runner_os].join(shell_script)
    what = core.create_file(path, content, target=runner_os)
    if runner_os == 'windows' and shell == 'bash':
        shell_command = (
            '%USERPROFILE%\\AppData\\Local\\Programs\\Git\\bin\\'
            + SHELL_TEMPLATE[shell]
        )
    else:
        shell_command = SHELL_TEMPLATE.get(shell, shell)
    return [what, shell_command.format(path)]


def make_script(
    command: Dict[str, Any], script_path: Optional[str], runner_os: str
) -> Tuple[str, str, str]:
    """Prepare script.

    # Required parameters

    - command: an ExecutionCommand event
    - script_path: a string or None, where to put script on runner
    - runner_os: a string

    # Returned value

    script_path, script_content, script_command.
    """
    metadata = command['metadata']
    job_id = metadata['job_id']
    step_sequence_id = metadata['step_sequence_id']
    root = script_path or SCRIPTPATH_DEFAULT[runner_os]
    script_path = SCRIPTFILE_DEFAULT[runner_os].format(
        root=root, job_id=job_id, step_sequence_id=step_sequence_id
    )
    script_command = SHELL_TEMPLATE[SHELL_DEFAULT[runner_os]].format(f'"{script_path}"')

    script: List[str] = []
    if runner_os == 'windows':
        script.append('@echo off')
        prefix = '@'
    else:
        script.append('#!/usr/bin/env bash')
        prefix = ''

    _add_default_variables(script, job_id, runner_os, root)

    _maybe_create_workspace(metadata, runner_os, step_sequence_id, script)
    _make_prolog(runner_os, job_id, step_sequence_id, root, script, command)
    _maybe_change_directory(command, runner_os, script, prefix)

    if command.get('shell') in (None, SHELL_DEFAULT[runner_os]):
        script += command['scripts']
    else:
        script += _make_altshell_script(
            command, f'{job_id}_shell_script_{step_sequence_id}', runner_os
        )

    return script_path, LINESEP[runner_os].join(script), script_command


VARIABLE_MAKER = {
    'linux': make_variable_linux,
    'macos': make_variable_linux,
    'windows': make_variable_windows,
}
