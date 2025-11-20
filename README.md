# txt2jsonl

A command-line utility for converting plaintext files to JSONL (JSON Lines) format, specifically designed for machine learning model training and fine-tuning.

## Features

- **Multiple Output Formats**: Support for various JSONL formats used in ML training
  - Simple text format
  - Chat/conversation format
  - Instruction-response format
  - Prompt-completion format

- **Flexible Text Splitting**: Multiple ways to chunk your text
  - By paragraph (double newlines)
  - By line
  - Entire document
  - Custom delimiter

- **Batch Processing**: Convert multiple files into a single JSONL output
- **UTF-8 Support**: Handles various text encodings
- **Zero Dependencies**: Pure Python 3 with standard library only

## Installation

Simply clone this repository and make the script executable:

```bash
git clone <repository-url>
cd txt2jsonl
chmod +x txt2jsonl.py
```

Or add it to your PATH for system-wide access:

```bash
sudo cp txt2jsonl.py /usr/local/bin/txt2jsonl
```

## Requirements

- Python 3.6 or higher
- No external dependencies required

## Usage

### Basic Syntax

```bash
./txt2jsonl.py [input_files...] -o output.jsonl [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output JSONL file path (required) | - |
| `-f, --format` | Output format: text, chat, instruction, completion | text |
| `-m, --mode` | Split mode: document, line, paragraph, custom | paragraph |
| `-d, --delimiter` | Custom delimiter (use with `-m custom`) | - |
| `-s, --system-message` | System message for chat format | - |
| `-r, --role` | Role for chat messages: user, assistant, system | assistant |
| `-v, --verbose` | Enable verbose output | - |

### Examples

#### 1. Simple Text Format (Default)

Convert paragraphs to simple text records:

```bash
./txt2jsonl.py input.txt -o output.jsonl
```

Output format:
```json
{"text": "First paragraph content..."}
{"text": "Second paragraph content..."}
```

#### 2. Chat Format

Convert text to chat/conversation format:

```bash
./txt2jsonl.py conversation.txt -o chat.jsonl -f chat -r assistant
```

Output format:
```json
{"messages": [{"role": "assistant", "content": "Response text..."}]}
```

With system message:

```bash
./txt2jsonl.py input.txt -o output.jsonl -f chat -s "You are a helpful assistant" -r user
```

#### 3. Line-by-Line Processing

Process each line as a separate record:

```bash
./txt2jsonl.py input.txt -o output.jsonl -m line
```

#### 4. Document Mode

Treat entire file as one record:

```bash
./txt2jsonl.py input.txt -o output.jsonl -m document
```

#### 5. Custom Delimiter

Split text using a custom delimiter:

```bash
./txt2jsonl.py input.txt -o output.jsonl -m custom --delimiter='---'
```

#### 6. Batch Processing

Combine multiple files into one JSONL output:

```bash
./txt2jsonl.py file1.txt file2.txt file3.txt -o combined.jsonl
```

#### 7. Instruction-Response Format

Useful for instruction fine-tuning:

```bash
./txt2jsonl.py instructions.txt -o output.jsonl -f instruction
```

The tool will try to split each chunk with the first line as instruction and the rest as response.

#### 8. Prompt-Completion Format

For completion-based training:

```bash
./txt2jsonl.py prompts.txt -o output.jsonl -f completion
```

## Output Formats

### Text Format
```json
{"text": "Your text content here"}
```

### Chat Format
```json
{"messages": [{"role": "user", "content": "Message content"}]}
```

With system message:
```json
{"messages": [
  {"role": "system", "content": "You are a helpful assistant"},
  {"role": "user", "content": "Message content"}
]}
```

### Instruction Format
```json
{"instruction": "Question or instruction", "response": "Answer or response"}
```

### Completion Format
```json
{"prompt": "Prompt text", "completion": "Completion text"}
```

## Use Cases

### Training Language Models

Convert your text corpus to JSONL for training:

```bash
./txt2jsonl.py corpus.txt -o training_data.jsonl -m paragraph
```

### Fine-tuning Chat Models

Prepare conversation data:

```bash
./txt2jsonl.py conversations.txt -o chat_training.jsonl \
  -f chat -s "You are a helpful coding assistant" -r assistant
```

### Instruction Tuning

Create instruction-response pairs:

```bash
./txt2jsonl.py qa_pairs.txt -o instruction_data.jsonl \
  -f instruction -m custom --delimiter='---'
```

## Examples Directory

The `examples/` directory contains sample input files and their corresponding outputs:

- `sample_text.txt` - Basic text paragraphs
- `conversation.txt` - Q&A style content
- `instructions.txt` - Instruction-response pairs
- `output_*.jsonl` - Example outputs in various formats

Try them out:

```bash
./txt2jsonl.py examples/sample_text.txt -o test.jsonl -v
```

## Tips

1. **Paragraph splitting** (default) works best for prose and documentation
2. **Line splitting** is ideal for lists, one-liners, or pre-formatted data
3. **Document mode** is useful when you want one record per file
4. **Custom delimiter** gives you full control over chunking
5. Use **verbose mode** (`-v`) to see processing details
6. The **chat format** with system messages is great for fine-tuning conversational models
7. For large datasets, process files in batches and combine the JSONL outputs

## Common Patterns

### Preparing data for GPT-style models:
```bash
./txt2jsonl.py data.txt -o training.jsonl -f chat -s "You are an expert assistant"
```

### Creating a simple text corpus:
```bash
./txt2jsonl.py *.txt -o corpus.jsonl -m paragraph
```

### Converting code documentation:
```bash
./txt2jsonl.py docs/*.txt -o docs.jsonl -m document
```

## Troubleshooting

**Q: My paragraphs aren't splitting correctly**
A: Make sure your paragraphs are separated by blank lines (double newlines). Or use `-m custom` with your own delimiter.

**Q: I'm getting encoding errors**
A: The tool tries UTF-8 first, then falls back to latin-1. If you have a specific encoding, convert your file first: `iconv -f ENCODING -t UTF-8 input.txt > output.txt`

**Q: Can I preview without creating a file?**
A: You can pipe to stdout: `./txt2jsonl.py input.txt -o /dev/stdout | head`

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

MIT License - feel free to use this in your projects!
