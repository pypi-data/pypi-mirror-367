import pathlib

_MODEL_PATH = pathlib.Path(__file__).parents[1] / "models"

_MODEL_PATH.mkdir(parents=True, exist_ok=True)


# Word2Vec paths
W2V_TOKENIZER_PATH = _MODEL_PATH / "word2vec" / "tokenizer.json"
CBOW_MODEL_PATH = _MODEL_PATH / "word2vec" / "cbow_model.pt"
SKIP_GRAM_MODEL_PATH = _MODEL_PATH / "word2vec" / "skip_gram_model.pt"


# Seq2Seq paths
SEQ2SEQ_TOKENIZER_PATH_MAP = {
    "en": _MODEL_PATH / "seq2seq" / "tokenizer_en.json",
    "fr": _MODEL_PATH / "seq2seq" / "tokenizer_fr.json",
    "de": _MODEL_PATH / "seq2seq" / "tokenizer_de.json",
}
SEQ2SEQ_MODEL_PATH = _MODEL_PATH / "seq2seq" / "seq2seq_model.pt"
