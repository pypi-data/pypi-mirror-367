"""
Tooling to extract code snippets from docs and then run
commands on them (syntax checking, formatting, etc.)

This was moved from cfengine/documentation repo.

TODO: This code needs several adjustments to better fit into
      the CFEngine CLI.
"""

import os
import json
from shutil import which
import subprocess

import markdown_it
from cfbs.pretty import pretty_file

from cfengine_cli.utils import UserError


IGNORED_DIRS = [".git"]


def count_indent(string: str) -> int:
    stripped = string.lstrip(" ")
    return len(string) - len(stripped)


def extract_inline_code(path, languages):
    """extract inline code, language and filters from markdown"""

    with open(path, "r") as f:
        content = f.read()

    lines = content.split("\n")

    md = markdown_it.MarkdownIt("commonmark")
    ast = md.parse(content)

    for child in ast:

        if child.type != "fence":
            continue

        if not child.info:
            continue

        info_string = child.info.split()
        language = info_string[0]
        flags = info_string[1:]
        if flags and flags[0][0] == "{" and flags[-1][-1] == "}":
            flags[0] = flags[0][1:]
            flags[-1] = flags[-1][0:-1]
        if language in languages:
            assert child.map is not None
            # Index of first line to include, the triple backtick fence:
            first_line = child.map[0]
            # The first line is triple backticks preceded by some spaces, count those:
            indent = count_indent(lines[first_line])
            # Index of first line to NOT include, the line after closing triple backtick:
            last_line = child.map[1]
            yield {
                "language": language,
                "flags": flags,
                "first_line": child.map[0],
                "last_line": child.map[1],
                "indent": indent,
                "lines": lines[
                    first_line:last_line
                ],  # Includes backtick fences on both sides
            }


def get_markdown_files(start, languages):
    """locate all markdown files and call extract_inline_code on them"""

    if os.path.isfile(start):
        return {
            "files": {
                start: {"code-blocks": list(extract_inline_code(start, languages))}
            }
        }

    return_dict = {"files": {}}
    for root, dirs, files in os.walk(start):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            if f.endswith(".markdown") or f.endswith(".md"):
                path = os.path.join(root, f)
                return_dict["files"][path] = {
                    "code-blocks": list(extract_inline_code(path, languages))
                }

    return return_dict


def fn_extract(origin_path, snippet_path, _language, first_line, last_line):
    try:
        with open(origin_path, "r") as f:
            content = f.read()

        code_snippet = "\n".join(content.split("\n")[first_line + 1 : last_line - 1])

        with open(snippet_path, "w") as f:
            f.write(code_snippet)
    except IOError:
        raise UserError(f"Couldn't open '{origin_path}' or '{snippet_path}'")


def fn_check_syntax(origin_path, snippet_path, language, first_line, _last_line):
    snippet_abs_path = os.path.abspath(snippet_path)

    if not os.path.exists(snippet_path):
        raise UserError(
            f"Couldn't find the file '{snippet_path}'. Run --extract to extract the inline code."
        )

    match language:
        case "cf":
            try:
                p = subprocess.run(
                    ["/var/cfengine/bin/cf-promises", snippet_abs_path],
                    capture_output=True,
                    text=True,
                )
                err = p.stderr

                if err:
                    err = err.replace(snippet_abs_path, f"{origin_path}:{first_line}")
                    print(err)
            except OSError:
                raise UserError(f"'{snippet_abs_path}' doesn't exist")
            except ValueError:
                raise UserError("Invalid subprocess arguments")
            except subprocess.CalledProcessError:
                raise UserError(f"Couldn't run cf-promises on '{snippet_abs_path}'")
            except subprocess.TimeoutExpired:
                raise UserError("Timed out")
        case "json":
            try:
                with open(snippet_abs_path, "r") as f:
                    json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                raise UserError(f"Error when checking '{snippet_abs_path}': {str(e)}")
            except Exception as e:
                print(str(e))
                raise UserError(f"Unknown error when checking '{snippet_abs_path}'")


def fn_check_output():
    pass


def fn_replace(origin_path, snippet_path, _language, first_line, last_line, indent):
    try:
        with open(snippet_path, "r") as f:
            pretty_content = f.read().strip()

        with open(origin_path, "r") as f:
            origin_lines = f.read().split("\n")
            pretty_lines = pretty_content.split("\n")

            pretty_lines = [" " * indent + x for x in pretty_lines]

            offset = len(pretty_lines) - len(
                origin_lines[first_line + 1 : last_line - 1]
            )

        origin_lines[first_line + 1 : last_line - 1] = pretty_lines

        with open(origin_path, "w") as f:
            f.write("\n".join(origin_lines))
    except FileNotFoundError:
        raise UserError(
            f"Couldn't find the file '{snippet_path}'. Run --extract to extract the inline code."
        )
    except IOError:
        raise UserError(f"Couldn't open '{origin_path}' or '{snippet_path}'")

    return offset  # TODO: offset can be undefined here


def fn_autoformat(_origin_path, snippet_path, language, _first_line, _last_line):
    match language:
        case "json":
            try:
                pretty_file(snippet_path)
            except FileNotFoundError:
                raise UserError(
                    f"Couldn't find the file '{snippet_path}'. Run --extract to extract the inline code."
                )
            except PermissionError:
                raise UserError(f"Not enough permissions to open '{snippet_path}'")
            except IOError:
                raise UserError(f"Couldn't open '{snippet_path}'")
            except json.decoder.JSONDecodeError:
                raise UserError(f"Invalid json in '{snippet_path}'")


def _markdown_code_checker(
    path, syntax_check, extract, replace, autoformat, languages, output_check, cleanup
):
    supported_languages = {"cf3": "cf", "json": "json", "yaml": "yml"}

    if not os.path.exists(path):
        raise UserError("This path doesn't exist")

    if (
        syntax_check
        and "cf3" in languages
        and not which("/var/cfengine/bin/cf-promises")
    ):
        raise UserError("cf-promises is not installed")

    for language in languages:
        if language not in supported_languages:
            raise UserError(
                f"Unsupported language '{language}'. The supported languages are: {", ".join(supported_languages.keys())}"
            )

    parsed_markdowns = get_markdown_files(path, languages)

    for origin_path in parsed_markdowns["files"].keys():
        offset = 0
        for i, code_block in enumerate(
            parsed_markdowns["files"][origin_path]["code-blocks"]
        ):

            # adjust line numbers after replace
            for cb in parsed_markdowns["files"][origin_path]["code-blocks"][i:]:
                cb["first_line"] += offset
                cb["last_line"] += offset

            language = supported_languages[code_block["language"]]
            snippet_path = f"{origin_path}.snippet-{i + 1}.{language}"

            flags = code_block["flags"]
            if "noextract" in flags or "skip" in flags:
                # code block was marked to be skipped
                continue
            if extract:
                fn_extract(
                    origin_path,
                    snippet_path,
                    language,
                    code_block["first_line"],
                    code_block["last_line"],
                )

            if syntax_check and "novalidate" not in code_block["flags"]:
                try:
                    fn_check_syntax(
                        origin_path,
                        snippet_path,
                        language,
                        code_block["first_line"],
                        code_block["last_line"],
                    )
                except Exception as e:
                    if cleanup:
                        os.remove(snippet_path)
                    raise e

            if autoformat and "noautoformat" not in code_block["flags"]:
                fn_autoformat(
                    origin_path,
                    snippet_path,
                    language,
                    code_block["first_line"],
                    code_block["last_line"],
                )

            if output_check and "noexecute" not in code_block["flags"]:
                fn_check_output()

            if replace and "noreplace" not in code_block["flags"]:
                offset = fn_replace(
                    origin_path,
                    snippet_path,
                    language,
                    code_block["first_line"],
                    code_block["last_line"],
                    code_block["indent"],
                )
            if cleanup:
                os.remove(snippet_path)

def _run_black():
    path = "."
    assert os.path.isdir(path)
    try:
        subprocess.run(
            ["black", path],
            capture_output=True,
            text=True,
            check=True,
            cwd=path,
        )
    except:
        raise UserError("Encountered an error running prettier")


def _run_prettier():
    path = "."
    assert os.path.isdir(path)
    try:
        subprocess.run(
            ["prettier", "--write", "**.markdown", "**.md"],
            capture_output=True,
            text=True,
            check=True,
            cwd=path,
        )
    except:
        raise UserError("Encountered an error running prettier")

def update_docs() -> int:
    """
    Iterate through entire docs repo (.), autoformatting as much as possible:
    - python code with black
    - markdown files with prettier
    - code blocks inside markdown files are formatted for the formats supported by prettier
    - JSON code blocks are re-formatted by cfbs pretty (we plan to expand this to CFEngine code blocks)

    Run by the command:
    cfengine dev docs-format
    """
    _run_black()
    _run_prettier()
    _markdown_code_checker(
        path=".",
        syntax_check=False,
        extract=True,
        replace=True,
        autoformat=True,
        languages=["json"],
        output_check=False,
        cleanup=True,
    )
    return 0


def check_docs() -> int:
    """
    Run checks / tests on docs.
    Currently only JSON syntax checking.

    Run by the command:
    cfengine dev docs-checking"""
    _markdown_code_checker(
        path=".",
        syntax_check=True,
        extract=True,
        replace=False,
        autoformat=False,
        languages=["json"],
        output_check=False,
        cleanup=True,
    )
    return 0
