from collections.abc import Iterator
from pathlib import Path

import click


def get_docs_dir(version: str | None = None) -> Path:
    """Get the path to the documentation directory."""
    base_dir = Path(__file__).parent / "docs"
    if version:
        return base_dir / version
    return base_dir


def get_all_docs(version: str | None = None) -> list[Path]:
    """Get all markdown documentation files sorted by path."""
    docs_dir = get_docs_dir(version)
    return sorted(docs_dir.rglob("*.md"))


def remove_frontmatter(content: str) -> str:
    """
    Remove YAML frontmatter from markdown content.
    """
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        # Find the closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                # Return content after frontmatter
                return "\n".join(lines[i + 1 :])
    return content


def iterate_markdown(content: str) -> Iterator[str]:
    """
    Iterator that does basic markdown formatting for a Click pager.

    Headings are yellow and bright, code blocks are indented.
    """
    in_code_block = False
    for line in content.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block

        if in_code_block:
            yield click.style(line, dim=True)
        elif line.startswith("# "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("## "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("### "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("#### "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("##### "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("###### "):
            yield click.style(line, fg="yellow", bold=True)
        elif line.startswith("**") and line.endswith("**"):
            yield click.style(line, bold=True)
        elif line.startswith("> "):
            yield click.style(line, italic=True)
        else:
            yield line

        yield "\n"


def list_docs_tree(version: str | None = None) -> None:
    """Display available documentation in a tree format."""
    docs_dir = get_docs_dir(version)
    docs_files = get_all_docs(version)

    # Group files by directory for tree display
    dirs: dict[str, list[str]] = {}
    for doc in docs_files:
        rel_path = doc.relative_to(docs_dir)
        dir_name = str(rel_path.parent) if rel_path.parent != Path(".") else ""
        if dir_name not in dirs:
            dirs[dir_name] = []
        dirs[dir_name].append(rel_path.stem)

    # Display as tree
    for dir_name in sorted(dirs.keys()):
        if dir_name:
            click.echo(f"{dir_name}/")
            for file in sorted(dirs[dir_name]):
                click.echo(f"  {file}")
        else:
            for file in sorted(dirs[dir_name]):
                click.echo(file)


def show_all_docs(version: str | None = None) -> None:
    """Display all documentation concatenated with separators."""
    docs_dir = get_docs_dir(version)
    docs_files = get_all_docs(version)

    # Concatenate all docs with headers
    all_content = []
    for doc_file in docs_files:
        rel_path = doc_file.relative_to(docs_dir)
        content = remove_frontmatter(doc_file.read_text())
        # Add a separator and file path header
        all_content.append(f"\n{'=' * 60}\n{rel_path}\n{'=' * 60}\n")
        all_content.append(content)

    click.echo_via_pager(iterate_markdown("\n".join(all_content)))


def show_doc_by_name(name: str, version: str | None = None) -> bool:
    """
    Display a specific documentation file by name.
    Returns True if found, False otherwise.
    """
    docs_dir = get_docs_dir(version)
    docs_files = get_all_docs(version)

    # Try exact match first
    for f in docs_files:
        if f.stem == name:
            content = remove_frontmatter(f.read_text())
            click.echo_via_pager(iterate_markdown(content))
            return True

    # Try matching with directory prefix (e.g., "scopes/paths")
    for f in docs_files:
        rel_path = f.relative_to(docs_dir).with_suffix("")
        if str(rel_path) == name:
            content = remove_frontmatter(f.read_text())
            click.echo_via_pager(iterate_markdown(content))
            return True

    return False


def show_doc_not_found(name: str, version: str | None = None) -> None:
    """Display error message when a doc is not found."""
    version_str = f" (v{version})" if version else ""
    click.secho(f"Documentation for '{name}' not found{version_str}.", fg="red")
    click.echo("\nAvailable docs:")
    list_docs_tree(version)


def show_default_doc(version: str | None = None) -> None:
    """Display the default documentation (index.md)."""
    docs_dir = get_docs_dir(version)
    index_file = docs_dir / "index.md"

    if index_file.exists():
        content = remove_frontmatter(index_file.read_text())
        click.echo_via_pager(iterate_markdown(content))
    else:
        version_str = f" for v{version}" if version else ""
        click.echo(
            f"Use --list to see available documentation{version_str} or specify a doc name."
        )


def get_doc_content(name: str, version: str | None = None) -> str | None:
    """
    Get the content of a specific documentation file by name.
    Returns the content with frontmatter removed, or None if not found.
    """
    docs_dir = get_docs_dir(version)
    docs_files = get_all_docs(version)

    # Try exact match first
    for f in docs_files:
        if f.stem == name:
            return remove_frontmatter(f.read_text())

    # Try matching with directory prefix (e.g., "scopes/paths")
    for f in docs_files:
        rel_path = f.relative_to(docs_dir).with_suffix("")
        if str(rel_path) == name:
            return remove_frontmatter(f.read_text())

    return None
