# coding: utf-8

import tkinter as tk
from tkinter import ttk, messagebox

from krypto_gui_smalk.resource_manager import ResourceManager
from alerk_pack.crypto import str2bytes, bytes2str, gen_sym_key, sym_key_to_str, str_to_sym_key, sym_encrypt, sym_decrypt


class App(tk.Tk):
    def __init__(self, rm: ResourceManager):
        super().__init__()

        self.title("krypto_gui_smalk")
        self.iconphoto(False, tk.PhotoImage(file=rm.ico_path()))

        self.geometry("700x400")
        self.minsize(500, 300)

        # Key section
        self.key_frame = ttk.Frame(self, padding=5)
        self.key_frame.pack(fill=tk.X)

        ttk.Label(self.key_frame, text="Key:").pack(side=tk.LEFT)
        self.key_entry = ttk.Entry(self.key_frame, width=55)
        self.key_entry.pack(side=tk.LEFT, padx=5)

        self.key_entry.bind("<Control-a>", self._select_all_entry)
        self.key_entry.bind("<Control-A>", self._select_all_entry)
        self.key_entry.bind("<Control-v>", self._paste_over_selection_entry)
        self.key_entry.bind("<Control-V>", self._paste_over_selection_entry)

        self.generate_btn = ttk.Button(
            self.key_frame,
            text="Generate",
            command=self.generate_key,
            width=10
        )
        self.generate_btn.pack(side=tk.LEFT)

        # Input and Output texts
        self.text_frame = ttk.Frame(self, padding=5)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # Input (left)
        self.input_frame = ttk.Frame(self.text_frame)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(self.input_frame, text="Input:").pack(anchor=tk.W)
        self.input_text = tk.Text(self.input_frame, height=8, width=30, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        self.input_text.bind("<Control-a>", self._select_all_text)
        self.input_text.bind("<Control-A>", self._select_all_text)
        self.input_text.bind("<Control-v>", self._paste_over_selection_text)
        self.input_text.bind("<Control-V>", self._paste_over_selection_text)

        # Output (right)
        self.output_frame = ttk.Frame(self.text_frame)
        self.output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(self.output_frame, text="Output:").pack(anchor=tk.W)
        self.output_text = tk.Text(self.output_frame, height=8, width=30, wrap=tk.WORD, state="disabled")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.output_text.bind("<Control-a>", self._select_all_text)
        self.output_text.bind("<Control-A>", self._select_all_text)

        # Buttons
        self.button_frame = ttk.Frame(self, padding=5)
        self.button_frame.pack(fill=tk.X)

        self.encrypt_btn = ttk.Button(
            self.button_frame,
            text="Encrypt",
            command=self.encrypt_text,
            width=10
        )
        self.encrypt_btn.pack(side=tk.LEFT, padx=2)

        self.decrypt_btn = ttk.Button(
            self.button_frame,
            text="Decrypt",
            command=self.decrypt_text,
            width=10
        )
        self.decrypt_btn.pack(side=tk.LEFT)

    def _select_all_entry(self, event):
        self.key_entry.select_range(0, tk.END)
        return "break"

    def _select_all_text(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def _paste_over_selection_entry(self, event):
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, self.clipboard_get())
        return "break"

    def _paste_over_selection_text(self, event):
        text_widget = event.widget
        if text_widget.tag_ranges("sel"):
            text_widget.delete("sel.first", "sel.last")
        text_widget.insert("insert", self.clipboard_get())
        return "break"

    def paste_text_to_output(self, text: str):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def generate_key(self):
        try:
            key = gen_sym_key()
            key_str = sym_key_to_str(key)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot generate key: {e}")
            return

        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, f"{key_str}")

    def encrypt_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        key_str = self.key_entry.get().strip()
        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if text == "":
            messagebox.showerror("Error", "Input text to encrypt (left)")
            return
        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        try:
            text_b: bytes = text.encode(encoding="utf-8")
            text_en: bytes = sym_encrypt(text_b, key)
            text_en_coded: str = bytes2str(text_en)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot encrypt: {e}")
            return

        self.paste_text_to_output(f"{text_en_coded}")

    def decrypt_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        key_str = self.key_entry.get().strip()

        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if text == "":
            messagebox.showerror("Error", "Input text to decrypt (left)")
            return

        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        text_en_coded = text
        try:
            text_en: bytes = str2bytes(text_en_coded)
            text_b: bytes = sym_decrypt(text_en, key)
            text: str = text_b.decode(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot decrypt: {e}")
            return

        self.paste_text_to_output(f"{text}")
