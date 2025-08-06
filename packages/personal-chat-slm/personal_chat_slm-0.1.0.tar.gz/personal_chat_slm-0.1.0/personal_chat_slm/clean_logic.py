# File: scripts/_clean_logic.py

import re
import os

def clean_data(args):
    """
    Contains the logic for cleaning the raw WhatsApp chat log.
    Accepts an 'args' object with input_file and output_file paths.
    """
    print(f"Starting the cleaning process...")
    print(f"Input file: {os.path.abspath(args.input_file)}")

    cleaned_lines = []
    line_pattern = re.compile(r"^\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s*(am|pm)\s*-\s*[^:]+:\s*(.*)")
    url_pattern = re.compile(r"https?://\S+")
    ignore_phrases = ["<Media omitted>", "This message was deleted"]

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                match = line_pattern.match(line)
                if match:
                    message = match.group(2).strip()
                    if message in ignore_phrases:
                        continue
                    message = url_pattern.sub("", message).strip()
                    if message:
                        cleaned_lines.append(message)
                else:
                    # Append multi-line message parts, cleaning URLs from them too
                    message = line.strip()
                    message = url_pattern.sub("", message).strip()
                    if message:
                        cleaned_lines.append(message)

        with open(args.output_file, 'w', encoding='utf-8') as f_out:
            for line in cleaned_lines:
                f_out.write(line + '\n')
        
        print(f"Cleaning complete!")
        print(f"Cleaned data saved to: {os.path.abspath(args.output_file)}")

    except FileNotFoundError:
        print(f"Error: The input file '{args.input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")