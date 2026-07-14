import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os


def load_env(path=".env"):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


ENV = load_env()


def hubungkan_database():
    try:
        db = mysql.connector.connect(
            host=ENV.get("DB_HOST", "localhost"),
            user=ENV.get("DB_USER", "root"),
            password=ENV.get("DB_PASSWORD", ""),
            database=ENV.get("DB_NAME", "tweak_db"),
        )
        return db
    except mysql.connector.Error as err:
        messagebox.showerror("Error Database", f"Gagal terhubung: {err}")
        return None


class TweakCategory:
    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.selected = None
        self.selected_size = 0.0

    def validate_input(self, pilihan):
        if pilihan in self.options:
            return pilihan, True
        for opt in self.options:
            if opt.lower() == pilihan.lower() or opt.upper() == pilihan.upper():
                return opt, True
        return None, False

    def select(self, match):
        self.selected = match
        self.selected_size = self.options[match]
        return self.selected_size


class TweakSelector:
    def __init__(self, categories):
        self.categories = {}
        for name, opts in categories.items():
            self.categories[name] = TweakCategory(name, opts)
        self.selected_items = {}
        self.selected_order = []
        self.total_size = 0.0

    def select_tweak(self, category_name, pilihan):
        category = self.categories[category_name]

        if pilihan == "":
            return 0

        match, found = category.validate_input(pilihan)

        if found:
            size = category.select(match)
            key = f"{category.name} ({match})"
            self.selected_items[key] = size
            self.selected_order.append(key)
            self.total_size += size
            return size
        else:
            return None

    def display_selections(self):
        result = []
        for item in self.selected_order:
            result.append(f"{item}: {self.selected_items[item]} mb")
        result.append(f"total item yang dipilih: {len(self.selected_order)}")
        return "\n".join(result)

    def handle_undo(self):
        if not self.selected_order:
            return None, self.total_size

        last_item = self.selected_order.pop()
        removed_size = self.selected_items.pop(last_item)
        self.total_size -= removed_size

        return last_item, removed_size


class TweakApp:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Tweak Customizer")
        self.win.geometry("500x600")

        self.storage = 0.0
        self.selector = None
        self.combos = {}

        self.setup_ui()

    def setup_ui(self):
        lbl_storage = tk.Label(self.win, text="Masukkan Kapasitas Storage (MB):")
        lbl_storage.pack()

        self.entry_storage = tk.Entry(self.win)
        self.entry_storage.pack()

        categories = {
            "-theme": {"navy": 9.4, "purple": 7.1, "green": 6.5, "red": 3.9, "yellow": 2.7},
            "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
            "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
            "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
            "-fonts": {"inter": 0.5, "JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
        }

        self.selector = TweakSelector(categories)

        for category_name, category in self.selector.categories.items():
            lbl = tk.Label(self.win, text=f"Pilih {category_name}:")
            lbl.pack()

            options_list = list(category.options.keys())
            combo = ttk.Combobox(self.win, values=options_list, state="readonly")
            combo.pack()
            self.combos[category_name] = combo

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=10)

        btn_simpan = tk.Button(btn_frame, text="Simpan Pilihan", command=self.simpan_ke_db)
        btn_simpan.pack(side=tk.LEFT, padx=5)

        btn_cek = tk.Button(btn_frame, text="Cek Total", command=self.cek_total)
        btn_cek.pack(side=tk.LEFT, padx=5)

        btn_hapus = tk.Button(btn_frame, text="Hapus Kategori", command=self.hapus_kategori)
        btn_hapus.pack(side=tk.LEFT, padx=5)

        lbl_list = tk.Label(self.win, text="Kategori yang dipilih:")
        lbl_list.pack()

        self.lb_selected = tk.Listbox(self.win, height=8, width=60)
        self.lb_selected.pack()

        self.lbl_result = tk.Label(self.win, text="", justify=tk.LEFT)
        self.lbl_result.pack()

    def cek_total(self):
        try:
            storage = float(self.entry_storage.get())
        except ValueError:
            messagebox.showerror("Error", "Storage harus berupa angka!")
            return

        self.selector.selected_items = {}
        self.selector.selected_order = []
        self.selector.total_size = 0.0

        for category_name, combo in self.combos.items():
            pilihan = combo.get()
            if pilihan:
                self.selector.select_tweak(category_name, pilihan)

        self.refresh_listbox()

        result_text = self.selector.display_selections()
        result_text += f"\nTotal size: {self.selector.total_size} mb\n"
        result_text += f"Sisa storage: {storage - self.selector.total_size} mb"

        if self.selector.total_size > storage:
            result_text += "\nMelebihi kapasitas storage!"
        else:
            result_text += "\nStorage mencukupi."

        self.lbl_result.config(text=result_text)

    def refresh_listbox(self):
        self.lb_selected.delete(0, tk.END)
        for item in self.selector.selected_order:
            self.lb_selected.insert(tk.END, item)

    def hapus_kategori(self):
        selection = self.lb_selected.curselection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih kategori yang ingin dihapus dari daftar!")
            return

        idx = selection[0]
        item = self.lb_selected.get(idx).strip()

        if item not in self.selector.selected_items:
            self.refresh_listbox()
            return

        size = self.selector.selected_items.pop(item)
        if item in self.selector.selected_order:
            self.selector.selected_order.remove(item)
        self.selector.total_size -= size

        kategori_nama = item.split(" (")[0]
        if kategori_nama in self.combos:
            self.combos[kategori_nama].set("")

        self.refresh_listbox()
        self.cek_total()

    def simpan_ke_db(self):
        db = hubungkan_database()
        if db is None:
            return

        cursor = db.cursor()

        sql = "INSERT INTO tb_pilihan (kategori, item, ukuran) VALUES (%s, %s, %s)"

        try:
            for category_name, category in self.selector.categories.items():
                if category.selected:
                    val = (category_name, category.selected, category.selected_size)
                    cursor.execute(sql, val)

            db.commit()
            messagebox.showinfo("Sukses", "Data berhasil disimpan ke database!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal menyimpan: {err}")
        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    app = TweakApp()
    app.win.mainloop()
