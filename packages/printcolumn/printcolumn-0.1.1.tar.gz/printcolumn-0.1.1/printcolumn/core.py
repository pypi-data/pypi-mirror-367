"""
core.py

Public-facing functions for printing wrapped, styled text columns to the console using the ColumnPrinter class.
Supports custom column widths, bold, italic, and foreground/background color names.

Features:
- Prints text in wrapped columns to the console
- Supports text color and background color for over 140 HTML-safe named colors

Usage:
Use individual print_* functions for simple formatting, or print_column_row() for multiple styles.
Create reusable, styled print calls for terminal output, logs, or CLI utilities.

Author: Ryan LaPine
Version: 0.1.1
Date: 2025-08-03
"""

from typing import List, Optional
from .column_printer import ColumnPrinter
from .colors import Colors

_column_printer: Optional[ColumnPrinter] = None

def get_colors()->List[str]:
    """Return a list of all supported color names.
    Returns:
        List[str]: All color names as lowercase strings.
    """
    color_values = []
    for member in Colors:
        color_values.append(member.value)
    return color_values


def _check_printer_obj() -> ColumnPrinter:
    """Initializes and returns a singleton ColumnPrinter instance.

    Returns:
        ColumnPrinter: A shared ColumnPrinter instance.
    """
    global _column_printer
    if _column_printer is None:
        _column_printer = ColumnPrinter()
    return _column_printer


def print_column_row(
    *args,
    col_widths: List[int] = None,
    col_text_colors: List[str] = None,
    col_back_colors: List[str] = None,
    col_bold: List[bool] = None,
    col_italic: List[bool] = None,
    col_divider_char: str = None,
    row_divider_char: str = None,
    width: int = None,
    bold: bool = None,
    italic: bool = None,
    text_color: str = None,
    back_color: str = None,
) -> None:
    """Prints a row of styled columns to the console.

    Args:
        *args: Text content for each column.
        col_widths: List of widths for each column.
        col_text_colors: List of text colors for each column.
        col_back_colors: List of background colors for each column.
        col_bold: List of booleans for bold styling per column.
        col_italic: List of booleans for italic styling per column.
        col_divider_char: Character used to divide columns.
        row_divider_char: Character used to divide rows.
        width: Default width for all columns.
        bold: Default bold styling for all columns.
        italic: Default italic styling for all columns.
        text_color: Default text color for all columns.
        back_color: Default background color for all columns.
    """
    printer = _check_printer_obj()
    printer.print_column_row(
        *args,
        col_widths=col_widths,
        col_text_colors=col_text_colors,
        col_back_colors=col_back_colors,
        col_bold=col_bold,
        col_italic=col_italic,
        col_divider_char=col_divider_char,
        row_divider_char=row_divider_char,
        width=width,
        bold=bold,
        italic=italic,
        text_color=text_color,
        back_color=back_color,
    )


def initialize_column_printer(
    *args,
    col_widths: List[int] = None,
    col_text_colors: List[str] = None,
    col_back_colors: List[str] = None,
    col_bold: List[bool] = None,
    col_italic: List[bool] = None,
    col_divider_char: str = None,
    row_divider_char: str = None,
    width: int = None,
    bold: bool = None,
    italic: bool = None,
    text_color: str = None,
    back_color: str = None,
) -> None:
    """Initializes a ColumnPrinter instance with default formatting.

    Args:
        *args: Optional initial column content.
        col_widths: List of widths for each column.
        col_text_colors: List of text colors for each column.
        col_back_colors: List of background colors for each column.
        col_bold: List of booleans for bold styling per column.
        col_italic: List of booleans for italic styling per column.
        col_divider_char: Character used to divide columns.
        row_divider_char: Character used to divide rows.
        width: Default width for all columns.
        bold: Default bold styling for all columns.
        italic: Default italic styling for all columns.
        text_color: Default text color for all columns.
        back_color: Default background color for all columns.
    """
    global _column_printer
    _column_printer = ColumnPrinter(
        *args,
        col_widths=col_widths,
        col_text_colors=col_text_colors,
        col_back_colors=col_back_colors,
        col_bold=col_bold,
        col_italic=col_italic,
        col_divider_char=col_divider_char,
        row_divider_char=row_divider_char,
        width=width,
        bold=bold,
        italic=italic,
        text_color=text_color,
        back_color=back_color,
    )


def main() -> None:
    """Console test entry point for PrintColumn functionality."""
    print("\nPrintColumn - for printing wrapped text columns to the console.\n")

    ColumnPrinter().print_column_row(
        "Column 1", "Column 2", "Column 3",
        text_color="red",
        bold=True,
        col_divider_char=" |"
    )

    basic_columns = [
        "PrintColumn makes it easy to print structured columns in the console.",
        "You can customize the number of columns, widths, and divider characters.",
        "Text can also be styled with colors, and formatting."
    ]

    ColumnPrinter().print_column_row(
        *basic_columns,
        col_text_colors=["", "", "Blue"],
        col_back_colors=["", "", "White"],
        col_bold=[False, False, True],
        col_italic=[False, False, True],
        col_divider_char=" |"
    )

    print("\nPrintColumn - Custom test")
    col_count = int(input("How many columns do you want?: "))
    col_text, col_widths = [], []
    col_text_colors, col_back_colors = [], []
    col_bold, col_italic = [], []

    for i in range(col_count):
        print(f"Enter values for column {i + 1}")
        col_text.append(input(f"\tEnter text for column {i + 1}: "))
        col_widths.append(int(input(f"\tEnter width of column {i + 1}: ")))
        col_text_colors.append(input(f"\tEnter text color for column {i + 1}: "))
        col_back_colors.append(input(f"\tEnter background color for column {i + 1}: "))
        col_bold.append(input(f"\tBold column {i + 1}? (y/n): ").strip().lower() == "y")
        col_italic.append(input(f"\tItalic column {i + 1}? (y/n): ").strip().lower() == "y")

    div_char = input("Enter a char to divide the columns: ")
    row_div_char = input("Enter a char to divide rows: ")

    ColumnPrinter().print_column_row(
        *col_text,
        col_widths=col_widths,
        col_text_colors=col_text_colors,
        col_back_colors=col_back_colors,
        col_bold=col_bold,
        col_italic=col_italic,
        col_divider_char=div_char,
        row_divider_char=row_div_char
    )
    print()



if __name__ == "__main__":
    main()