import os
import json
from datasets import Dataset
from huggingface_hub import login

from dotenv import load_dotenv
load_dotenv()



STORE_HF_USERNAME = "yanghuattt"  # Your Hugging Face username
DATASET_NAME="pii-stackv2-demo"


def load_json_lines(file_path):
    with open(file_path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def json_to_dataset(jsonl_data):
    return Dataset.from_list(jsonl_data)

def add_content(json_data, root_dir="/home/hyang45/se_git_repo/pii/pile"):
    for item in json_data:
        save_path = item.get("save_path", None)
        if save_path is None:
            raise ValueError("save_path is not found in the item.")
        else:
            with open(root_dir+'/'+save_path, "r") as f:
                content = json.load(f)
                content = content.get("content", None)
            item["content"] = content
    return json_data

def find_and_load_json_files(directory):
    json_data = []
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    for json_file in json_files:
        with open(json_file, "r") as f:
            data = json.load(f)
            
#             {
#   "language": "makefile",
#   "path": "/www/p5-Mozilla-CA/Makefile",
#   "blob_id": "0576d98de09d7d0aec81f03844fcc35c58842ae5",
#   "content": "# $OpenBSD$\n\nCOMMENT =\tMozilla's CA cert bundle in PEM format\n\nMODULES =\tcpan\nDISTNAME =\tMozilla-CA-20120823\nCATEGORIES =\twww\nUSE_GROFF =\tYes\n\nMAINTAINER =\tLawrence Teo <lteo@openbsd.org>\n\n# MPLv1.1 / GPLv2+ / LGPLv2.1+\nPERMIT_PACKAGE_CDROM =\t\tYes\n\n.include <bsd.port.mk>\n",
#   "matches": [
#     {
#       "secret_type": "email",
#       "match": "lteo@openbsd.org",
#       "start": 170,
#       "end": 186
#     }
#   ]
# }
            index_entry = {
                "original_path": data["path"],
                "language": data["language"],
                "blob_id": data["blob_id"],
                "content": data["content"],
                "matches": data["matches"],
            }
            json_data.append(index_entry)
    return json_data

def save_list_to_jsonl(data, file_path):
    with open(file_path, "w") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")


def upload_jsonl_to_huggingface(
    jsonl_file_path: str,
    repo_id: str,
    private: bool = True,
    token: str = None
):
    """
    Load a .jsonl file, create a Hugging Face Dataset, and push it to the hub.

    Args:
        jsonl_file_path (str): Path to your .jsonl file.
        repo_id (str): Target repo ID on Hugging Face Hub, e.g., "your_username/your_dataset_name".
        private (bool): Whether to upload as a private dataset. Default is True.
        token (str, optional): Hugging Face token. If not provided, will prompt login.
    """

    # Step 1: Login (only if token is not passed)
    if token:
        login(token=token)
    else:
        login()

    # Step 2: Load .jsonl file
    data = []
    with open(jsonl_file_path, "r") as f:
        for line in f:
            if line.strip():  # skip empty lines
                data.append(json.loads(line))

    # Step 3: Create Dataset
    dataset = Dataset.from_list(data)

    # Step 4: Push to Hub
    dataset.push_to_hub(repo_id, private=private)
    print(f"✅ Dataset successfully pushed to https://huggingface.co/datasets/{repo_id}")


    






if __name__ == "__main__":
    #api_matched_file = "/home/hyang45/se_git_repo/pii/pile/matched_files_api/index.json"
    #email_matched_file = "/home/hyang45/se_git_repo/pii/pile/matched_files_email/index.json"

    # api_matched_data = load_json(api_matched_file)
    # email_matched_data = load_json(email_matched_file)

    # # print("api_matched_data: ", len(api_matched_data))
    # # print(api_matched_data[0])
    # # assert 0

    # api_matched_data = add_content(api_matched_data)
    # email_matched_data = add_content(email_matched_data)

    # print("api_matched_data: ", len(api_matched_data))
    # print(api_matched_data[0])
    # assert 0

    api_matched_data = find_and_load_json_files("/home/hyang45/se_git_repo/pii/pile/matched_files_api/files")
    email_matched_data = find_and_load_json_files("/home/hyang45/se_git_repo/pii/pile/matched_files_email/files")

    # print("api_matched_data: ", len(api_matched_data))
    # print(api_matched_data[0])
    # assert 0

    # Save the data to JSONL files
    api_matched_file = "/home/hyang45/se_git_repo/pii/pile/matched_files_api/hf_ready_api.jsonl"
    email_matched_file = "/home/hyang45/se_git_repo/pii/pile/matched_files_email/hf_ready_email.jsonl"
    save_list_to_jsonl(api_matched_data, api_matched_file)
    save_list_to_jsonl(email_matched_data, email_matched_file)

    # upload to hf
    upload_jsonl_to_huggingface(
        api_matched_file,
        STORE_HF_USERNAME+"/"+DATASET_NAME+"-api",
        private=False,
        token=os.environ["HUGGINGFACE_HUB_TOKEN"]
    )
    upload_jsonl_to_huggingface(
        email_matched_file,
        STORE_HF_USERNAME+"/"+DATASET_NAME+"-email",
        private=False,
        token=os.environ["HUGGINGFACE_HUB_TOKEN"]
    )


