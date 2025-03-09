import tkinter as tk
from tkinter import filedialog, messagebox
from use_cases.file_search_usecase import get_matched_files
from infrastructure.json_writer import write_json_output

class FileSearchUI(tk.Frame):
    def __init__(self, root, keywords):
        super().__init__(root, width=600, height=500, borderwidth=1, relief='groove')
        self.root = root
        self.keywords = keywords
        self.pack(fill=tk.BOTH, expand=True)
        self.pack_propagate(0)
        self.create_widgets()
    
    def create_widgets(self):
        # 上部ボタン群
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.select_folder_button = tk.Button(top_frame, text="フォルダを選択", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=10)
        self.info_button = tk.Button(top_frame, text="情報取得", command=self.show_selected_info)
        self.info_button.pack(side=tk.LEFT, padx=10)
        self.close_button = tk.Button(top_frame, text="閉じる", command=self.root.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=10)

        # 下部左右フレーム
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)
        
        # 左側：ファイル一覧
        left_frame = tk.Frame(bottom_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(left_frame, text="ファイル一覧").pack(anchor='w')
        # Ctrl／Shiftキーで複数選択可能なListbox
        self.file_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 右側：選択状態表示
        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(right_frame, text="選択状態").pack(anchor='w')
        self.info_listbox = tk.Listbox(right_frame)
        self.info_listbox.pack(fill=tk.BOTH, expand=True)
    
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_list(folder_path)
    
    def populate_file_list(self, folder_path):
        self.file_listbox.delete(0, tk.END)
        try:
            matched_files = get_matched_files(folder_path, self.keywords)
            if matched_files:
                for file in matched_files:
                    self.file_listbox.insert(tk.END, file)
            else:
                self.file_listbox.insert(tk.END, "一致するファイルがありません")
            self.info_listbox.delete(0, tk.END)
        except Exception as e:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, f"エラー: {e}")
    
    def show_selected_info(self):
        """
        左側のListboxでの選択状態に基づいて、
        各ファイルが選択されていればTrue、未選択ならFalseと表示し、
        その内容を JSON ファイルとして OUTPUT フォルダに保存し、
        出力結果はメッセージボックスで表示する
        """
        self.info_listbox.delete(0, tk.END)
        try:
            selected_indices = self.file_listbox.curselection()
            files = self.file_listbox.get(0, tk.END)
            output_data = {}
            for idx, file in enumerate(files):
                state = idx in selected_indices
                output_data[file] = state
                self.info_listbox.insert(tk.END, f"{file} : {state}")
            
            # JSONファイルとして出力
            json_filepath = write_json_output(output_data)
            # メッセージボックスで出力結果を表示
            messagebox.showinfo("JSON出力", f"JSONファイルが作成されました:\n{json_filepath}")
        except Exception as e:
            self.info_listbox.insert(tk.END, f"エラー: {e}")
