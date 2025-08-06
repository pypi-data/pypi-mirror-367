# File: scripts/_train_logic.py

import torch
import torch.nn as nn
from .model import NanoLLM # Import the model definition

def train_model(args):
    """
    Contains the full logic for training the NanoLLM model.
    Accepts an 'args' object from argparse.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using {device} device for training.")

    # --- Data Loading and Tokenization ---
    try:
        with open(args.data_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find data file at '{args.data_path}'")
        return # Exit the function gracefully
        
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = { ch:i for i,ch in enumerate(chars) }
    itos = { i:ch for i,ch in enumerate(chars) }
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
    data = torch.tensor(encode(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_data = data[:n]
    val_data = data[n:]

    def get_batch(split):
        data_source = train_data if split == 'train' else val_data
        ix = torch.randint(len(data_source) - args.block_size, (args.batch_size,))
        x = torch.stack([data_source[i:i+args.block_size] for i in ix])
        y = torch.stack([data_source[i+1:i+args.block_size+1] for i in ix])
        x, y = x.to(device), y.to(device)
        return x, y

    # --- Model Definition ---
    model_config_args = {
        'vocab_size': vocab_size,
        'n_embd': args.n_embd,
        'n_head': args.n_head,
        'n_layer': args.n_layer,
        'block_size': args.block_size,
        'dropout': args.dropout,
    }
    model = NanoLLM(**model_config_args)
    m = model.to(device)
    print(f"Model initialized with {sum(p.numel() for p in m.parameters())/1e6:.2f}M parameters.")

    @torch.no_grad()
    def estimate_loss():
        out = {}
        model.eval()
        for split in ['train', 'val']:
            # Using a smaller number of iterations for evaluation to speed it up
            eval_iters = 200
            losses = torch.zeros(eval_iters)
            for k in range(eval_iters):
                X, Y = get_batch(split)
                logits, loss = model(X, Y)
                losses[k] = loss.item()
            out[split] = losses.mean()
        model.train()
        return out

    # --- Training Loop ---
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    print("\nStarting training...")
    for iter in range(args.max_iters):
        # Default eval interval unless specified otherwise, to avoid crashing if arg is missing
        eval_interval = getattr(args, 'eval_interval', 500)
        if iter % eval_interval == 0 or iter == args.max_iters - 1:
            losses = estimate_loss()
            print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
            
        xb, yb = get_batch('train')
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        
    print("Training finished.")

    # --- Save the model ---
    torch.save(model.state_dict(), args.model_save_path)
    print(f"Model saved to {args.model_save_path}")