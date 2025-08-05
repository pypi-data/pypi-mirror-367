"""PDF conversion utilities for autorpt."""

import argparse
from pathlib import Path
import os
import time

try:
    from docx2pdf import convert
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def convert_to_pdf(word_file, output_dir=None, max_retries=2):
    """Convert a Word document to PDF with the same name

    Args:
        word_file (str): Path to the Word document to convert
        output_dir (str, optional): Directory to save PDF. If None, saves in same directory as Word file
        max_retries (int): Maximum number of retry attempts (default: 2)

    Returns:
        tuple: (bool, str) - (success status, pdf_path or error message)
    """
    if not PDF_AVAILABLE:
        error_msg = "❌ PDF conversion not available. Please install docx2pdf: pip install docx2pdf"
        print(error_msg)
        return False, error_msg

    # Convert to Path object for easier manipulation
    word_path = Path(word_file)

    # Check if Word file exists
    if not word_path.exists():
        error_msg = f"❌ Word file not found: {word_file}"
        print(error_msg)
        return False, error_msg

    # Determine output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        pdf_path = output_path / word_path.with_suffix('.pdf').name
    else:
        pdf_path = word_path.with_suffix('.pdf')

    # Try conversion with retries
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt} for {word_path.name}...")
                time.sleep(2)  # Wait 2 seconds between retries
            else:
                print(f"🔄 Converting {word_path.name} to PDF...")

            convert(str(word_path), str(pdf_path))

            # Verify PDF was created
            if pdf_path.exists():
                file_size = os.path.getsize(pdf_path) / 1024  # KB
                print(f"✅ PDF created successfully: {pdf_path}")
                print(f"📊 PDF file size: {file_size:.1f} KB")
                return True, str(pdf_path)
            else:
                error_msg = f"❌ PDF conversion failed: {pdf_path} was not created"
                if attempt < max_retries:
                    print(f"⚠️  {error_msg} - retrying...")
                    continue
                else:
                    print(error_msg)
                    return False, error_msg

        except (OSError, PermissionError, ImportError) as e:
            error_msg = f"❌ Error converting to PDF: {e}"

            if attempt < max_retries:
                print(f"⚠️  {error_msg} - retrying...")
                # Try to kill any hanging Word processes before retry
                _cleanup_word_processes()
                continue
            else:
                print(error_msg)
                print("💡 Tips:")
                print("   - Make sure Microsoft Word is installed")
                print("   - Close the Word document if it's open")
                print("   - Try closing all Word applications and retry")
                return False, error_msg

    # Should not reach here, but just in case
    return False, "Conversion failed after all retries"


def _cleanup_word_processes():
    """Try to cleanup hanging Word processes (Windows only)"""
    try:
        import subprocess
        # Kill any hanging WINWORD.EXE processes
        subprocess.run(['taskkill', '/f', '/im', 'WINWORD.EXE'],capture_output=True, check=False)
        time.sleep(1)  # Give time for processes to terminate
    except (OSError, ImportError):
        # If cleanup fails, just continue - it's not critical
        pass


def convert_all_reports(reports_dir="reports", output_dir=None):
    """Convert all Word reports in the reports directory to PDF

    Args:
        reports_dir (str): Directory containing Word reports
        output_dir (str, optional): Directory to save PDFs. If None, saves in same directory as Word files

    Returns:
        dict: Summary of conversion results
    """
    reports_path = Path(reports_dir)

    if not reports_path.exists():
        print(f"❌ Reports directory not found: {reports_dir}")
        return {"success": 0, "failed": 0, "errors": [f"Directory not found: {reports_dir}"]}

    # Find all .docx files
    word_files = list(reports_path.glob("*.docx"))

    if not word_files:
        print(f"ℹ️  No Word documents found in {reports_dir}")
        return {"success": 0, "failed": 0, "errors": []}

    print(f"📁 Found {len(word_files)} Word document(s) to convert")

    results = {"success": 0, "failed": 0, "errors": []}

    for i, word_file in enumerate(word_files):
        print(f"\n🔄 Processing ({i+1}/{len(word_files)}): {word_file.name}")

        # Add delay between conversions to let Word close properly
        if i > 0:
            print("⏱️  Waiting for Word to close properly...")
            time.sleep(3)

        success, result_msg = convert_to_pdf(str(word_file), output_dir)

        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"{word_file.name}: {result_msg}")

    # Print summary
    print("\n📊 Conversion Summary:")
    print(f"   ✅ Successful: {results['success']}")
    print(f"   ❌ Failed: {results['failed']}")

    if results["errors"]:
        print("   📝 Errors:")
        for error in results["errors"]:
            print(f"      - {error}")

    return results


def main():
    """Main function for PDF conversion script"""
    parser = argparse.ArgumentParser(
        description='Convert Word reports to PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
python pdf.py -f report.docx                    # Convert single file
python pdf.py -a                                # Convert all reports in reports/ folder
python pdf.py -a -d reports -o pdfs             # Convert all from reports/ to pdfs/ folder
python pdf.py -f report.docx -o output          # Convert single file to output/ folder
        """)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--file', '-f', help='Convert a specific Word document to PDF')
    group.add_argument('--all', '-a', action='store_true',
                       help='Convert all Word documents in reports directory')

    parser.add_argument('--dir', '-d', default='reports',
                        help='Input directory for --all option (default: reports)')
    parser.add_argument(
        '--output', '-o', help='Output directory for PDF files (default: same as input)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    if not PDF_AVAILABLE:
        print("❌ PDF conversion not available. Please install docx2pdf:")
        print("   pip install docx2pdf")
        return 1

    if args.verbose:
        print("🔧 Verbose mode enabled")
        if args.file:
            print(f"📄 Converting file: {args.file}")
        else:
            print(f"📁 Converting all files from: {args.dir}")
        if args.output:
            print(f"📂 Output directory: {args.output}")

    success = True

    if args.file:
        # Convert single file
        success, result = convert_to_pdf(args.file, args.output)
        if not success:
            print(f"❌ Conversion failed: {result}")
    else:
        # Convert all files
        results = convert_all_reports(args.dir, args.output)
        success = results["failed"] == 0

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
