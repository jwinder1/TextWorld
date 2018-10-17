# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.


from collections import OrderedDict
import os
import glob
from os.path import join as pjoin
from shutil import copyfile, copytree, rmtree
from typing import Optional

from textworld.logic import GameLogic
from textworld.generator.vtypes import VariableType, VariableTypeTree
from textworld.utils import maybe_mkdir, RegexDict

BUILTIN_DATA_PATH = os.path.dirname(__file__)
LOGIC_DATA_PATH = pjoin(BUILTIN_DATA_PATH, 'logic')
TEXT_GRAMMARS_PATH = pjoin(BUILTIN_DATA_PATH, 'text_grammars')


def _maybe_copyfile(src, dest, force=False, verbose=False):
    if not os.path.isfile(dest) or force:
        copyfile(src=src, dst=dest)
    else:
        if verbose:
            print("Skipping {} (already exists).".format(dest))


def _maybe_copytree(src, dest, force=False, verbose=False):
    if os.path.exists(dest):
        if force:
            rmtree(dest)
        else:
            if verbose:
                print("Skipping {} (already exists).".format(dest))
            return

    copytree(src=src, dst=dest)


def create_data_files(dest: str = './textworld_data', verbose: bool = False, force: bool = False):
    """
    Creates grammar files in the target directory.

    Will NOT overwrite files if they alredy exist (checked on per-file basis).

    Parameters
    ----------
    dest :
        The path to the directory where to dump the data files into.
    verbose :
        Print when skipping an existing file.
    force :
        Overwrite all existing files.
    """

    # Make sure the destination folder exists.
    maybe_mkdir(dest)

    # Knowledge base related files.
    _maybe_copytree(LOGIC_DATA_PATH, pjoin(dest, "logic"), force=force, verbose=verbose)

    # Text generation related files.
    _maybe_copytree(TEXT_GRAMMARS_PATH, pjoin(dest, "text_grammars"), force=force, verbose=verbose)


def _to_type_tree(types):
    vtypes = []

    for vtype in sorted(types):
        if vtype.parents:
            parent = vtype.parents[0]
        else:
            parent = None
        vtypes.append(VariableType(vtype.name, vtype.name, parent))

    return VariableTypeTree(vtypes)


def _to_regex_dict(rules):
    # Sort rules for reproducibility
    # TODO: Only sort where needed
    rules = sorted(rules, key=lambda rule: rule.name)

    rules_dict = OrderedDict()
    for rule in rules:
        rules_dict[rule.name] = rule

    return RegexDict(rules_dict)


def _to_reverse_mapper(rules, reverse_rules):
    def _get_reverse_rule(rule):
        splits = rule.name.split("-")
        name = splits[0]

        reverse_rule_name = reverse_rules.get(name)
        if reverse_rule_name is None:
            return None

        if len(splits) > 1:
            extension = "-".join(splits[1:])
            reverse_rule_name += "-" + extension

        return rules.get(reverse_rule_name)

    return _get_reverse_rule


class KnowledgeBase:

    def __init__(self, logic: GameLogic, text_grammars_path: str):

        self.logic = logic
        self.text_grammars_path = text_grammars_path

        self.types = _to_type_tree(self.logic.types)
        self.rules = _to_regex_dict(self.logic.rules.values())
        self.reverse_rules = _to_reverse_mapper(self.rules, self.logic.reverse_rules)
        self.constraints = _to_regex_dict(self.logic.constraints.values())
        self.inform7_commands = {i7cmd.rule: i7cmd.command for i7cmd in self.logic.inform7.commands.values()}
        self.inform7_events = {i7cmd.rule: i7cmd.event for i7cmd in self.logic.inform7.commands.values()}
        self.inform7_predicates = {i7pred.predicate.signature: (i7pred.predicate, i7pred.source) for i7pred in self.logic.inform7.predicates.values()}
        self.inform7_variables = {i7type.name: i7type.kind for i7type in self.logic.inform7.types.values()}
        self.inform7_variables_description = {i7type.name: i7type.definition for i7type in self.logic.inform7.types.values()}
        self.inform7_addons_code = self.logic.inform7.code

    @classmethod
    def load(cls, target_dir: Optional[str] = None):
        if target_dir is None:
            if os.path.isdir("./textworld_data"):
                target_dir = "./textworld_data"
            else:
                target_dir = BUILTIN_DATA_PATH

        # Load knowledge base related files.
        paths = glob.glob(pjoin(target_dir, "logic", "*"))
        logic = GameLogic.load(paths)

        # Load text generation related files.
        text_grammars_path = pjoin(target_dir, "text_grammars")
        return cls(logic, text_grammars_path)


# On module load.
KB = KnowledgeBase.load()
