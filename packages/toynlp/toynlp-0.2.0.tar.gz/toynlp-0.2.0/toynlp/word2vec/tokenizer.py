from datasets import Dataset
from tokenizers import Tokenizer, normalizers
from tokenizers.models import WordLevel
from tokenizers.normalizers import NFD, Lowercase, StripAccents
from tokenizers.pre_tokenizers import Punctuation, Sequence, Whitespace
from tokenizers.trainers import WordLevelTrainer

from toynlp.paths import W2V_TOKENIZER_PATH


class Word2VecTokenizer:
    def __init__(
        self,
        vocab_size: int = 20000,
    ) -> None:
        self.model_path = W2V_TOKENIZER_PATH
        self.vocab_size = vocab_size

        self.tokenizer = Tokenizer(WordLevel(vocab=None, unk_token="[UNK]"))
        self.tokenizer.pre_tokenizer = Sequence(
            [
                Punctuation(behavior="removed"),  # Remove punctuation during pre-tokenization
                Whitespace(),
            ],
        )
        self.tokenizer.normalizer = normalizers.Sequence(
            [
                NFD(),
                Lowercase(),
                StripAccents(),
            ],  # type: ignore[assignment]
        )

    def train(self, dataset: Dataset) -> Tokenizer:
        trainer = WordLevelTrainer(
            vocab_size=self.vocab_size,  # type: ignore[unknown-argument]
            min_frequency=50,  # type: ignore[unknown-argument]
            special_tokens=["[UNK]"],  # type: ignore[unknown-argument]
        )
        self.tokenizer.train_from_iterator(dataset["text"], trainer=trainer)
        self.tokenizer.save(str(self.model_path))
        print(f"Tokenizer saved to {self.model_path}")
        return self.tokenizer

    def load(self) -> Tokenizer:
        self.tokenizer = Tokenizer.from_file(self.model_path.as_posix())
        return self.tokenizer


if __name__ == "__main__":
    word2vec_tokenizer = Word2VecTokenizer().load()
    print(word2vec_tokenizer.encode("Hello, World!").ids)
    print(word2vec_tokenizer.decode([0, 1, 2, 3, 4, 5]))
