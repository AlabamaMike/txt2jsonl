#!/usr/bin/env python3
"""
txt2jsonl - Convert plaintext files to JSONL format for model training

A command-line utility that converts plaintext files into JSONL format
suitable for training and fine-tuning language models.
"""

import argparse
import json
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


class TextToJsonlConverter:
    """Converts plaintext files to JSONL format with various options."""

    def __init__(
        self,
        format_type: str = "text",
        split_mode: str = "paragraph",
        delimiter: Optional[str] = None,
        system_message: Optional[str] = None,
        role: str = "assistant"
    ):
        """
        Initialize the converter.

        Args:
            format_type: Output format (text, chat, instruction, completion)
            split_mode: How to split input (paragraph, line, document, custom)
            delimiter: Custom delimiter for split_mode='custom'
            system_message: System message for chat format
            role: Role for chat format (user, assistant, system)
        """
        self.format_type = format_type
        self.split_mode = split_mode
        self.delimiter = delimiter
        self.system_message = system_message
        self.role = role

    def read_file(self, file_path: str) -> str:
        """Read content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def split_text(self, text: str) -> List[str]:
        """Split text according to the specified mode."""
        if self.split_mode == "document":
            # Treat entire document as one chunk
            return [text.strip()] if text.strip() else []

        elif self.split_mode == "line":
            # Split by lines, filter empty
            return [line.strip() for line in text.split('\n') if line.strip()]

        elif self.split_mode == "paragraph":
            # Split by double newlines (paragraphs)
            chunks = text.split('\n\n')
            return [chunk.strip() for chunk in chunks if chunk.strip()]

        elif self.split_mode == "custom":
            # Split by custom delimiter
            if not self.delimiter:
                raise ValueError("Custom split mode requires a delimiter")
            chunks = text.split(self.delimiter)
            return [chunk.strip() for chunk in chunks if chunk.strip()]

        elif self.split_mode == "section":
            # Split by sections (detects section headers and groups related paragraphs)
            # This mode looks for lines that appear to be section titles
            # (e.g., all caps, numbered, or ending with specific patterns)
            return self._split_by_sections(text)

        else:
            raise ValueError(f"Unknown split mode: {self.split_mode}")

    def _split_by_sections(self, text: str) -> List[str]:
        """
        Split text by sections, detecting section headers automatically.

        A section header is identified by patterns such as:
        - Lines in ALL CAPS (optionally with punctuation)
        - Lines ending with .— or similar patterns
        - Lines that are significantly shorter and followed by longer content
        """
        paragraphs = text.split('\n\n')
        sections = []
        current_section = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if this paragraph looks like a section header
            is_header = self._is_section_header(para)

            if is_header and current_section:
                # Save the previous section and start a new one
                sections.append('\n\n'.join(current_section))
                current_section = [para]
            else:
                # Add to current section
                current_section.append(para)

        # Don't forget the last section
        if current_section:
            sections.append('\n\n'.join(current_section))

        return sections

    def _is_section_header(self, text: str) -> bool:
        """
        Determine if a text block is likely a section header.

        Heuristics:
        - Contains mostly uppercase letters
        - Ends with .— or similar patterns
        - Is relatively short (< 200 chars) and has no lowercase paragraphs
        """
        # Get first line for analysis
        first_line = text.split('\n')[0] if '\n' in text else text

        # Pattern 1: Ends with .— (common in classical texts)
        if re.search(r'\.—', first_line):
            return True

        # Pattern 2: Mostly uppercase (at least 70% of letters are uppercase)
        letters = [c for c in first_line if c.isalpha()]
        if letters:
            uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if uppercase_ratio >= 0.7 and len(first_line) < 200:
                return True

        # Pattern 3: Starts with a number followed by a period (e.g., "1. Introduction")
        if re.match(r'^\d+\.?\s+[A-Z]', first_line):
            return True

        # Pattern 4: Starts with "CHAPTER" or "SECTION" or similar
        if re.match(r'^(CHAPTER|SECTION|PART|BOOK|ARTICLE)\s+', first_line, re.IGNORECASE):
            return True

        return False

    def format_text(self, chunk: str) -> Dict[str, Any]:
        """Format a text chunk according to the specified format type."""
        if self.format_type == "text":
            return {"text": chunk}

        elif self.format_type == "chat":
            messages = []
            if self.system_message:
                messages.append({"role": "system", "content": self.system_message})
            messages.append({"role": self.role, "content": chunk})
            return {"messages": messages}

        elif self.format_type == "instruction":
            # For instruction format, try to split on first line as instruction
            lines = chunk.split('\n', 1)
            if len(lines) == 2:
                return {"instruction": lines[0].strip(), "response": lines[1].strip()}
            else:
                return {"instruction": "", "response": chunk}

        elif self.format_type == "completion":
            # For completion format, try to split on delimiter
            parts = chunk.split('\n---\n', 1)
            if len(parts) == 2:
                return {"prompt": parts[0].strip(), "completion": parts[1].strip()}
            else:
                return {"prompt": "", "completion": chunk}

        else:
            raise ValueError(f"Unknown format type: {self.format_type}")

    def convert_file(self, input_path: str) -> List[Dict[str, Any]]:
        """Convert a single file to JSONL records."""
        content = self.read_file(input_path)
        chunks = self.split_text(content)
        return [self.format_text(chunk) for chunk in chunks]

    def write_jsonl(self, records: List[Dict[str, Any]], output_path: str):
        """Write records to a JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Convert plaintext files to JSONL format for model training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file to simple text format
  %(prog)s input.txt -o output.jsonl

  # Convert to chat format with system message
  %(prog)s input.txt -o output.jsonl -f chat -s "You are a helpful assistant"

  # Split by lines instead of paragraphs
  %(prog)s input.txt -o output.jsonl -m line

  # Convert multiple files
  %(prog)s file1.txt file2.txt file3.txt -o combined.jsonl

  # Use custom delimiter
  %(prog)s input.txt -o output.jsonl -m custom -d "---"

Format types:
  text        - Simple format: {"text": "..."}
  chat        - Chat format: {"messages": [{"role": "...", "content": "..."}]}
  instruction - Instruction format: {"instruction": "...", "response": "..."}
  completion  - Completion format: {"prompt": "...", "completion": "..."}

Split modes:
  document   - Treat entire file as one record
  line       - Split by lines
  paragraph  - Split by double newlines (default)
  section    - Auto-detect sections by headers (all-caps, numbered, etc.)
  custom     - Split by custom delimiter
        """
    )

    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input text file(s) to convert'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output JSONL file path'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['text', 'chat', 'instruction', 'completion'],
        default='text',
        help='Output format type (default: text)'
    )

    parser.add_argument(
        '-m', '--mode',
        choices=['document', 'line', 'paragraph', 'section', 'custom'],
        default='paragraph',
        help='Text splitting mode (default: paragraph)'
    )

    parser.add_argument(
        '-d', '--delimiter',
        help='Custom delimiter for split mode (used with -m custom)'
    )

    parser.add_argument(
        '-s', '--system-message',
        help='System message for chat format'
    )

    parser.add_argument(
        '-r', '--role',
        choices=['user', 'assistant', 'system'],
        default='assistant',
        help='Role for chat format messages (default: assistant)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate custom delimiter
    if args.mode == 'custom' and not args.delimiter:
        parser.error("Custom split mode (-m custom) requires a delimiter (-d)")

    # Initialize converter
    converter = TextToJsonlConverter(
        format_type=args.format,
        split_mode=args.mode,
        delimiter=args.delimiter,
        system_message=args.system_message,
        role=args.role
    )

    # Convert all input files
    all_records = []
    for input_file in args.input_files:
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Processing: {input_file}")

        try:
            records = converter.convert_file(input_file)
            all_records.extend(records)

            if args.verbose:
                print(f"  Generated {len(records)} records")

        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            sys.exit(1)

    # Write output
    try:
        converter.write_jsonl(all_records, args.output)

        if args.verbose:
            print(f"\nSuccessfully created {args.output}")
            print(f"Total records: {len(all_records)}")
        else:
            print(f"Created {args.output} with {len(all_records)} records")

    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
