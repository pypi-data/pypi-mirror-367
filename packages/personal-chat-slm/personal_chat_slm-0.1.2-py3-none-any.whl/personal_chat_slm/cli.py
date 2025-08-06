# File: scripts/cli.py

import argparse
# Use relative imports because the files are in the same package (src)
from .clean_logic import clean_data
from .train_logic import train_model
from .generate_logic import generate_text

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="A custom nano-LLM for personal chat data.",
        prog="personal-chat-slm"
    )
    # Create a subparser to handle commands
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- Clean Command ---
    parser_clean = subparsers.add_parser('clean', help='Clean a raw WhatsApp chat file.')
    parser_clean.add_argument('--input-file', type=str, default='data/data.txt', help='Path to the raw input chat file.')
    parser_clean.add_argument('--output-file', type=str, default='data/chat_clean.txt', help='Path to save the cleaned output file.')
    parser_clean.set_defaults(func=clean_data)

    # --- Train Command ---
    parser_train = subparsers.add_parser('train', help='Train a new model from scratch.')
    # Add all the arguments for the train command
    parser_train.add_argument('--data_path', type=str, default='data/chat_clean.txt', help='Path to the training data')
    parser_train.add_argument('--model_save_path', type=str, default='models/nano_llm_model.pth', help='Path to save the trained model')
    parser_train.add_argument('--max_iters', type=int, default=5000, help='Maximum training iterations')
    parser_train.add_argument('--learning_rate', type=float, default=3e-4, help='Learning rate')
    parser_train.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser_train.add_argument('--n_embd', type=int, default=384, help='Embedding dimension')
    parser_train.add_argument('--n_head', type=int, default=6, help='Number of attention heads')
    parser_train.add_argument('--n_layer', type=int, default=6, help='Number of transformer layers')
    parser_train.add_argument('--dropout', type=float, default=0.2, help='Dropout rate')
    parser_train.set_defaults(func=train_model)

    # --- Generate Command ---
    parser_generate = subparsers.add_parser('generate', help='Generate text from a trained model.')
    # Add all the arguments for the generate command
    parser_generate.add_argument('prompt', type=str, help='The starting prompt for text generation.')
    parser_generate.add_argument('--model_path', type=str, default='models/nano_llm_model.pth', help='Path to the saved model state dictionary')
    parser_generate.add_argument('--max_new_tokens', type=int, default=200, help='Maximum number of new tokens to generate')
    parser_generate.add_argument('--data_path', type=str, default='data/chat_clean.txt', help='Path to the training data to build vocabulary')
    parser_generate.set_defaults(func=generate_text)

    # Parse the arguments and call the function associated with the command
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()