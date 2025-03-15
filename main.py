import tkinter as tk
import logging
import os
import sys
from presentation.ui import ResultMergeUI
from config import PROJECT_ROOT, ERR_FOLDER, KEYWORDS

def tk_exception_handler(exc, val, tb):
    logging.exception("Unhandled Tkinter exception", exc_info=(exc, val, tb))
    print("Tkinter 内部で例外が発生しました。詳細は Err フォルダ内のログをご確認ください。", file=sys.stderr)

def setup_logging():
    if not os.path.exists(ERR_FOLDER):
        os.makedirs(ERR_FOLDER)
    log_file = ERR_FOLDER + "/error.log"
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
        root.title("実績合算・分析アプリ")
        root.report_callback_exception = tk_exception_handler
        ResultMergeUI(root, KEYWORDS)
        root.mainloop()
    except Exception as e:
        logging.exception("Tkinter アプリケーション起動時にエラーが発生しました: %s", e)

if __name__ == '__main__':
    main()
