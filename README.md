# Election Manifesto Fine-Tuning Dataset Generator

A Python tool for processing OCR-extracted text from election manifestos and creating high-quality fine-tuning datasets for Large Language Models (LLMs). This project transforms raw OCR data into structured training data for AI models specialized in manifesto summarization.

## Overview

This tool provides a complete pipeline for:
1. **Text Reassembly**: Converting OCR JSON output into clean, readable text
2. **Intelligent Chunking**: Splitting text into coherent segments based on paragraph breaks
3. **Manual Review Interface**: Structured format for human editing and quality control
4. **Dataset Generation**: Creating properly formatted JSON datasets for LLM fine-tuning

## Features

- ✅ **OCR Text Reassembly**: Reconstructs readable text from OCR bounding box data
- ✅ **Smart Chunking**: Automatically splits text based on paragraph boundaries
- ✅ **Human-in-the-Loop**: Manual review and editing workflow for quality assurance
- ✅ **SFTTrainer Compatible**: Generates datasets in the correct format for supervised fine-tuning
- ✅ **Error Handling**: Comprehensive validation and error reporting
- ✅ **Dual Mode Operation**: Separate workflows for initial processing and final dataset creation

## Workspace Structure

```
├── export.json                                    # Input: OCR data (JSON format)
├── manifesto_processor.py                         # Main processing script
├── 01_reassembled_text.txt                       # Output: Full reassembled text
├── 02_chunks_for_editing_and_summarization.txt   # Output: Chunked text for review
├── 03_summaries.txt                              # Input: Manual summaries (one per line)
├── manifesto_fine_tuning_data.json               # Final: Training dataset
└── output.oxps                                   # Optional: Source document
```

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Udayatk/FineTunning-LLM.git
cd FineTunning-LLM
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

### Phase 1: Initial Processing

Process your OCR data and create initial text chunks:

```bash
python manifesto_processor.py
```

This will:
- Read OCR data from [`export.json`](export.json)
- Generate [`01_reassembled_text.txt`](01_reassembled_text.txt) (full text reconstruction)
- Create [`02_chunks_for_editing_and_summarization.txt`](02_chunks_for_editing_and_summarization.txt) (segmented chunks)

### Phase 2: Manual Review & Editing

1. **Edit the chunks**: Open [`02_chunks_for_editing_and_summarization.txt`](02_chunks_for_editing_and_summarization.txt)
   - Review each chunk for OCR errors
   - Ensure coherent segmentation
   - Keep chunk markers intact (`--- CHUNK X ---` and `--- END CHUNK X ---`)

2. **Create summaries**: Create [`03_summaries.txt`](03_summaries.txt)
   - Write one summary per line
   - Each line corresponds to a chunk (Line 1 = Chunk 1, etc.)
   - Ensure high-quality, neutral summaries

### Phase 3: Dataset Generation

Generate the final training dataset:

```bash
python manifesto_processor.py process_summaries
```

This creates [`manifesto_fine_tuning_data.json`](manifesto_fine_tuning_data.json) with properly formatted training examples.

## Key Functions

### [`reassemble_text_from_ocr_data`](manifesto_processor.py)
Reconstructs readable text from OCR bounding box coordinates and text fragments.

### [`create_initial_chunks`](manifesto_processor.py)
Intelligently splits text using regex pattern matching on paragraph breaks (`\n\s*\n+`).

### [`create_final_json`](manifesto_processor.py)
Formats edited chunks and summaries into SFTTrainer-compatible JSON structure with system prompts.

## Dataset Format

The generated dataset follows this structure:

```json
[
  {
    "messages": [
      {
        "role": "system",
        "content": "You are an AI assistant that provides concise and neutral summaries of election manifesto sections. Focus on key policies and promises."
      },
      {
        "role": "user", 
        "content": "Please summarize the following section from the election manifesto:\n\n[CHUNK_TEXT]"
      },
      {
        "role": "model",
        "content": "[HUMAN_WRITTEN_SUMMARY]"
      }
    ]
  }
]
```

## Error Handling

The tool includes comprehensive validation:
- ✅ File existence checks
- ✅ JSON format validation  
- ✅ Chunk-summary count matching
- ✅ Empty content detection
- ✅ Encoding error handling

## Configuration

Modify file paths in [`manifesto_processor.py`](manifesto_processor.py):

```python
INPUT_OCR_FILE = "export.json"
REASSEMBLED_TEXT_FILE = "01_reassembled_text.txt"
CHUNKS_FOR_REVIEW_FILE = "02_chunks_for_editing_and_summarization.txt"
SUMMARIES_INPUT_FILE = "03_summaries.txt"
FINAL_OUTPUT_JSON_FILE = "manifesto_fine_tuning_data.json"
```

## Best Practices

### For Text Editing:
- Fix OCR errors (character recognition mistakes)
- Ensure logical paragraph breaks
- Maintain consistent formatting
- Preserve important policy details

### For Summary Writing:
- Keep summaries concise but comprehensive
- Use neutral, objective language
- Focus on key policies and promises
- Maintain consistency in style and length

## Troubleshooting

### Common Issues:

**File not found errors**: Ensure all input files are in the same directory as the script

**Chunk-summary mismatch**: Verify that [`03_summaries.txt`](03_summaries.txt) has exactly one line per chunk

**JSON encoding errors**: Check that [`export.json`](export.json) is valid JSON format

**Empty output**: Verify OCR data contains text content and proper structure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for election manifesto analysis and AI model training
- Designed for compatibility with HuggingFace's SFTTrainer
- Optimized for human-in-the-loop quality control workflows
