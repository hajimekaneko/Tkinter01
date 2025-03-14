import json
import logging
from openpyxl import load_workbook

logger = logging.getLogger(__name__)

def extract_xlsx_to_json(file_path: str) -> dict:
    """
    指定された XLSX ファイルの内容を JSON 形式の辞書として抜き出す関数。
    ・各シートの 1 行目をヘッダーとして使用し、2 行目以降をデータ行として扱う。
    ・ヘッダーに「グループ」が存在すれば、その列の値をグループキーとして利用し、
      グループ列が空欄の場合は直前のグループ（current_group）の値を割り当てます。
    結果は { シート名: { グループ名: [rowの辞書, ...], ... }, ... } の形式となる。
    """
    try:
        workbook = load_workbook(file_path, data_only=True)
        result = {}
        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                result[sheet_name] = {}
                continue
            headers = list(rows[0])
            try:
                group_index = headers.index("グループ")
            except ValueError:
                group_index = 0
            data_by_group = {}
            current_group = None
            for row in rows[1:]:
                if all(cell is None for cell in row):
                    continue
                group_value = row[group_index]
                if group_value is not None and str(group_value).strip() != "":
                    current_group = group_value
                if current_group is None:
                    current_group = "UNDEFINED"
                row_dict = {header: value for header, value in zip(headers, row)}
                row_dict["グループ"] = current_group
                if current_group not in data_by_group:
                    data_by_group[current_group] = []
                data_by_group[current_group].append(row_dict)
            result[sheet_name] = data_by_group
        return result
    except Exception as e:
        logger.error("XLSX ファイルの読み込みエラー: %s", e)
        raise e

def extract_xlsx_to_json_str(file_path: str) -> str:
    data = extract_xlsx_to_json(file_path)
    return json.dumps(data, ensure_ascii=False, indent=4)
