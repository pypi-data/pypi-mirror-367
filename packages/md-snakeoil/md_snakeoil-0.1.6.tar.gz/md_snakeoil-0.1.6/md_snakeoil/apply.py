import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent, indent


class Formatter:
    """
    Format and lint Python code blocks within markdown files.

    Args:
        line_length: Maximum line length for formatted code
        rules: Tuple of rules to apply during linting
    """

    def __init__(
        self, line_length: int = 79, rules: tuple[str, ...] = ("I", "W")
    ) -> None:
        self.line_length = line_length
        self.rules = rules

    @staticmethod
    def read_markdown(file_path: str | Path) -> str:
        """Read a markdown file and return the content as string."""
        return Path(file_path).read_text(encoding="utf-8")

    @staticmethod
    def write_markdown(content: str, file_path: Path) -> None:
        """Write content to a markdown file."""
        file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def detect_indent(text: str) -> str:
        """Detect the indentation of the first non-empty line."""
        for line in text.splitlines():
            if line.strip():
                # match spaces or tabs at the beginning of the line
                return re.match(r"^\s*", line).group()
        return ""  # empty string, if no indentation is found

    def format_single_block(self, code: str, quiet: bool = True) -> str:
        try:
            # detect and remove indentation
            indent_str = self.detect_indent(code)
            dedented_code = dedent(code)

            # format code with ruff
            formatted = subprocess.check_output(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    "--line-length",
                    str(self.line_length),
                    "-",
                ],
                input=dedented_code,
                encoding="utf-8",
                stderr=subprocess.DEVNULL if quiet else None,
            )

            if len(self.rules) != 0:
                # lint code with ruff
                linted = subprocess.check_output(
                    [
                        sys.executable,
                        "-m",
                        "ruff",
                        "check",
                        f"--select={','.join([*self.rules])}",
                        "--fix",
                        "-",
                    ],
                    input=formatted,
                    encoding="utf-8",
                    stderr=subprocess.DEVNULL if quiet else None,
                )
                # reapply original indentation to linted code
                return indent(linted.rstrip(), indent_str)

            # if no linting rules, just reapply indentation to formatted code
            return indent(formatted.rstrip(), indent_str)

        except subprocess.CalledProcessError as e:
            # if formatting fails, keep original code
            print(f"Warning: Failed to format code block: {e}")
            return code

    def format_markdown_content(
        self, *, file_name: str, content: str, quiet: bool = True
    ) -> str:
        """Replace code blocks in markdown content with formatted versions."""
        result = content
        offset = 0

        # look for particular info strings of fenced
        # code blocks - e.g. "python", "py"; works with attributes
        # like ```python title="example" ... as well; plus handles indentation
        short_names = ["python", "py", "Python", "python3", "py3"]
        info_strings = "|".join(short_names) + "| " + "| ".join(short_names)

        pattern = (
            rf"([ \t]*)(```(?:{info_strings})(?:[^\n]*)\n)(.*?)([ \t]*```)"  # noqa: E501
        )

        matches = list(re.finditer(pattern, content, re.DOTALL))
        if len(matches) == 0:
            print(f"No Python code blocks found in {file_name}.")
        else:
            for match in matches:
                leading_indent = match.group(1)  # capture leading whitespace
                lang_tag = match.group(2)
                original_block = match.group(3)
                closing_backticks = match.group(
                    4
                )  # capture closing backticks with their indent

                # format the block while preserving indentation
                formatted_block = self.format_single_block(
                    original_block, quiet=quiet
                )

                # calculate positions considering the offset
                start = match.start() + offset
                end = match.end() + offset

                # reconstruct the code block with original indentation
                new_block = f"{leading_indent}{lang_tag}{formatted_block}\n{closing_backticks}"  # noqa: E501

                # replace the entire block
                result = result[:start] + new_block + result[end:]

                # update offset
                offset += len(new_block) - (end - start)

        return result

    def run(
        self,
        file_path: str | Path,
        inplace: bool = True,
        output_path: str | Path | None = None,
        quiet: bool = True,
    ) -> None:
        """
        Format Python code blocks in a markdown file.

        Args:
            file_path: Markdown file path
            inplace: If True, update the file in place
            output_path: If provided, write formatted content to this path
                        (ignored if inplace=True)
            quiet: If True, suppress ruff output
        """
        if not inplace and output_path is None:
            raise ValueError("Provide an output_path if inplace=False.")

        file_path = Path(file_path)
        markdown = self.read_markdown(file_path)
        formatted_content = self.format_markdown_content(
            file_name=str(file_path), content=markdown, quiet=quiet
        )

        if inplace:
            self.write_markdown(formatted_content, file_path)
        else:
            self.write_markdown(formatted_content, Path(output_path))
