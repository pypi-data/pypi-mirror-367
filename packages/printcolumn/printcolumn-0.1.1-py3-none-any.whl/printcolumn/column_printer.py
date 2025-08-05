#!/usr/bin/env python

# PrintColumn
# Author: Ryan LaPine
# Version: 0.1.1
# Date: 2025-08-02

"""
PrintColumn module for printing formatted columns to the console.

Supports:
- Text wrapping per column
- Custom column widths
- Text and background colors (HTML-safe names)
- Bold and italic styling
- Custom column and row dividers

Requires:
- printpop: for styled console output
"""

import textwrap
import math
from typing import List
from printpop import print_formatted


class ColumnPrinter:
    """Prints formatted columns to the console with optional styling.

    To keep styling for subsequent rows, pass formats into ColumnPrinter constructor

    Attributes:
        DEFAULT_COL_WIDTH (int): Default width of each column.
        DEFAULT_COL_DIV (str): Default character between columns.
        DEFAULT_ROW_DIV (str): Default character between rows.
        CARRIAGE_RETURN (str): Newline character.
    """

    DEFAULT_COL_WIDTH = 20
    DEFAULT_COL_DIV = ' '
    DEFAULT_ROW_DIV = '-'
    CARRIAGE_RETURN = '\n'

    col_widths: List[int] = []
    col_text_colors: List[str] = []
    col_back_colors: List[str] = []
    col_bold: List[bool] = []
    col_italic: List[bool] = []
    col_divider_char: str = DEFAULT_COL_DIV
    row_divider_char: str = DEFAULT_ROW_DIV
    width: int = DEFAULT_COL_WIDTH
    bold: bool = False
    italic: bool = False
    text_color: str = ''
    back_color: str = ''

    def __init__(
        self,
        col_widths: List[int] = [],
        col_text_colors: List[str] = [],
        col_back_colors: List[str] = [],
        col_bold: List[bool] = [],
        col_italic: List[bool] = [],
        col_divider_char: str = DEFAULT_COL_DIV,
        row_divider_char: str = DEFAULT_ROW_DIV,
        width: int = DEFAULT_COL_WIDTH,
        bold: bool = False,
        italic: bool = False,
        text_color: str = '',
        back_color: str = ''
    ) -> None:
        """Initializes a ColumnPrinter instance with optional styling.

        Args:
            col_widths (List[int], optional): Widths for each column.
            col_text_colors (List[str], optional): Text colors per column (HTML-safe).
            col_back_colors (List[str], optional): Background colors per column.
            col_bold (List[bool], optional): Bold styling per column.
            col_italic (List[bool], optional): Italic styling per column.
            col_divider_char (str, optional): Character between columns.
            row_divider_char (str, optional): Character between rows.
            width (int, optional): Sets column width for entire row.
            bold (bool, optional): Sets bold value for entire row.
            italic (bool, optional): Sets italic value for entire row.
            text_color (str, optional): Sets text color for entire row.
            back_color (str, optional): Sets background color for entire row.
        """
        self.col_widths = col_widths
        self.col_text_colors = col_text_colors
        self.col_back_colors = col_back_colors
        self.col_bold = col_bold
        self.col_italic = col_italic
        self.col_divider_char = col_divider_char
        self.row_divider_char = row_divider_char
        self.width = width
        self.bold = bold
        self.italic = italic
        self.text_color = text_color
        self.back_color = back_color
       
    def print_column_row(
        self,
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
        """Prints a row of formatted columns to the console.

        Each column can be styled individually or inherit default styling from the class.
        Text is wrapped to fit column widths, and rows are printed line-by-line with optional dividers.

        Args:
            *args: Variable-length list of strings to print as columns.
            col_widths (List[int], optional): Widths for each column.
            col_text_colors (List[str], optional): Text colors per column (HTML-safe).
            col_back_colors (List[str], optional): Background colors per column.
            col_bold (List[bool], optional): Bold styling per column.
            col_italic (List[bool], optional): Italic styling per column.
            col_divider_char (str, optional): Character between columns.
            row_divider_char (str, optional): Character after each row.
            width (int, optional): Default column width if not specified.
            bold (bool, optional): Default bold styling.
            italic (bool, optional): Default italic styling.
            text_color (str, optional): Default text color.
            back_color (str, optional): Default background color.

        Returns:
            None
        """
        # Fallback to class-level defaults if not provided
        
        col_widths = col_widths or self.col_widths[:]
        col_text_colors = col_text_colors or self.col_text_colors[:]
        col_back_colors = col_back_colors or self.col_back_colors[:]
        col_bold = col_bold or self.col_bold[:]
        col_italic = col_italic or self.col_italic[:]
        if col_divider_char is None:
            col_divider_char = self.col_divider_char[:]
        if row_divider_char is None:
            row_divider_char = self.row_divider_char[:]
        
        width = width or self.width
        bold = bold if bold is not None else self.bold
        italic = italic if italic is not None else self.italic
        text_color = (text_color or self.text_color[:]).replace(' ', '')
        back_color = (back_color or self.back_color[:]).replace(' ', '')

        # Normalize inputs to lists
        col_widths = [col_widths] if isinstance(col_widths, int) else col_widths
        col_text_colors = [c.replace(' ', '') for c in col_text_colors] if isinstance(col_text_colors, list) else [col_text_colors.replace(' ', '')]
        col_back_colors = [c.replace(' ', '') for c in col_back_colors] if isinstance(col_back_colors, list) else [col_back_colors.replace(' ', '')]
        col_bold = [col_bold] if isinstance(col_bold, bool) else col_bold
        col_italic = [col_italic] if isinstance(col_italic, bool) else col_italic
        args = list(args) if args else ['']

        # Extend styling lists to match number of columns
        # if col_widths less than arg fill will width if col_widths greater than args add blank args
        if len(col_widths) < len(args):
            col_widths += [width] * (len(args) - len(col_widths))
        elif len(args) < len(col_widths):
            args += [''] * (len(col_widths) - len(args))

        num_cols = len(args)
        col_bold += [bold] * (num_cols - len(col_bold))
        col_italic += [italic] * (num_cols - len(col_italic))
        col_text_colors += [text_color] * (num_cols - len(col_text_colors))
        col_back_colors += [back_color] * (num_cols - len(col_back_colors))

        columns = self._wrap_columns(args=args,
                                     col_widths=col_widths,
                                     col_divider_char=col_divider_char)
        self._print_columns(columns,
                            col_widths,
                            col_text_colors,
                            col_back_colors,
                            col_bold,
                            col_italic,
                            col_divider_char
                            )
        # Print row divider
        row_length = self._get_row_length(col_widths=col_widths, col_divider_char=col_divider_char)
        
        self._print_row_divider(row_divider_char=row_divider_char, row_length=row_length)
     
    
    def _get_row_length(self, 
                        col_widths: List[int], 
                        col_divider_char: str
                        ) -> int:
        """Calculates the total length of a row based on column widths and divider characters.

        Args:
            col_widths (List[int]): List of widths for each column.
            col_divider_char (str): Character used to separate columns.

        Returns:
            int: Total row length including column widths and divider spacing.
        """
        row_length = sum(col_widths)
        row_length += len(col_divider_char) * (len(col_widths) - 1)
        return row_length

    def _wrap_columns(
        self,
        args: List[str],
        col_widths: List[int],
        col_divider_char: str
        ) -> List[List[str]]:
        """Wraps each column's text to fit within its specified width.

        Args:
            args (List[str]): List of text strings for each column.
            col_widths (List[int]): List of maximum widths for each column.
            col_divider_char (str): Character used to separate columns (not used in wrapping logic).

        Returns:
            List[List[str]]: A list where each element is a list of wrapped lines for a column.
        """
        columns = []
        for text, wrap_width in zip(args, col_widths):
            wrapped_lines = textwrap.fill(str(text or ' '), width=wrap_width).split('\n')
            columns.append(wrapped_lines)
        return columns


    def _print_columns(
        self,
        columns: List[List[str]],
        col_widths: List[int],
        col_text_colors: List[str],
        col_back_colors: List[str],
        col_bold: List[bool],
        col_italic: List[bool],
        col_divider_char: str
    ) -> None:
        """Prints styled columns line-by-line with alignment and dividers.

        Each column is printed with its corresponding width, text color, background color,
        and font styling. Rows are printed line-by-line, aligned to the tallest column.
        Columns are separated by a divider character.

        Args:
            columns (List[List[str]]): A list of columns, where each column is a list of wrapped text lines.
            col_widths (List[int]): Widths for each column.
            col_text_colors (List[str]): Text color for each column (e.g., 'red', 'blue').
            col_back_colors (List[str]): Background color for each column.
            col_bold (List[bool]): Whether each column's text should be bold.
            col_italic (List[bool]): Whether each column's text should be italic.
            col_divider_char (str): Character used to separate columns visually.

        Returns:
            None
        """
        row_count = max(len(col) for col in columns)

        for row_index in range(row_count):
            for col_index in range(len(columns)):
                line = columns[col_index][row_index] if row_index < len(columns[col_index]) else ''
                padded_line = line.ljust(col_widths[col_index])
                print_formatted(
                    padded_line,
                    color=col_text_colors[col_index],
                    back_color=col_back_colors[col_index],
                    bold=col_bold[col_index],
                    italic=col_italic[col_index],
                    end=''
                )
                if col_index < len(columns) - 1:
                    print_formatted(
                        col_divider_char,
                        back_color=col_back_colors[col_index],
                        end=''
                    )
            print()


    def _print_row_divider(self, 
                           row_divider_char: str, 
                           row_length: int
                           ) -> None:
        """Prints a divider line after a row of columns.

        If the divider character is a carriage return, prints a blank line.
        Otherwise, prints a repeated character string sized to match the row length.

        Args:
            row_divider_char (str): Character used to create the divider line.
                If set to '\n', a blank line is printed instead.
            row_length (int): Total width of the row, used to size the divider.

        Returns:
            None
        """
        
        if row_divider_char == self.CARRIAGE_RETURN:
            print()
        elif len(row_divider_char) > 0:
            # print 
            divider = (row_divider_char * math.ceil(row_length / len(row_divider_char)))[:row_length]
            print(divider)
                

