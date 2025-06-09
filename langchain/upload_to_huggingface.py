import os
from huggingface_hub import HfApi, HfFolder, Repository
from dotenv import load_dotenv
load_dotenv()
def upload_to_huggingface(repo_name: str, local_dir: str):
    """
    Upload a local directory to a Hugging Face repository.

    Args:
        repo_name (str): The name of the Hugging Face repository.
        local_dir (str): The local directory to upload.
    """
    api = HfApi()
    token = HfFolder.get_token()
    
    # Create the repository if it doesn't exist
    api.create_repo(repo_id=repo_name, exist_ok=True)
    
    # Initialize the repository
    repo = Repository(local_dir=local_dir, clone_from=repo_name, token=token)
    
    # Push the changes
    repo.push_to_hub(commit_message="Upload files to Hugging Face")
    
    
upload_to_huggingface("myllms", "/Users/rizwanmushtaq/Downloads/gpt2.gguf")