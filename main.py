import tkinter as tk
import logging
import os
import sys
from presentation.ui import FileSearchUI

def tk_exception_handler(exc, val, tb):
    # Tkinter 内部の例外をキャッチし、Errフォルダのログに出力
    logging.exception("Unhandled Tkinter exception", exc_info=(exc, val, tb))
    print("Tkinter 内部で例外が発生しました。詳細は Err フォルダ内のログをご確認ください。", file=sys.stderr)

def setup_logging():
    # main.py のあるディレクトリ（Src）の親ディレクトリをプロジェクトルートとする
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..")
    error_folder = os.path.join(project_root, "Err")
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
    
    log_file = os.path.join(error_folder, "error.log")
    # コンソール出力とファイル出力（Err/error.log）を設定
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8")
        ]
    )

def main():
    setup_logging()
    try:
        root = tk.Tk()
        root.title("特定のファイルを検索")
        # Tkinter の例外ハンドラを上書き
        root.report_callback_exception = tk_exception_handler

        # 検索対象キーワードを定義
        keywords = ["金子", "本間"]
        FileSearchUI(root, keywords)
        root.mainloop()
    except Exception as e:
        logging.exception("Tkinter アプリケーション起動時にエラーが発生しました: %s", e)

if __name__ == '__main__':
    main()
