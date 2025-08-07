# Copyright (c) 2023 Henix, Henix.fr
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

"""Selectors helpers"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union

import re

########################################################################
## Constants

Object = Dict[str, Any]
OpCode = Tuple[
    int,
    Optional[Union[str, List[str]]],
    Optional[bool],
    Optional[Union[str, Set[str]]],
]

KEY = r'[a-z0-9A-Z-_./]+'
VALUE = r'[a-z0-9A-Z-_./@:#]+'
TAIL = rf"\[({KEY})\]"
EQUAL_EXPR = re.compile(rf'^({KEY})({TAIL})?\s*([=!]?=)\s*({VALUE})(?:,|$)')
INSET_EXPR = re.compile(
    rf'^({KEY})({TAIL})?\s+(in|notin)\s+\(({VALUE}(\s*,\s*{VALUE})*)\)(?:,|$)'
)
SETIN_EXPR = re.compile(
    rf'^\(({VALUE}(\s*,\s*{VALUE})*)\)\s+(in|notin)\s+({KEY})({TAIL})?(?:,|$)'
)
EXISTS_EXPR = re.compile(rf'^({KEY})({TAIL})?(?:,|$)')
NEXISTS_EXPR = re.compile(rf'^!({KEY})({TAIL})?(?:,|$)')


########################################################################
## Selectors helpers

OP_RESOLV = 0x01
OP_EQUAL = 0x10
OP_EXIST = 0x20
OP_NEXIST = 0x40
OP_INSET = 0x80
OP_SETIN = 0x100


def compile_selector(exprs: str, resolve_path: bool = True) -> List[OpCode]:
    """Compile selector.

    # Required parameters

    - exprs: a string, a comma-separated list of expressions

    # Optional parameters

    - resolve_path: a boolean, default True

    # Returned value

    A list of tuples, the 'compiled' selectors.

    # Raised exceptions

    A _ValueError_ exception is raised if at least one expression is
    invalid.
    """

    def _opcode(code, key, ope=None, val=None, tail=None):
        if not resolve_path and tail:
            raise ValueError(f'[] not allowed in label selectors: {exprs}.')
        if resolve_path and (tail or '.' in key):
            return code | OP_RESOLV, key.split('.') + ([tail] if tail else []), ope, val
        return code, key, ope, val

    if not exprs:
        return []

    if match := EQUAL_EXPR.match(exprs):
        key, _, tail, ope, value = match.groups()
        instr = _opcode(OP_EQUAL, key, ope == '!=', value, tail)
    elif match := EXISTS_EXPR.match(exprs):
        instr = _opcode(OP_EXIST, match.group(1), tail=match.group(3))
    elif match := NEXISTS_EXPR.match(exprs):
        instr = _opcode(OP_NEXIST, match.group(1), tail=match.group(3))
    elif match := INSET_EXPR.match(exprs):
        key, _, tail, ope, vals, _ = match.groups()
        instr = _opcode(
            OP_INSET, key, ope == 'notin', {v.strip() for v in vals.split(',')}, tail
        )
    elif match := SETIN_EXPR.match(exprs):
        vals, _, ope, key, _, tail = match.groups()
        instr = _opcode(
            OP_SETIN, key, ope == 'notin', {v.strip() for v in vals.split(',')}, tail
        )
    else:
        raise ValueError(f'Invalid expression {exprs}.')

    return [instr] + compile_selector(exprs[match.end() :].strip(', '), resolve_path)


def _resolve_path(items: List[str], obj) -> Tuple[bool, Optional[Any]]:
    head, rest = items[0], items[1:]
    try:
        if head in obj:
            return (True, obj[head]) if not rest else _resolve_path(rest, obj[head])
    except TypeError:
        pass
    return False, None


def _evaluate(obj: Object, req: OpCode) -> bool:
    """Evaluate whether obj matches selector."""
    opcode, key, neq, arg = req
    if opcode == OP_EQUAL:  # fast path
        if key in obj:
            return (str(obj[key]) == arg) ^ neq  # type: ignore
        return neq  # type: ignore

    if opcode & OP_RESOLV:
        found, value = _resolve_path(key, obj)  # type: ignore
    else:
        found, value = key in obj, obj.get(key)  # type: ignore

    if opcode & OP_EXIST:
        return found

    if opcode & OP_NEXIST:
        return not found

    if found and opcode & OP_SETIN:
        return (set({} if value is None else value) >= arg) ^ neq  # type: ignore
    if found and opcode & OP_EQUAL:
        return (str(value) == arg) ^ neq  # type: ignore
    if found:  # OP_INSET
        return (str(value) in arg) ^ neq  # type: ignore
    return neq  # type: ignore


def match_compiledfieldselector(obj: Object, opcodes: List[OpCode]) -> bool:
    return all(_evaluate(obj, opcode) for opcode in opcodes)


def match_compiledlabelselector(obj: Object, opcodes: List[OpCode]) -> bool:
    labels = obj.get('metadata', {}).get('labels', {})
    return all(_evaluate(labels, opcode) for opcode in opcodes)


def match_selectors(
    obj: Object,
    fieldselector: Union[None, str, List[OpCode]] = None,
    labelselector: Union[None, str, List[OpCode]] = None,
) -> bool:
    """Check if object matches selector.

    An empty selector matches.  The selectors can be strings or
    compiled selectors.

    The complete selector feature has been implemented.  `selector` is
    of form:

        expr[,expr]*

    where `expr` is one of `key`, `!key`, or `key op value`, with
    `op` being one of `=`, `==`, or `!=`.  The
    `key in (value[, value...])`, `key notin (value[, value...])`,
    `(value[, value...]) in key` and `(value[, value...]) notin key`
    set-based requirements are also implemented.

    # Required parameters

    - obj: a dictionary

    # Optional parameters

    - fieldselector: a string or a list of opcodes or None
    - labelselector: a string or a list of opcodes or None

    # Returned value

    A boolean.

    # Raised exceptions

    A _ValueError_ exception is raised if `fieldselector` or
    `labelselector` is not a valid.
    """
    if isinstance(fieldselector, str):
        fieldselector = compile_selector(fieldselector)
    if isinstance(labelselector, str):
        labelselector = compile_selector(labelselector, resolve_path=False)
    return (not fieldselector or match_compiledfieldselector(obj, fieldselector)) and (
        not labelselector or match_compiledlabelselector(obj, labelselector)
    )


def prepare_selectors(
    src: Any,
) -> Tuple[Optional[List[OpCode]], Optional[List[OpCode]]]:
    """Prepare selectors if defined.

    `src` is typically a request arg dictionary.  The selectors,
    `fieldSelector` and `labelSelector`, are compiled if defined.

    # Required parameters

    - src: a dictionary-like structure

    # Returned value

    A pair of lists of opcodes or None.

    # Raised exceptions

    A _ValueError_ exception is raised if the selectors defined in `src`
    are not a valid.
    ."""
    fieldselector = src.get('fieldSelector')
    labelselector = src.get('labelSelector')

    if fieldselector:
        fieldselector = compile_selector(fieldselector)
    if labelselector:
        labelselector = compile_selector(labelselector, resolve_path=False)
    return fieldselector, labelselector
