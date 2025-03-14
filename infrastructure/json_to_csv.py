import json
import csv
import os
import logging

logger = logging.getLogger(__name__)

def convert_json_file_to_csv(json_filepath: str, csv_filepath: str) -> bool:
    """
    指定された JSON ファイルを読み込み、その内容を CSV ファイルに変換して csv_filepath に保存します。
    JSON の形式は、辞書型でキーがグループ名、値がそのグループの行リスト（各行は辞書）となっていることを想定しています。
    各グループの行をフラットに連結し、"merged_files" がリストの場合はカンマ区切りの文字列に変換します。
    """
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("JSONファイルの読み込みエラー (%s): %s", json_filepath, e)
        return False

    # data は { "グループ名": [row, row, ...], ... } の形式を想定
    rows = []
    for group, group_rows in data.items():
        for row in group_rows:
            # merged_files がリストなら文字列に変換
            if "merged_files" in row and isinstance(row["merged_files"], list):
                row["merged_files"] = ", ".join(row["merged_files"])
            rows.append(row)
    
    if not rows:
        logger.info("変換対象の行が存在しません: %s", json_filepath)
        return False

    headers = list(rows[0].keys())
    try:
        with open(csv_filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        logger.error("CSVファイル書き出しエラー (%s): %s", csv_filepath, e)
        return False

    return True
