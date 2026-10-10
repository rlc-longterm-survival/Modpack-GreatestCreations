"""Two-directory toolkit for the modpack tree.

Layout maintained by this toolkit::

    <category>-sorted/    source of truth (git-tracked, packwiz-ignored)
    <category>/           derived flat tree of symlinks (git-ignored)

``<category>`` is normally ``mods``.  The toolkit only manipulates these two
directories; it never runs packwiz and never edits packwiz indexes.

Disabled entries
----------------
Any file or directory whose name starts with ``.`` or ends with ``.disabled``
is treated as non-existent.

Symlinks
--------
Symlinks are always real, system-native links created with ``os.symlink``.
There is no fallback to hardlinks or copies: if link creation is refused
(for example on Windows with Developer Mode off) the command fails.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import NoReturn
import tomllib

DISABLED_SUFFIX = ".disabled"


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #

def fail(message: str) -> NoReturn:
    """Print *message* to stderr and exit with status 1."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def is_disabled(name: str) -> bool:
    """Return whether *name* marks a disabled file or directory."""
    return name.startswith(".") or name.endswith(DISABLED_SUFFIX)


def require_dir(path: Path, role: str) -> None:
    if not path.is_dir():
        fail(f"{role} directory does not exist: {path}")


def category_dirs(category: str) -> tuple[Path, Path]:
    """Return the ``(derived, source)`` directory pair for *category*."""
    return Path(category), Path(f"{category}-sorted")


def iter_enabled_files(root: Path):
    """Yield regular files and valid file symlinks under *root*, recursively.

    Disabled files and disabled directories are skipped entirely, and broken
    symlinks are ignored.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not is_disabled(name)]
        for name in filenames:
            if is_disabled(name):
                continue
            path = Path(dirpath) / name
            if path.is_file():
                yield path


def symlink_relative(target: Path, link: Path) -> None:
    """Create *link* as a relative symlink to *target*.

    Raises ``OSError`` when the link cannot be created; callers translate that
    into a clean failure.  No hardlink/copy fallback is attempted.
    """
    os.symlink(os.path.relpath(target, start=link.parent), link)


# --------------------------------------------------------------------------- #
# flatten
# --------------------------------------------------------------------------- #

def cmd_flatten(args: argparse.Namespace) -> None:
    derived, source = category_dirs(args.category)
    require_dir(source, "source")

    by_name: dict[str, Path] = {}
    for path in sorted(iter_enabled_files(source)):
        previous = by_name.get(path.name)
        if previous is not None:
            fail(f"basename clash in {source}: {previous} and {path}")
        by_name[path.name] = path

    try:
        derived.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"failed to create derived directory {derived}: {exc}")

    # Non-symlink entries are kept (with a warning), so a name clash with one
    # of them is fatal.  Hidden names cannot clash: sources never start with '.'.
    kept = {
        entry.name
        for entry in os.scandir(derived)
        if not entry.name.startswith(".") and not entry.is_symlink()
    }
    clashes = sorted(kept.intersection(by_name))
    if clashes:
        fail("refusing to overwrite non-symlink entries in derived directory: "
             + ", ".join(clashes))

    for entry in os.scandir(derived):
        if entry.name.startswith("."):
            continue
        if entry.is_symlink():
            os.unlink(entry.path)
        else:
            warn(f"keeping non-symlink entry in derived directory: {entry.path}")

    for name, path in sorted(by_name.items()):
        link = derived / name
        if os.path.lexists(link):
            fail(f"refusing to overwrite existing path: {link}")
        try:
            symlink_relative(path, link)
        except OSError as exc:
            fail(f"failed to create symlink {link} -> {path}: {exc}")

    print(f"flattened {len(by_name)} file(s) from {source} into {derived}")


# --------------------------------------------------------------------------- #
# sort
# --------------------------------------------------------------------------- #

def parse_subfolder(argument: str, source_name: str) -> list[str]:
    """Turn the ``sort`` destination argument into path segments.

    Accepts ``<category>-sorted/<subfolder>`` or a bare ``<subfolder>``, rejects
    absolute paths and ``..`` segments.
    """
    normalized = argument.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) >= 2 and normalized[1] == ":"):
        fail(f"subfolder must be a relative path: {argument!r}")

    segments = [segment for segment in normalized.split("/") if segment not in ("", ".")]
    if ".." in segments:
        fail(f"subfolder must not contain '..': {argument!r}")
    if segments and segments[0] == source_name:
        segments = segments[1:]
    return segments


def cmd_sort(args: argparse.Namespace) -> None:
    derived, source = category_dirs(args.category)
    require_dir(derived, "derived")
    require_dir(source, "source")

    destination = source.joinpath(*parse_subfolder(args.subfolder, source.name))
    if not destination.is_dir():
        if not args.create:
            fail(f"destination subfolder does not exist (pass -c to create): {destination}")
        try:
            destination.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            fail(f"failed to create destination subfolder {destination}: {exc}")

    candidates = sorted(
        Path(entry.path)
        for entry in os.scandir(derived)
        if not entry.name.startswith(".") and entry.is_file(follow_symlinks=False)
    )

    for path in candidates:
        target = destination / path.name
        if os.path.lexists(target):
            fail(f"refusing to overwrite existing path: {target}")

    moved = 0
    for path in candidates:
        target = destination / path.name
        try:
            shutil.move(str(path), str(target))
        except OSError as exc:
            fail(f"failed to move {path} -> {target}: {exc}")
        try:
            symlink_relative(target, path)
        except OSError as exc:
            # Keep both trees consistent so a retry can be a plain rerun.
            try:
                shutil.move(str(target), str(path))
            except OSError as rollback_exc:
                warn(f"failed to roll back {target} -> {path}: {rollback_exc}")
            fail(f"failed to create symlink {path} -> {target}: {exc}")
        moved += 1

    print(f"sorted {moved} file(s) from {derived} into {destination}")


# --------------------------------------------------------------------------- #
# dangerously-prune
# --------------------------------------------------------------------------- #

def collect_derived_names(derived: Path) -> set[str]:
    """Basenames in *derived* that a sorted file may legitimately match.

    Counts regular files, valid file symlinks and broken symlinks.  Symlinks to
    directories and real directories do not count.
    """
    names: set[str] = set()
    for entry in os.scandir(derived):
        if entry.name.startswith("."):
            continue
        if entry.is_symlink():
            if not entry.is_dir(follow_symlinks=True):
                names.add(entry.name)
        elif entry.is_file(follow_symlinks=False):
            names.add(entry.name)
    return names


def remove_empty_parents(start: Path, stop: Path) -> None:
    """Remove directories made empty by a removal, never removing *stop*."""
    stop = Path(os.path.abspath(stop))
    current = Path(os.path.abspath(start))
    while current != stop and stop in current.parents:
        try:
            if any(current.iterdir()):
                return
            current.rmdir()
        except OSError:
            return
        current = current.parent


def cmd_prune(args: argparse.Namespace) -> None:
    derived, source = category_dirs(args.category)
    require_dir(derived, "derived")
    require_dir(source, "source")

    present = collect_derived_names(derived)
    marked = sorted(path for path in iter_enabled_files(source) if path.name not in present)

    if not marked:
        print("nothing to prune")
        return

    print("marked for removal:")
    for path in marked:
        print(f"  {path}")

    if args.dry_run:
        print("dry run: nothing removed")
        return

    if not args.force:
        try:
            answer = input(f"Remove {len(marked)} file(s)? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("aborted")
            return

    removed = 0
    for path in marked:
        try:
            os.unlink(path)
        except OSError as exc:
            warn(f"failed to remove {path}: {exc}")
            continue
        removed += 1
        if args.remove_empty_dirs:
            remove_empty_parents(path.parent, source)
    print(f"removed {removed} file(s)")

# --------------------------------------------------------------------------- #
# config writing
# --------------------------------------------------------------------------- #

def cmd_write_config(args: argparse.Namespace):
    with open("pack.toml", "rb") as f:
        data = tomllib.load(f)
    pack_name = data['name']
    version = data['version']
    mc_version = data['versions']['minecraft']
    title = f'{pack_name} v{version} (Minecraft* {mc_version})'
    open('config/customwindowtitle-client.toml', 'w', encoding='utf-8').write(
        f'title = {json.dumps(title)}\n'
    )
    print('Derived MC config generated.')

# --------------------------------------------------------------------------- #
# determine artifact name
# --------------------------------------------------------------------------- #

def cmd_artifact_name(args: argparse.Namespace):
    with open("pack.toml", "rb") as f:
        data = tomllib.load(f)
    pack_name = data['name']
    version = data['version']
    title = f'{pack_name} v{version} ({args.target}).zip'
    print(title)

# --------------------------------------------------------------------------- #
# command line
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="toolkit.py",
        description="Maintain the <category> / <category>-sorted two-directory layout.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    flatten = subparsers.add_parser(
        "flatten",
        help="rebuild <category> as symlinks into <category>-sorted",
    )
    flatten.add_argument("category", help="derived category directory name, e.g. mods")
    flatten.set_defaults(func=cmd_flatten)

    sort = subparsers.add_parser(
        "sort",
        help="move new regular files from <category> into <category>-sorted",
    )
    sort.add_argument("category", help="derived category directory name, e.g. mods")
    sort.add_argument(
        "-c", "--create", action="store_true",
        help="create the destination subfolder if it does not exist",
    )
    sort.add_argument(
        "subfolder",
        help="destination relative to <category>-sorted, "
             "e.g. mods-sorted/optim-optional or optim-optional",
    )
    sort.set_defaults(func=cmd_sort)

    prune = subparsers.add_parser(
        "dangerously-prune",
        help="remove <category>-sorted files with no matching basename in <category>",
    )
    prune.add_argument("category", help="derived category directory name, e.g. mods")
    prune.add_argument(
        "-d", "--remove-empty-dirs", action="store_true",
        help="remove parent subfolders left empty by the removals",
    )
    prune.add_argument(
        "-f", "--force", action="store_true",
        help="remove without asking for confirmation",
    )
    prune.add_argument(
        "--dry-run", action="store_true",
        help="list what would be removed and exit",
    )
    prune.set_defaults(func=cmd_prune)

    write_config = subparsers.add_parser(
        "write-config",
        help="generate derived MC config files",
    )
    write_config.set_defaults(func=cmd_write_config)

    artifact_name = subparsers.add_parser(
        "artifact-name",
        help="determine the name for artifact",
    )
    artifact_name.add_argument(
        "--target",
        required=True,
        help="Specifier of the target platform/side, included in the artifact file name."
    )
    artifact_name.set_defaults(func=cmd_artifact_name)

    return parser


def main(argv: list[str] | None = None) -> int:
    if not os.path.exists('pack.toml'):
        print('Toolkit can only be run in modpack root dir.', file=sys.stderr)
        return 2

    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
