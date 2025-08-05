# autorpt

[![image](https://img.shields.io/pypi/v/autorpt.svg)](https://pypi.python.org/pypi/autorpt)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**autorpt is an automated word and pdf report generator using Excel and Markdown files**

- User works from a folder with two files in the reports folder of this repo: [content.md](https://github.com/VRConservation/autorpt/blob/main/reports/content.md) and [budget.xlsx](https://github.com/VRConservation/autorpt/blob/main/reports/budget.xlsx). The two files can be downloaded at the links provided and copied to a folder on your local drive.
- Copy and adapt the files or add your own files to generate the reports. 
- See basic usage section below for how to set it up. Videos coming soon.
- Documentation: https://VRConservation.github.io/autorpt.

## Features

- **Auto-Discovery**: Automatically finds and combines all `.md` and `.xlsx` files in your content folder
- **Excel Table Integration**: Any Excel file becomes a formatted table in your report
- **Markdown Content**: Write content in markdown format for easy editing and version control
- **Mixed Content Support**: Combine multiple markdown files and Excel tables in one report
- **Customizable Content**: Use example files or create your own content structure
- **Command Line Interface**: Simple commands for different workflows
- **Python API**: Use programmatically in your own scripts
- **Visual Charts**: Automatically generates budget comparison charts
- **Professional Formatting**: Clean, business-ready Word document output
- **PDF Conversion**: Built-in PDF generation from Word documents

## Quick Start

### Installation

```bash
pip install autorpt
```

### Basic Usage (Recommended: Folder-Based Workflow)

1. **Prepare your content in the `reports/` folder**:

    - Copy or edit the provided example files:
        - `reports/budget.xlsx` (your budget data)
        - `reports/content.md` (custom content sections)
    - Or add your own `.md` (markdown) and `.xlsx` (Excel) files to the `reports/` folder.

2. **Generate a report from all content in the folder**:

    ```bash
    # Auto-discover and combine all .md and .xlsx files in reports/
    autorpt --auto-content
    ```

    - This will create a Word document in the `reports/` folder using all detected files.

3. **Convert the generated Word report to PDF (optional)**:

    ```bash
    # Convert the latest report in reports/ to PDF
    autorpt --pdf-only
    ```

---

### Advanced Usage (Custom Files)

You can still specify custom files if needed:

```bash
# Specify input/output files
autorpt --input my_budget.xlsx --output custom_report.docx
```

### File Structure

Your project directory should contain:

```
your_project/
├── reports/             # Content folder for your files
│   ├── budget.xlsx      # Your budget data (example provided)
│   ├── content.md       # Custom content sections (example provided)
│   ├── your_data.xlsx   # Any additional Excel files
│   ├── notes.md         # Any additional markdown files
│   └── generated_reports.docx  # Auto-generated reports
└── (other project files)
```

### Customizing Content

Add your content files to the `reports/` folder:

**Example markdown file (`reports/project_notes.md`)**:

```markdown
# Summary

Your custom summary content here...

# Deliverables Progress

- Custom deliverable 1
- Custom deliverable 2

# Challenges

Current project challenges...

# Next Period Activities

Planned activities...
```

**Example Excel file**: Any `.xlsx` file with tabular data will be automatically formatted as tables in your report.

## Command Line Options

```bash
autorpt --help

# Basic report generation with auto-discovery
autorpt --auto-content               # Auto-discover files in reports/
autorpt --auto-content --content-folder "data"  # Use custom folder

# Traditional single-file approach
autorpt --input budget.xlsx --output report.docx --verbose

# PDF generation
autorpt --pdf                     # Generate report + PDF
autorpt --pdf-only                # Convert latest report to PDF
autorpt --pdf-all                 # Convert all reports to PDF

# Advanced content mixing
autorpt --markdown notes.md       # Add specific markdown file
autorpt --excel data.xlsx         # Add specific Excel file
autorpt --mixed file1.md data.xlsx  # Add multiple specific files
```

**Key Options**

- `--auto-content`: Auto-discover and combine all .md and .xlsx files from content folder
- `--content-folder`: Specify which folder to scan (default: reports)
- `--input, -i`: Input Excel file (default: budget.xlsx)
- `--output, -o`: Output Word document filename
- `--markdown, -m`: Add specific markdown file to report
- `--excel, -e`: Add specific Excel file as table
- `--mixed`: Add multiple specific files (markdown and/or Excel)
- `--pdf, -p`: Also convert the report to PDF
- `--pdf-only`: Convert most recent report to PDF (no new generation)
- `--pdf-all`: Convert all Word reports to PDF
- `--verbose, -v`: Enable verbose output

## PDF Conversion

autorpt includes built-in PDF conversion capabilities. See the `pdf/` folder for:

- Complete PDF documentation (`pdf/PDF_README.md`)
- Helper scripts for easy PDF operations
- Simple command aliases setup

Quick PDF usage:

```bash
# Built-in commands
autorpt --pdf                     # Generate new report + PDF
autorpt --pdf-only                # Convert latest report to PDF

# Helper scripts (from pdf/ folder)
.\pdf\setup-aliases.ps1           # Set up simple aliases
pdf-latest                        # Then use: convert latest to PDF
pdf-new                           # Generate new report + PDF
```

## Output

The package generates:

- Professional Word document in the `reports/` folder using sample or user added content.md and budget.xlsx files.
- Automatic integration of all markdown content as formatted sections.
- Excel data converted to professional tables with proper formatting into the Word document.
- Optional PDF conversion of reports.
- Budget comparison charts (when budget data is included).
- Summary statistics and insights from your budget data.

