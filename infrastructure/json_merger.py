import json
import os
import logging
from config import TMP_FOLDER, OUT_FOLDER
from infrastructure.utils import ensure_folder_exists

logger = logging.getLogger(__name__)

def merge_json_files_by_unit(keywords: list) -> dict:
    """
    TMP_FOLDER 内の JSON ファイルを、ファイル名に含まれる単位（keywords に該当する文字列）ごとに合算する。

    合算処理:
      - 各 JSON ファイルは XLSX 変換時の出力（構造は { sheet: { group: [row, ...], ... } } ）とする。
      - 各 row について、結合主キー「グループ」「指図書No」「補足」でマージし、"時間" フィールドの値を合計する。
      - 合算対象の行（"時間" が数値または null の場合）は、"merged_files" フィールドに寄与したファイル名を必ずリストで追加する。
    その後、unit ごとにマージした結果を、さらに「グループ」ごとに分けた辞書形式に変換し、
    OUT_FOLDER に output_{unit}.json として保存します。
    戻り値は、unit → 出力ファイルパス の辞書です。
    """
    merged_data = {}  # unit -> { composite_key: row }　（composite_key = (グループ, 指図書No, 補足)）
    ensure_folder_exists(OUT_FOLDER)
    
    # TMP_FOLDER 内の JSON ファイルを処理
    for filename in os.listdir(TMP_FOLDER):
        if not filename.lower().endswith(".json"):
            continue
        file_path = os.path.join(TMP_FOLDER, filename)
        unit_found = None
        for kw in keywords:
            if kw in filename:
                unit_found = kw
                break
        if not unit_found:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("JSON読み込みエラー %s: %s", file_path, e)
            continue
        if unit_found not in merged_data:
            merged_data[unit_found] = {}
        # data は { sheet: { group: [row, ...], ... }, ... }
        for sheet, groups in data.items():
            for group, rows in groups.items():
                for row in rows:
                    try:
                        composite_key = (
                            str(row["グループ"]).strip(),
                            str(row["指図書No"]).strip(),
                            str(row["補足"]).strip()
                        )
                    except Exception as e:
                        logger.error("必要なキーが存在しない行: %s", row)
                        continue
                    # "時間" が null の場合は 0.0 として扱う
                    if row["時間"] is None:
                        time_val = 0.0
                    else:
                        try:
                            time_val = float(row["時間"])
                        except Exception as e:
                            logger.error("時間の値が不正な行 (ファイル %s): %s", file_path, row)
                            continue
                    if composite_key in merged_data[unit_found]:
                        merged_entry = merged_data[unit_found][composite_key]
                        merged_entry["時間"] += time_val
                        if "merged_files" in merged_entry:
                            if filename not in merged_entry["merged_files"]:
                                merged_entry["merged_files"].append(filename)
                        else:
                            merged_entry["merged_files"] = [filename]
                    else:
                        new_row = row.copy()
                        new_row["時間"] = time_val
                        new_row["merged_files"] = [filename]
                        merged_data[unit_found][composite_key] = new_row
    
    # ここから、各 unit ごとに「グループ」ごとに分ける
    final_output = {}  # unit -> { group_name: [row, ...], ... }
    for unit, comp_dict in merged_data.items():
        grouped = {}
        for comp_key, row in comp_dict.items():
            # comp_key の最初の要素がグループ名
            group_name = comp_key[0]
            if group_name not in grouped:
                grouped[group_name] = []
            grouped[group_name].append(row)
        final_output[unit] = grouped
    
    output_paths = {}
    for unit, merged_dict in final_output.items():
        out_filename = f"output_{unit}.json"
        out_path = os.path.join(OUT_FOLDER, out_filename)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(merged_dict, f, ensure_ascii=False, indent=4)
            output_paths[unit] = out_path
        except Exception as e:
            logger.error("出力ファイル書き出しエラー (%s): %s", out_path, e)
    return output_paths
