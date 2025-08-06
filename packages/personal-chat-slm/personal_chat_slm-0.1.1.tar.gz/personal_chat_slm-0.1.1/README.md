# Personal Chat SLM (Small Language Model)

[![PyPI version](https://badge.fury.io/py/personal-chat-slm.svg)](https://badge.fury.io/py/personal-chat-slm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)

A command-line tool to train a "nano" language model from scratch on your personal chat history. This project takes a raw chat export (like from WhatsApp) and builds a character-level Transformer model that learns to mimic the unique style, vocabulary, and rhythm of your conversations.

Think of it as creating a "digital conversational ghost" from your chat data. It's designed primarily as an educational tool to understand how language models are built from the ground up, rather than a large-scale, general-purpose chatbot.

## Features

* **Builds from Scratch:** Doesn't use pre-trained models. You build and train your own Transformer architecture.
* **Character-Level Learning:** Learns the statistical patterns of your chat one character at a time, allowing it to capture unique spellings, slang, and emoji usage.
* **CLI Interface:** A simple, powerful command-line interface to manage the entire workflow: cleaning data, training the model, and generating text.
* **Packaged for Distribution:** Published as a public package on PyPI, so anyone can install and use it.

## How It Works

The tool follows a three-step process, managed entirely by the command-line interface:

1.  **Clean:** It ingests a raw chat file (e.g., `_chat.txt` from WhatsApp) and strips away all metadata like timestamps, sender names, and system messages (`<Media omitted>`). This produces a clean text corpus.
2.  **Train:** It uses this clean corpus to train a decoder-only Transformer model (like GPT). The model learns the probability of which character is likely to follow a given sequence of characters.
3.  **Generate:** Once trained, the model can be given a starting prompt. It then generates new text character-by-character based on the patterns it learned, effectively mimicking the conversational style of the training data.

## Installation

You can install `personal-chat-slm` directly from PyPI using pip:

```bash
pip install personal-chat-slm
````

## Usage: The 3-Step Workflow

Using the tool involves preparing your data and then running the three main commands in order.

### Step 1: Prepare Your Data

You need a raw chat log file. The tool is designed to work with WhatsApp chat exports.

1.  In WhatsApp, go to a chat, tap the three dots -\> More -\> Export chat -\> Without media.
2.  Save the resulting `.txt` file inside a `data/` folder in your project directory. Let's assume you name it `data/my_chat.txt`.

### Step 2: Clean the Data

Run the `clean` command to process your raw chat file.

```bash
# This command will read your raw chat file and create a clean version.
personal-chat-slm clean --input-file data/my_chat.txt --output-file data/chat_clean.txt
```

### Step 3: Train the Model

Now, use the cleaned data to train your model. This step will take time and is best run on a machine with a GPU.

```bash
# This command starts the training process and saves the final model.
personal-chat-slm train --data_path data/chat_clean.txt --max-iters 5000
```

  * `--max-iters`: The number of training steps. 5000 is a good starting point. More iterations can lead to a better model but will take longer.
  * The trained model will be saved by default to `models/nano_llm_model.pth`.

### Step 4: Generate Text

Once your model is trained, you can use it to generate text from any prompt.

```bash
# Provide a prompt directly on the command line.
personal-chat-slm generate "Hey, what are you doing tonight?" --max-new-tokens 300
```

The model will load your trained weights and generate text that continues the prompt in the style it has learned.

## For Developers (Local Setup)

If you want to contribute or modify the source code, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/yourusername/personal-chat-slm.git](https://github.com/yourusername/personal-chat-slm.git)
    cd personal-chat-slm
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install in editable mode:**
    This command links the `personal-chat-slm` command to your source code, so any changes you make are immediately reflected.

    ```bash
    pip install -e .
    ```

## Ethical Considerations & Disclaimer

**This project deals with highly sensitive personal data.** Ethical use is paramount.

  * **Consent:** Do **not** use any chat log without the explicit, informed consent of **all participants** in the chat.
  * **Privacy:** Never upload your private chat data or trained models derived from it to public repositories like GitHub. The `.gitignore` file in this project is configured to prevent this automatically. Handle the data with extreme care.
  * **Disclaimer:** This tool is provided for educational purposes. The generated text is a statistical artifact and may not always be coherent or appropriate. The creators are not responsible for the model's output or any misuse of this software.

## License

This project is licensed under the MIT License.