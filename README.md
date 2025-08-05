# Eduparser

EduParser converts educational documents such as PDF, DOCX, HTML or plain
text files into clean JSONL chunks that can be fed to machine learning
pipelines. It offers a modular architecture:

1. **pdf_extractor** – reads text from various formats.
2. **content_cleaner** – normalises and cleans raw text.
3. **chunk_generator** – splits text into roughly 300 token chunks.
4. **metadata_injector** – attaches metadata like grade, course and topic.
5. **jsonl_exporter** – writes the processed data to JSONL files.
6. **faiss_indexer** *(optional)* – builds a FAISS vector index from JSONL
   records.

## Installation

Install the core dependencies:

```bash
pip install -r requirements.txt
```

For FAISS indexing support, also install:

```bash
pip install -r requirements.txt -r requirements-faiss.txt
```
To enable the OpenAI ``tiktoken`` based tokenizer used by ``--tokenizer openai``
install ``tiktoken`` as well:

```bash
pip install tiktoken
```

## Command line usage

```bash
python -m eduparser.cli book.pdf \
  --sınıf 4 --ders "Fen Bilgisi" --konu "Maddenin Halleri" \
  --out output.jsonl --tokenizer openai --split_headings \
  --id_strategy uuid --index output.faiss \
  --model_name sentence-transformers/all-MiniLM-L6-v2
```

This command extracts the text from `book.pdf`, cleans and chunks it,
attaches the provided metadata and finally writes `output.jsonl`. Because an
`--index` path was provided, a FAISS index is also built using the specified
embedding model.

## Streamlit GUI

For a graphical interface launch the Streamlit app:

```bash
streamlit run app.py
```

The GUI allows uploading PDF, DOCX, HTML or TXT files, entering grade, course
and topic information, adjusting the chunk size and optionally creating a
FAISS index. After processing, download links for the generated JSONL and
index files are presented along with a preview of the first records and basic
statistics.
