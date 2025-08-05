<p align="center">
  <img src="https://github.com/rlapine/printcolumn/blob/main/assets/print_column_logo.png?raw=true" alt="PrintColumn logo" width="400"/>
</p>

---

## PrintColumn V 0.11

A lightweight Python utility for printing styled, wrapped columns to the console.   Supports text wrapping, color formatting, bold/italic styling, and customizable dividers — perfect for CLI tools, debugging output, or readable logs.

---

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/rlapine/printcolumn?style=social)](https://github.com/rlapine/printcolumn/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/rlapine/printcolumn?style=social)](https://github.com/rlapine/printcolumn/network/members)

---

## Overview

PrintColumn prints clean, customizable columns to the console. Designed for clarity and flexibility, it helps you format tabular text with style—perfect for CLI tools, logs, or readable summaries.

# Features
- Custom Column Widths – Define exact widths for each column
- Text Wrapping – Automatically wraps text within column boundaries
- Text & Background Colors – Use HTML-safe color names for styling
- Bold & Italic Styling – Add emphasis with simple formatting options
- Custom Dividers – Configure column and row separators for visual clarity

# Requirements
- printpop – Handles styled console output (colors, bold, italic)

---

## Installation

`pip install printcolumn`

---

## API Overview

- `initialize_column_printer(
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
    ) -> None`: Initializes a ColumnPrinter instance with default formatting.
- `def print_column_row(
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
    ) -> None`: Prints a row of styled columns to the console.
- `ColumnPrinter`: Printer class. Instantiate with format values for subsequent calls to print_column_row
- `Colors`: Enum of available colors. Returns string name that can be passed as color arguments to print_column_row
- `get_colors()->List[str]`: Returns list of supported colors

---

## Usage Examples

```
from printcolumn import print_column_row
print("\nPrintColumn - for printing wrapped text columns to the console.\n")

# Prints a header row of three columns
ColumnPrinter().print_column_row(
    "Column 1", "Column 2", "Column 3",
    text_color="red",
    bold=True,
    col_divider_char=" |"
)

# holds text for three columns
basic_columns = [
    "PrintColumn makes it easy to print structured columns in the console.",
    "You can customize the number of columns, widths, and divider characters.",
    "Text can also be styled with colors, and formatting."
]

# prints a row with three columns
ColumnPrinter().print_column_row(
    *basic_columns,
    col_text_colors=["", "", "Blue"],
    col_back_colors=["", "", "White"],
    col_bold=[False, False, True],
    col_italic=[False, False, True],
    col_divider_char=" |"
)
```

<p align="left">
  <img src="https://github.com/rlapine/printcolumn/blob/main/assets/colorprinter_usage_output.png?raw=true" alt="console output" width="800"/>
</p>

---

## Supported Colors

ColorPrinter includes support for over 140 HTML name safe colors

```
[
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "bisque", "blanchedalmond", "blue", "blueviolet", "brown",
    "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue",
    "darkcyan", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred",
    "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray",
    "dimgrey", "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "gray",
    "green", "greenyellow", "grey", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender",
    "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey",
    "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen",
    "linen", "magenta", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise",
    "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin", "navy", "oldlace", "olive", "olivedrab", "orange",
    "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink",
    "plum", "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown",
    "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen",
    "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke",
    "yellow", "yellowgreen"
]
```

---

## Built-in demo:

`python printcolumn`

---

## 📁 Package Structure
```
printcolumn/
├── printcolumn/              
│   ├── core.py             # Public functions and console test
│   ├── colors.py           #supported colors enum
│   ├── column_printer.py   # Core ANSI logic
│   ├── __init__.py         # Package init
├── assets/                # Folder for images, badges, or other static assets
│   ├── print_column_logo.png      # Logo 
│   └── colorprinter_usage_output.png   # Console output 
├── pyproject.toml
├── README.md   # Documentation
├── setup.cfg
└── setup.py             

```

---

## 🤝 Contributing

Pull requests welcome! If you spot formatting quirks, want to add new named colors or extend features (like terminal detection or theme presets), feel free to collaborate.

To contribute:

Fork the repo

Add your changes with Google-style comments

Submit a pull request with a clear description

For style consistency, follow the Python Google Style Guide for functions and comments.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Created by Ryan LaPine [@rlapine](https://github.com/rlapine) — a technically skilled developer focused on clarity, maintainability, and audience-ready documentation. This class is part of a broader effort to build reusable, well-documented tools for data-driven projects.

---

## 📬 Contact

Feel free to reach out with questions or collaboration ideas:

📧 github.stunt845@passinbox.com  
🔗 GitHub: [@rlapine](https://github.com/rlapine)