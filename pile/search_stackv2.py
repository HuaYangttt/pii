import sys
import os
from huggingface_hub import login
from dotenv import load_dotenv
load_dotenv()

import boto3
s3 = boto3.client('s3')
response = s3.list_buckets()

import json
from smart_open import open
from datasets import load_dataset
from hard_c import SecretSearcher

# argparse
import argparse
parser = argparse.ArgumentParser(description="Search for secrets in code files.")
parser.add_argument("--search_type", type=str, required=True, help="api/email")

args = parser.parse_args()

searcher = SecretSearcher()
if args.search_type == "email":
    searcher.search_data = searcher.email_secrets_data 
elif args.search_type == "api":
    searcher.search_data = searcher.api_secrets_data 
else:
    raise ValueError("Invalid search type. Choose 'api' or 'email'.")

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
s3 = session.client("s3")

def download_contents(files, prefilter=None):
    results = []
    for file in files:
        language = file.get("language", "unknown").lower()  # 默认语言字段
        if prefilter:
            match = all(file.get(k) == v for k, v in prefilter.items())
            if not match:
                continue
        s3_url = f"s3://softwareheritage/content/{file['blob_id']}"
        try:
            with open(s3_url, "rb", compression=".gz", transport_params={"client": s3}) as fin:
                content = fin.read().decode(file["src_encoding"])
                file["content"] = content
                matches = searcher.search(content, secrets_data=searcher.search_data)
                if matches:
                    results.append({
                        "language": language,
                        "path": file["path"],
                        "blob_id": file["blob_id"],
                        "content": content,
                        "matches": matches
                    })
            if matches != []:
                print("matches:", matches)
        except Exception as e:
            continue
    return {"files": results}

# 加载数据
ds = load_dataset("bigcode/the-stack-v2-train-full-ids", split="train", streaming=True)

prefilter = None

# 创建基础输出目录
base_output_dir = f"matched_files_{args.search_type}"
os.makedirs(base_output_dir, exist_ok=True)
file_output_dir = os.path.join(base_output_dir,'files')
os.makedirs(file_output_dir, exist_ok=True)

count = 0
file_counters = {}  # 每种语言的文件编号
match_count = 0

index_file = open(os.path.join(base_output_dir,  "index.jsonl"), "a", encoding="utf-8")

for i, row in enumerate(ds):
    matched_files = download_contents(row["files"], prefilter=prefilter)

    for file in matched_files["files"]:
        language = file["language"]
        content = file["content"]

        # 统计文件保存编号
        file_name = f"{count}_file.json"
        file_path = os.path.join(file_output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file, f, indent=2, ensure_ascii=False)

        
        for match in file["matches"]:
            secret_type = match.get("secret_type")

            match_count += 1
            index_target = index_file
            if match_count > 2000:
                f.close()
                index_target.close()
                exit(0)

            index_entry = {
                "secret_type": secret_type,
                "match": match.get("match"),
                "start": match.get("start"),
                "end": match.get("end"),
                "language": language,
                "path": file["path"],
                "blob_id": file["blob_id"],
                "save_path": file_path
            }
            index_target.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
            
        count += 1






# import os
# import json
# import boto3
# from smart_open import open
# from datasets import load_dataset
# from hard_c import SecretSearcher

# # SecretSearcher 和 boto3
# searcher = SecretSearcher()
# session = boto3.Session(
#     aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
#     aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
# s3 = session.client("s3")

# base_output_dir = "./output"
# unified_dir = os.path.join(base_output_dir, "contain_secrets")
# index_dir = os.path.join(base_output_dir, "index")
# os.makedirs(unified_dir, exist_ok=True)
# os.makedirs(index_dir, exist_ok=True)

# file_counters = {}  # {(language, type): count}
# index_files = {
#     "email": open(os.path.join(index_dir, "email_index.jsonl"), "a", encoding="utf-8"),
#     "api": open(os.path.join(index_dir, "api_index.jsonl"), "a", encoding="utf-8")
# }
# count = 0
# prefilter = None

# def download_contents(files, prefilter=None):
#     results = []
#     for file in files:
#         language = file.get("language", "unknown").lower()
#         if prefilter:
#             match = all(file.get(k) == v for k, v in prefilter.items())
#             if not match:
#                 continue
#         s3_url = f"s3://softwareheritage/content/{file['blob_id']}"
#         try:
#             with open(s3_url, "rb", compression=".gz", transport_params={"client": s3}) as fin:
#                 content = fin.read().decode(file["src_encoding"])
#                 matches = searcher.search(content)
#                 if matches:
#                     results.append({
#                         "language": language,
#                         "path": file["path"],
#                         "blob_id": file["blob_id"],
#                         "content": content,
#                         "matches": matches
#                     })
#         except Exception as e:
#             continue
#     return {"files": results}


# ds = load_dataset("bigcode/the-stack-v2-train-full-ids", split="train", streaming=True)
# ds = ds.map(lambda row: download_contents(row["files"]))

# for results in ds:
#     if results["files"] == []:
#         continue

#     for file in results["files"]:
#         language = file["language"]
#         content = file["content"]

#         # 统计文件保存编号
#         file_index = file_counters.get((language, "total"), 0)
#         file_name = f"{language}_file_{file_index}.json"
#         file_path = os.path.join(unified_dir, file_name)

#         # 保存原始文件
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(file, f, indent=2, ensure_ascii=False)
#         file_counters[(language, "total")] = file_index + 1

#         # 初始化计数
#         email_count = file_counters.get((language, "email"), 0)
#         api_count = file_counters.get((language, "api"), 0)

#         # 遍历匹配项
#         for match in file["matches"]:
#             secret_type = match.get("secret_type")

#             if secret_type == "email":
#                 email_count += 1
#                 file_counters[(language, "email")] = email_count
#                 index_target = index_files["email"]
#             else:
#                 api_count += 1
#                 file_counters[(language, "api")] = api_count
#                 index_target = index_files["api"]

#             index_entry = {
#                 "secret_type": secret_type,
#                 "match": match.get("match"),
#                 "start": match.get("start"),
#                 "end": match.get("end"),
#                 "language": language,
#                 "path": file["path"],
#                 "blob_id": file["blob_id"],
#                 "file_path": file_path
#             }
#             index_target.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

#         # 检查终止条件
#         if email_count > 1000 and api_count > 1000:
#             print(f"终止：{language} 的 email 和 api 文件都超过 1000")
#             index_files["email"].close()
#             index_files["api"].close()
#             exit(0)

#         count += 1

# # 正常结束时关闭 index 文件
# index_files["email"].close()
# index_files["api"].close()