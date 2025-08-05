import os
import sys
import time
from pathlib import Path
from textwrap import dedent

import click
from pydantic import ValidationError

from . import docs as docs_module
from . import git
from .agent import Agent, AgentType
from .config import CONFIG_FILENAME, CONFIG_FILENAME_PREFIX, ConfigModel, ConfigModels
from .matches import match_diff, match_files
from .printer import MatchesPrinter


# Most often used as `pullapprove`
# @click.group(invoke_without_command=True)
@click.group()
@click.pass_context
def cli(ctx):
    pass
    # if ctx.invoked_subcommand is None:
    #     ctx.invoke(review)


# Most often used as `pullapprove review`
# @cli.command()
# @click.pass_context
# def review(ctx):
#     """
#     Show changed files that need review
#     """

#     # What might we be reviewing?
#     # - PR number / url
#     # - branch
#     # - diff

#     # This is an alias for files --changed
#     ctx.invoke(files, changed=True)


@cli.command()
@click.option("--filename", default=CONFIG_FILENAME, help="Configuration filename")
def init(filename):
    """Create a new CODEREVIEW.toml"""
    config_path = Path(filename)
    if config_path.exists():
        click.secho(f"{CONFIG_FILENAME} already exists!", fg="red")
        sys.exit(1)

    # Could we use blame to guess?
    # go straight to agent?
    # gh auth status can give us the user? or ask what's their username?
    # keep it simple - agent can do more when I get to it

    contents = """
    [[scopes]]
    name = "default"
    paths = ["**/*"]
    request = 1
    require = 1
    reviewers = ["<YOU>"]

    [[scopes]]
    name = "pullapprove"
    paths = ["**/CODEREVIEW.toml"]
    request = 1
    require = 1
    """
    config_path.write_text(dedent(contents).strip() + "\n")
    click.secho(f"Created {filename}")


@cli.command()
@click.option("--quiet", is_flag=True)
def check(quiet):
    """
    Validate configuration files
    """
    errors = {}
    configs = ConfigModels(root={})

    for root, _, files in os.walk("."):
        for f in files:
            if f.startswith(CONFIG_FILENAME_PREFIX):
                config_path = Path(root) / f

                if not quiet:
                    click.echo(config_path, nl=False)
                try:
                    configs.add_config(
                        ConfigModel.from_filesystem(config_path), config_path
                    )

                    if not quiet:
                        click.secho(" -> OK", fg="green")
                except ValidationError as e:
                    if not quiet:
                        click.secho(" -> ERROR", fg="red")

                    errors[config_path] = e

    for path, error in errors.items():
        click.secho(str(path), fg="red")
        print(error)

    if errors:
        raise click.Abort("Configuration validation failed.")

    return configs


@cli.command()
@click.option("--changed", is_flag=True, help="Show only changed files")
@click.option("--staged", is_flag=True, help="Show only staged files")
@click.option("--diff", is_flag=True, help="Show diff content with matches")
@click.option(
    "--by-scope", is_flag=True, help="Organize output by scope instead of by path"
)
@click.option(
    "--scope",
    multiple=True,
    help="Filter to show only files matching these scopes (can be used multiple times)",
)
@click.pass_context
def files(ctx, changed, staged, diff, by_scope, scope):
    """
    Show files and their matching scopes
    """
    configs = ctx.invoke(check, quiet=True)

    if not configs:
        click.secho("No valid configurations found.", fg="red")
        raise click.Abort("No configurations to check.")

    if diff or staged:
        # Use git diff for these options
        diff_args = []
        if staged:
            diff_args.append("--staged")

        diff_stream = git.git_diff_stream(".", *diff_args)
        results, _ = match_diff(configs, diff_stream)
        # For diff mode, we only show files in the diff
        all_files = None
    elif changed:
        iterator = git.git_ls_changes(".")
        results = match_files(configs, iterator)
        # For changed mode, we only show changed files
        all_files = None
    else:
        # For normal mode, show all files to see gaps
        iterator = git.git_ls_files(".")
        results = match_files(configs, iterator)
        # Get all files again for the printer
        all_files = list(git.git_ls_files("."))

    printer = MatchesPrinter(results, all_files=all_files)
    if by_scope:
        printer.print_by_scope(scope_filter=scope)
    else:
        printer.print_by_path(scope_filter=scope)


@cli.command()
@click.option("--agent-command", default="claude", help="Command to run the agent")
@click.pass_context
def agent(ctx, agent_command):
    click.secho("Checking for existing configuration...", dim=True)
    try:
        configs = ctx.invoke(check)
    except click.Abort:
        click.secho("There is an error with your configuration!", fg="red")
        agent_type = AgentType.FIX
    else:
        if configs:
            click.secho("Configuration loaded successfully!", fg="green")
            # make changes to it...
            agent_type = AgentType.EDIT
        elif Path(".pullapprove.yml").exists():
            click.secho("Found existing .pullapprove.yml file.", fg="green")
            agent_type = AgentType.MIGRATE_V3
        elif (
            Path("CODEOWNERS").exists()
            or Path(".github", "CODEOWNERS").exists()
            or Path("docs", "CODEOWNERS").exists()
        ):
            click.secho("Found existing CODEOWNERS file.", fg="green")
            agent_type = AgentType.MIGRATE_CODEOWNERS
        else:
            click.secho("No configuration yet. Let's get started.")
            agent_type = AgentType.NEW

    click.secho(f"\nStarting `{agent_command}` agent...", dim=True)
    time.sleep(1)  # Simulate some delay for effect and time to read the above
    agent = Agent(agent_type)
    agent.run_command(agent_command)


@cli.command()
@click.option("--v3", is_flag=True, help="Show v3 documentation")
@click.option(
    "--list",
    "list_topics",
    is_flag=True,
    help="List all available documentation topics",
)
@click.argument("topic", required=False, default=None)
def docs(topic, v3, list_topics):
    """
    Print markdown documentation
    """
    version = "v3" if v3 else None

    if list_topics:
        # Show the list of available topics
        docs_module.list_docs_tree(version)
    elif topic:
        # Show specific topic
        if not docs_module.show_doc_by_name(topic, version):
            docs_module.show_doc_not_found(topic, version)
    else:
        # Default: show index documentation
        if not docs_module.show_doc_by_name("index", version):
            docs_module.show_doc_not_found("index", version)


@cli.command()
@click.option(
    "--check",
    "check_flag",
    is_flag=True,
    help="Exit with non-zero status if coverage is incomplete",
)
@click.argument("path", type=click.Path(exists=True), default=".")
@click.pass_context
def coverage(ctx, path, check_flag):
    """
    Calculate file coverage for review scopes
    """
    configs = ctx.invoke(check, quiet=True)

    num_matched = 0
    num_total = 0
    uncovered_files = []

    # First, get all files to know the total count for progress bar
    all_files = list(git.git_ls_files(path))

    if not all_files:
        click.echo("No files found")
        return

    # Process files with progress bar
    with click.progressbar(
        all_files, label="Analyzing coverage", show_percent=True, show_pos=True
    ) as files:
        # Use match_files to get proper scope matching including code patterns
        results = match_files(configs, iter(files))

        # Count files with and without scope matches
        for path_str, path_match in results.paths.items():
            if path_match.scopes:
                num_matched += 1
            else:
                uncovered_files.append(path_str)
            num_total += 1

        # Also count files that weren't in the results (no scope matches at all)
        for f in all_files:
            if f not in results.paths:
                uncovered_files.append(f)
                num_total += 1

    percentage = (num_matched / num_total) * 100

    # Display coverage statistics
    if num_matched == num_total:
        click.secho(f"\n✓ {num_matched}/{num_total} files covered (100.0%)", fg="green")
    else:
        # Show uncovered files
        if uncovered_files:
            click.echo("\nUncovered files:")
            for file in sorted(uncovered_files)[:10]:  # Show first 10
                click.echo(f"  - {file}")
            if len(uncovered_files) > 10:
                click.echo(f"  ...and {len(uncovered_files) - 10} more")

        click.secho(
            f"\n{num_matched}/{num_total} files covered ({percentage:.1f}%)",
            fg="yellow",
        )

    if check_flag and num_matched != num_total:
        sys.exit(1)


# list - find open PRs, find status url and send json request (needs PA token)
