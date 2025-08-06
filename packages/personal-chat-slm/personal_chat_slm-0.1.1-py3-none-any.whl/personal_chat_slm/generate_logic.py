# File: scripts/_generate_logic.py

import torch
from .model import NanoLLM # Import the model definition

def generate_text(args):
    """
    Contains the full logic for loading a trained NanoLLM model
    and generating text from a prompt. Accepts an 'args' object.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # --- Data and Tokenizer Setup ---
    try:
        with open(args.data_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find data file at '{args.data_path}' to build vocabulary.")
        return

    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = { ch:i for i,ch in enumerate(chars) }
    itos = { i:ch for i,ch in enumerate(chars) }
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])

    # --- Load Model ---
    # We must define the model with the same architecture it was trained with.
    # In a more advanced setup, you'd save the model config along with the weights.
    # For now, we assume the config from default training arguments.
    model_config = {
        'vocab_size': vocab_size,
        'n_embd': 384,
        'n_head': 6,
        'n_layer': 6,
        'block_size': 256,
        'dropout': 0.2,
    }
    model = NanoLLM(**model_config)
    m = model.to(device)

    print(f"Loading trained model from {args.model_path}")
    try:
        m.load_state_dict(torch.load(args.model_path, map_location=device))
    except FileNotFoundError:
        print(f"Error: Model file not found at '{args.model_path}'. Please run the 'train' command first.")
        return
    except Exception as e:
        print(f"Error loading model state: {e}")
        return
    
    m.eval() # Set the model to evaluation mode

    # --- Generate Text ---
    print(f"\n--- Generating from prompt ---")
    print(f"Prompt: '{args.prompt}'")
    
    context = torch.tensor(encode(args.prompt), dtype=torch.long, device=device).unsqueeze(0)
    generated_output = m.generate(context, max_new_tokens=args.max_new_tokens)
    decoded_output = decode(generated_output[0].tolist())
    
    print("\n--- Model Output ---")
    print(decoded_output)
    print("--------------------\n")