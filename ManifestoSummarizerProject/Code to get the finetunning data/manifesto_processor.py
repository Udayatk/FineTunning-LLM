import json
import re
import sys # Used to get command-line arguments

# --- Configuration ---
INPUT_OCR_FILE = "export.json" # Your OCR output
REASSEMBLED_TEXT_FILE = "01_reassembled_text.txt"
CHUNKS_FOR_REVIEW_FILE = "02_chunks_for_editing_and_summarization.txt"
SUMMARIES_INPUT_FILE = "03_summaries.txt" # File you will create manually
FINAL_OUTPUT_JSON_FILE = "manifesto_fine_tuning_data.json"

# --- Part 1: Text Reassembly Logic ---
def reassemble_text_from_ocr_data(ocr_data):
    """
    Parses OCR data (as a Python dictionary from loaded JSON),
    reassembles words into lines, and attempts basic paragraphing.

    Args:
        ocr_data (dict): The loaded JSON data from the OCR output.

    Returns:
        str: The reassembled text from the document.
    """
    full_text_parts = []
    page_data = ocr_data.get("page_data", [])

    for page_idx, page_info in enumerate(page_data):
        page_number = page_info.get("page", page_idx) # Use index if 'page' key is not present
        words = page_info.get("words", [])
        
        if not words:
            full_text_parts.append(f"\n--- Page {page_number} (No words found) ---\n")
            continue

        # Sort words primarily by ymin (top to bottom), then by xmin (left to right)
        # This is a common heuristic for standard document layouts.
        words.sort(key=lambda w: (w.get('ymin', 0), w.get('xmin', 0)))

        page_lines = []
        if not words: # Should be redundant due to the check above, but good for safety
            continue
            
        current_line_words = []
        # Heuristic for line grouping:
        # Tolerance for how much y-coordinate can vary for words on the same line.
        # This value might need tuning based on your document's font size and line spacing.
        line_y_tolerance = 15 # Example tolerance in pixels

        if words: # Ensure there are words to process
            current_line_ymin_ref = words[0].get('ymin', 0) # y-coordinate of the first word in the current potential line

            for word_obj in words:
                word_text = word_obj.get('text', '')
                word_ymin = word_obj.get('ymin', 0)

                # Check if the current word belongs to the current line
                if not current_line_words or abs(word_ymin - current_line_ymin_ref) <= line_y_tolerance:
                    current_line_words.append(word_obj)
                else:
                    # New line detected (significant y-coordinate change)
                    # Sort words in the completed line by xmin before joining
                    current_line_words.sort(key=lambda w: w.get('xmin', 0))
                    page_lines.append(" ".join(w.get('text', '') for w in current_line_words))
                    
                    # Start a new line
                    current_line_words = [word_obj]
                    current_line_ymin_ref = word_obj.get('ymin', 0) # Update reference y for the new line
            
            # Add the last line being processed
            if current_line_words:
                current_line_words.sort(key=lambda w: w.get('xmin', 0))
                page_lines.append(" ".join(w.get('text', '') for w in current_line_words))
        
        # Basic paragraphing: For now, simply join lines with a newline.
        # More sophisticated paragraph detection would analyze vertical spacing between line bounding boxes.
        # Manual review and adjustment of paragraphs in the output file is highly recommended.
        page_content = "\n".join(page_lines)
        full_text_parts.append(f"\n--- Page {page_number} ---\n{page_content}\n")

    return "".join(full_text_parts)

def create_initial_chunks(full_text, output_chunk_file):
    """
    Splits the full reassembled text into initial chunks based on multiple newline characters
    (indicative of paragraph breaks) and saves them in a numbered format for review.

    Args:
        full_text (str): The complete reassembled text of the document.
        output_chunk_file (str): Path to the file where initial chunks will be saved.

    Returns:
        int: The number of initial chunks created.
    """
    # Split by two or more consecutive newline characters (common paragraph separator)
    # Then, filter out any empty strings that might result from multiple splits or leading/trailing newlines.
    # Also, strip leading/trailing whitespace from each potential chunk.
    potential_chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n+', full_text) if chunk.strip()]
    
    with open(output_chunk_file, 'w', encoding='utf-8') as f:
        for i, chunk_text in enumerate(potential_chunks):
            f.write(f"--- CHUNK {i+1} ---\n")
            f.write(chunk_text + "\n") # Ensure a newline after the chunk text itself
            f.write(f"--- END CHUNK {i+1} ---\n\n") # Double newline to separate chunk blocks
    return len(potential_chunks)

# --- Part 2: Final JSON Creation Logic ---
def create_final_json(edited_chunks_file, summaries_file, output_json_file):
    """
    Reads the manually edited chunks and their corresponding manually written summaries,
    then formats them into the final JSON structure required for fine-tuning.

    Args:
        edited_chunks_file (str): Path to the file containing manually edited text chunks.
        summaries_file (str): Path to the file containing one summary per line, corresponding to each chunk.
        output_json_file (str): Path where the final JSON dataset will be saved.
    """
    chunks = []
    try:
        with open(edited_chunks_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Regex to find chunks based on the defined delimiters
            # re.DOTALL allows '.' to match newline characters as well
            raw_chunks = re.findall(r"--- CHUNK \d+ ---\n(.*?)\n--- END CHUNK \d+ ---", content, re.DOTALL)
            chunks = [chunk.strip() for chunk in raw_chunks] # Strip whitespace from each extracted chunk
    except FileNotFoundError:
        print(f"Error: Edited chunks file not found: '{edited_chunks_file}'")
        return

    summaries = []
    try:
        with open(summaries_file, 'r', encoding='utf-8') as f:
            # Read each line, strip whitespace, and only include non-empty lines
            summaries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Summaries file not found: '{summaries_file}'")
        return

    if not chunks:
        print(f"Error: No chunks found in '{edited_chunks_file}'. Please check the file and delimiters.")
        return
        
    if not summaries:
        print(f"Error: No summaries found in '{summaries_file}'. Please ensure it contains one summary per line.")
        return

    if len(chunks) != len(summaries):
        print(f"Error: Mismatch between the number of chunks ({len(chunks)}) and summaries ({len(summaries)}).")
        print(f"Please ensure each chunk in '{edited_chunks_file}' has a corresponding summary line in '{summaries_file}'.")
        return

    final_dataset_records = []
    # Define the system prompt that will be part of each training example
    system_prompt = "You are an AI assistant that provides concise and neutral summaries of election manifesto sections. Focus on key policies and promises."

    for i in range(len(chunks)):
        chunk_text = chunks[i]
        summary_text = summaries[i]
        
        # Construct the user message, including an instruction to summarize
        user_content = f"Please summarize the following section from the election manifesto:\n\n{chunk_text}"

        # Create the record in the format expected by the SFTTrainer
        record = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
                {"role": "model", "content": summary_text} # This is the target output for the model to learn
            ]
        }
        final_dataset_records.append(record)

    try:
        with open(output_json_file, "w", encoding="utf-8") as f:
            # Save the list of records as a JSON array, pretty-printed with an indent of 2
            json.dump(final_dataset_records, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully created fine-tuning data at: '{output_json_file}'")
        print(f"Total records created: {len(final_dataset_records)}")
    except IOError:
        print(f"\nError: Could not write fine-tuning data to '{output_json_file}'")


# --- Main Script Logic ---
def main():
    """
    Main function to orchestrate the processing pipeline.
    It checks for a command-line argument to switch between modes:
    1. Initial processing: OCR to reassembled text and initial chunks.
    2. Final formatting: Edited chunks and summaries to final JSON.
    """
    # Check if a command-line argument 'process_summaries' is provided
    if len(sys.argv) > 1 and sys.argv[1].lower() == "process_summaries":
        print("--- Mode: Processing Summaries and Creating Final JSON ---")
        create_final_json(CHUNKS_FOR_REVIEW_FILE, SUMMARIES_INPUT_FILE, FINAL_OUTPUT_JSON_FILE)
    else:
        print("--- Mode: Initial OCR Processing and Chunk Creation ---")
        try:
            with open(INPUT_OCR_FILE, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input OCR file not found at '{INPUT_OCR_FILE}'.")
            print("Please make sure it's in the same directory as the script, or update the INPUT_OCR_FILE path.")
            return
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{INPUT_OCR_FILE}'. Ensure it's a valid JSON file.")
            return

        print(f"Step 1: Reassembling text from '{INPUT_OCR_FILE}'...")
        reassembled_text = reassemble_text_from_ocr_data(ocr_data)
        
        try:
            with open(REASSEMBLED_TEXT_FILE, 'w', encoding='utf-8') as f:
                f.write(reassembled_text)
            print(f"   ... Full reassembled text saved to '{REASSEMBLED_TEXT_FILE}'.")
            print("      (For your reference and detailed manual cleaning if the initial reassembly needs refinement).")
        except IOError:
            print(f"   Error: Could not write reassembled text to '{REASSEMBLED_TEXT_FILE}'.")


        print(f"\nStep 2: Creating initial chunks for your review in '{CHUNKS_FOR_REVIEW_FILE}'...")
        try:
            num_chunks = create_initial_chunks(reassembled_text, CHUNKS_FOR_REVIEW_FILE)
            print(f"   ... Created {num_chunks} initial chunks.")
            print("      (These chunks are based on paragraph-like breaks from the reassembled text).")
        except IOError:
            print(f"   Error: Could not write initial chunks to '{CHUNKS_FOR_REVIEW_FILE}'.")
            return # Stop if we can't create this crucial file

        # Instructions for the user's manual steps
        print("\n--- MANUAL ACTION REQUIRED ---")
        print(f"1. Open and review/edit the file: '{CHUNKS_FOR_REVIEW_FILE}'.")
        print("   - This file contains the manifesto text split into numbered chunks.")
        print("   - Carefully review each chunk. Edit the text directly IN THIS FILE for clarity,")
        print("     correctness (fix any OCR errors), and to ensure each chunk is a good,")
        print("     coherent segment suitable for summarization.")
        print("   - Ensure the '--- CHUNK X ---' and '--- END CHUNK X ---' markers remain intact and correctly numbered.")
        
        print(f"\n2. Create a new text file named: '{SUMMARIES_INPUT_FILE}' (in the same directory as this script).")
        
        print(f"\n3. In '{SUMMARIES_INPUT_FILE}', write one high-quality summary PER LINE.")
        print("   - The first line of this file should be your human-written summary for CHUNK 1")
        print(f"     (from your edited '{CHUNKS_FOR_REVIEW_FILE}').")
        print("   - The second line should be the summary for CHUNK 2, and so on.")
        print(f"   - You should have exactly {num_chunks} lines of summaries if you don't add or remove chunks")
        print(f"     during your editing of '{CHUNKS_FOR_REVIEW_FILE}'. If you do modify the number of chunks,")
        print("     ensure your summaries in this file match the final count and order of chunks.")

        print(f"\n4. After you have completed and saved your edits in '{CHUNKS_FOR_REVIEW_FILE}'")
        print(f"   AND written all corresponding summaries in '{SUMMARIES_INPUT_FILE}':")
        print(f"   Re-run this script with the 'process_summaries' argument to generate the final JSON dataset.")
        print(f"   Example command: python {sys.argv[0]} process_summaries")
        print("---------------------------------")

if __name__ == "__main__":
    main()
