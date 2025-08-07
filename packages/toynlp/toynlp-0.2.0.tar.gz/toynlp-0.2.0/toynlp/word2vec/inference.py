import torch
from tokenizers import Tokenizer

from toynlp.util import current_device
from toynlp.paths import CBOW_MODEL_PATH, SKIP_GRAM_MODEL_PATH
from toynlp.word2vec.model import CbowModel
from toynlp.word2vec.tokenizer import Word2VecTokenizer


def load_tokenizer_model(model_name: str = "skip_gram") -> tuple[Tokenizer, CbowModel]:
    if model_name == "cbow":
        word2vec_model_path = CBOW_MODEL_PATH
    elif model_name == "skip_gram":
        word2vec_model_path = SKIP_GRAM_MODEL_PATH
    else:
        msg = f"Unknown model name: {model_name}. Use 'cbow' or 'skip_gram'."
        raise ValueError(msg)

    tokenizer = Word2VecTokenizer().load()
    model = torch.load(str(word2vec_model_path), weights_only=False)
    model.to(current_device)
    model.eval()
    return tokenizer, model


def word_to_vec(word: str) -> torch.Tensor:
    tokenizer, model = load_tokenizer_model()
    token_ids = tokenizer.encode(word).ids
    token_ids_tensor = torch.tensor(token_ids).unsqueeze(0).to(current_device)

    with torch.no_grad():
        vec = model.embedding(token_ids_tensor)
    return vec[0, 0, :]


def vocab_embedding(
    tokenizer: Tokenizer | None = None,
    model: CbowModel | None = None,
) -> tuple[torch.Tensor, list[int]]:
    """Returns vocabulary embeddings and corresponding token IDs."""
    if tokenizer is None or model is None:
        tokenizer, model = load_tokenizer_model()

    vocab = tokenizer.get_vocab()
    vocab_ids = list(vocab.values())
    vocab_ids_tensor = torch.tensor(vocab_ids, dtype=torch.long).unsqueeze(0).to(current_device)

    with torch.no_grad():
        embeddings = model.embedding(vocab_ids_tensor).squeeze(0)

    return embeddings, vocab_ids


def find_similar_words(word: str, top_k: int = 5) -> list[str]:
    word_vec = word_to_vec(word)
    return find_similar_words_by_vec(word_vec, top_k)


def calc_vecs_similarity(vec1: torch.Tensor, vec2: torch.Tensor) -> float:
    return torch.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0)).item()


def find_similar_words_by_vec(word_vec: torch.Tensor, top_k: int = 5) -> list[str]:
    tokenizer, model = load_tokenizer_model()
    all_embeddings, vocab_ids = vocab_embedding(tokenizer, model)

    similarities = torch.nn.functional.cosine_similarity(word_vec.unsqueeze(0), all_embeddings, dim=1)
    top_k_indices = torch.topk(similarities, k=top_k).indices

    # Map indices back to actual token IDs and decode them
    similar_token_ids = [vocab_ids[i] for i in top_k_indices]
    similar_words = [tokenizer.decode([token_id]) for token_id in similar_token_ids]
    return similar_words


def evaluate_model_context(text: str) -> None:
    tokenizer, model = load_tokenizer_model()
    token_ids = tokenizer.encode(text).ids
    token_ids_tensor = torch.tensor(token_ids).unsqueeze(0).to(current_device)
    with torch.no_grad():
        print(token_ids_tensor.shape)
        logits = model(token_ids_tensor)
        pred = torch.argmax(logits, dim=1)
        print(tokenizer.decode(pred.tolist()))


def evaluate_embedding() -> None:
    print(f"Embedding for 'machine': {word_to_vec('machine').shape}")

    embeddings, _ = vocab_embedding()
    print("Vocabulary embeddings shape:", embeddings.shape)


def evaluate_similar_words(word: str, top_k: int = 5) -> None:
    similar_words = find_similar_words(word, top_k)
    print(f"[{word}]'s similar words: {similar_words}")


def evaluate_king_queen():
    # king - man + women
    king_vec = word_to_vec("king")
    man_vec = word_to_vec("man")
    woman_vec = word_to_vec("woman")
    res_vec = king_vec - man_vec + woman_vec
    queen_vec = word_to_vec("queen")

    similar_words = find_similar_words_by_vec(res_vec, top_k=10)
    print(f"[king-man+women]'s similar words: {similar_words}")

    print(f"similarity king-queen: {calc_vecs_similarity(king_vec, queen_vec)}")
    print(f"similarity man-woman: {calc_vecs_similarity(man_vec, woman_vec)}")
    print(f"similarity (king-man+women)-queen: {calc_vecs_similarity(res_vec, queen_vec)}")


def evaluate_word_addition(words: list[str]) -> None:
    word_vecs = [word_to_vec(word) for word in words]
    res_vec = torch.sum(torch.stack(word_vecs), dim=0)
    similar_words = find_similar_words_by_vec(res_vec, top_k=10)
    print(f"[{' + '.join(words)}]'s most similar words:")
    for i, word in enumerate(similar_words, 1):
        print(f"  {i:2d}. 🔸 {word}")


def evaluate_country_capital(capital_1: str, country_1: str, country_2: str) -> None:
    capital_vec_1 = word_to_vec(capital_1)
    country_vec_1 = word_to_vec(country_1)
    country_vec_2 = word_to_vec(country_2)

    res_vec = capital_vec_1 - country_vec_1 + country_vec_2
    similar_words = find_similar_words_by_vec(res_vec, top_k=10)
    print(f"[{capital_1} - {country_1} + {country_2}]'s most similar words:")
    for i, word in enumerate(similar_words, 1):
        print(f"  {i:2d}. 🔸 {word}")


if __name__ == "__main__":
    # machine learning is a [method] of data analysis that
    # evaluate_model_context("machine learning is a of data analysis that")

    # evaluate_embedding()
    # evaluate_similar_words("home", top_k=10)
    evaluate_king_queen()

    # evaluate_word_addition(["tall", "rich", "handsome"])
    # evaluate_word_addition(["white", "rich", "beautiful"])

    evaluate_country_capital("Paris", "France", "Italy")
    evaluate_country_capital("think", "thinking", "read")
