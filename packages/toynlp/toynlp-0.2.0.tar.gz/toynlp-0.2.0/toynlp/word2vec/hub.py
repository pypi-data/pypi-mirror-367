from pathlib import Path

from huggingface_hub import HfApi

from toynlp.word2vec.inference import load_tokenizer_model
from toynlp.word2vec.model import CbowModel


def push_model_to_hub(model: CbowModel, repo_id: str) -> None:
    """Push the model to the Hugging Face Hub."""
    model.save_pretrained(repo_id)
    model.push_to_hub(repo_id)
    print(f"Model pushed to Hugging Face Hub at {repo_id}")


def push_file_to_hub(path: Path, repo_id: str) -> None:
    """Push the tokenizer to the Hugging Face Hub."""
    api = HfApi()
    api.upload_file(
        path_or_fileobj=path,
        path_in_repo=path.name,
        repo_id=repo_id,
    )


if __name__ == "__main__":
    from toynlp.paths import W2V_TOKENIZER_PATH, CBOW_MODEL_PATH, SKIP_GRAM_MODEL_PATH

    tokenizer, model = load_tokenizer_model()

    repo_id = "AI-Glimpse/word2vec"
    push_model_to_hub(model, repo_id)
    push_file_to_hub(W2V_TOKENIZER_PATH, repo_id)
    push_file_to_hub(CBOW_MODEL_PATH, repo_id)
    push_file_to_hub(SKIP_GRAM_MODEL_PATH, repo_id)
