import os

# PROJECT_ROOT: Src の親ディレクトリ
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 各フォルダのパス
IN_FOLDER = os.path.join(PROJECT_ROOT, "In")
OUT_FOLDER = os.path.join(PROJECT_ROOT, "Out")
TMP_FOLDER = os.path.join(PROJECT_ROOT, "Tmp")
ERR_FOLDER = os.path.join(PROJECT_ROOT, "Err")

# ログファイルのパス
LOG_FILE = os.path.join(ERR_FOLDER, "error.log")

# 検索対象キーワード
KEYWORDS = ["金子", "本間"]
