import pandas as pd
import os
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizer

class TextFileDataset(Dataset):
    def __init__(self, file_path: str, tokenizer: PreTrainedTokenizer, block_size: int = 512):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        tokenized = tokenizer(text, return_tensors="pt", truncation=False)
        self.input_ids = tokenized['input_ids'][0]

        # Split into chunks
        self.examples = [
            self.input_ids[i:i+block_size]
            for i in range(0, len(self.input_ids) - block_size + 1, block_size)
        ]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        x = self.examples[idx]
        return {'input_ids': x, 'labels': x.clone()}

class TextDirDataset(Dataset):
    def __init__(self, dir_path: str, tokenizer: PreTrainedTokenizer, block_size: int = 512):
        texts = []
        for fname in os.listdir(dir_path):
            if fname.endswith(".txt"):
                with open(os.path.join(dir_path, fname), 'r', encoding='utf-8') as f:
                    texts.append(f.read())

        full_text = "\n".join(texts)
        tokenized = tokenizer(full_text, return_tensors="pt", truncation=False)
        self.input_ids = tokenized['input_ids'][0]

        self.examples = [
            self.input_ids[i:i+block_size]
            for i in range(0, len(self.input_ids) - block_size + 1, block_size)
        ]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        x = self.examples[idx]
        return {'input_ids': x, 'labels': x.clone()}

class CSVTextDataset(Dataset):
    def __init__(self, csv_path: str, tokenizer: PreTrainedTokenizer, text_col: str, block_size: int = 512):
        df = pd.read_csv(csv_path)
        texts = df[text_col].dropna().astype(str).tolist()

        full_text = "\n".join(texts)
        tokenized = tokenizer(full_text, return_tensors="pt", truncation=False)
        self.input_ids = tokenized['input_ids'][0]

        self.examples = [
            self.input_ids[i:i+block_size]
            for i in range(0, len(self.input_ids) - block_size + 1, block_size)
        ]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        x = self.examples[idx]
        return {'input_ids': x, 'labels': x.clone()}
