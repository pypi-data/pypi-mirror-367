import json
from typing import Dict

COMMON_ARGS = {"domain_identifier", "project_identifier", "remote", "profile", "region"}


def print_formatted(raw_output):
    print(json.dumps(raw_output, default=str))


def parse_execution_args(args):
    if args.get("input_config"):
        args["input_config"] = json.loads(args["input_config"])
    if args.get("output_config"):
        args["output_config"] = json.loads(args["output_config"])
    if args.get("tags"):
        args["tags"] = json.loads(args["tags"])
    if args.get("filter_by_tags"):
        args["filter_by_tags"] = json.loads(args["filter_by_tags"])
    if args.get("compute"):
        args["compute"] = json.loads(args["compute"])
    if args.get("termination_condition"):
        args["termination_condition"] = json.loads(args["termination_condition"])

    none_args = {key: value for (key, value) in args.items() if value is not None}

    return none_args


def prune_args(args: Dict) -> Dict:
    """Prunes arguments related to execution client, leaving only method-specific arguments."""
    return {k: v for k, v in args.items() if k not in COMMON_ARGS}
