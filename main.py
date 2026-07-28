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
        messagebox.showerror("Error database", f"Gagal terhubung: {err}")
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
        self.win.geometry("800x650")

        self.storage = 0.0
        self.selector = None
        self.combos = {}

        self.setup_ui()
        self.load_from_db()

    def setup_ui(self):
        frame_storage = tk.Frame(self.win)
        frame_storage.pack(pady=5)

        lbl_storage = tk.Label(frame_storage, text="Masukkan Kapasitas Storage (MB):")
        lbl_storage.pack(side=tk.LEFT)

        self.entry_storage = tk.Entry(frame_storage, width=10)
        self.entry_storage.pack(side=tk.LEFT, padx=5)

        categories = {
            "-theme": {"navy": 9.4, "purple": 7.1, "green": 6.5, "red": 3.9, "yellow": 2.7},
            "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
            "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
            "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
            "-fonts": {"inter": 0.5, "JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
        }

        self.selector = TweakSelector(categories)

        frame_categories = tk.Frame(self.win)
        frame_categories.pack(pady=5)

        for category_name, category in self.selector.categories.items():
            lbl = tk.Label(frame_categories, text=f"{category_name}:")
            lbl.pack(anchor=tk.W)

            options_list = list(category.options.keys())
            combo = ttk.Combobox(frame_categories, values=options_list, state="readonly", width=20)
            combo.pack(anchor=tk.W, pady=2)
            self.combos[category_name] = combo

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=5)

        btn_simpan = tk.Button(btn_frame, text="Simpan", command=self.simpan_ke_db)
        btn_simpan.pack(side=tk.LEFT, padx=5)

        btn_muat = tk.Button(btn_frame, text="Muat Data", command=self.load_from_db)
        btn_muat.pack(side=tk.LEFT, padx=5)

        btn_hapus = tk.Button(btn_frame, text="Hapus Pilihan", command=self.hapus_dari_db)
        btn_hapus.pack(side=tk.LEFT, padx=5)

        btn_cek = tk.Button(btn_frame, text="Cek Total", command=self.cek_total)
        btn_cek.pack(side=tk.LEFT, padx=5)

        btn_undo = tk.Button(btn_frame, text="Undo", command=self.undo_terakhir)
        btn_undo.pack(side=tk.LEFT, padx=5)

        lbl_list = tk.Label(self.win, text="Pilihan Tweak:")
        lbl_list.pack()

        self.lb_selected = tk.Listbox(self.win, height=6, width=60)
        self.lb_selected.pack()

        lbl_db = tk.Label(self.win, text="Data di Database:")
        lbl_db.pack()

        frame_tree = tk.Frame(self.win)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(frame_tree, columns=("id", "kategori", "item", "ukuran", "created_at"), show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("id", text="ID")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("item", text="Item")
        self.tree.heading("ukuran", text="Ukuran (MB)")
        self.tree.heading("created_at", text="Dibuat")

        self.tree.column("id", width=50)
        self.tree.column("kategori", width=150)
        self.tree.column("item", width=150)
        self.tree.column("ukuran", width=100)
        self.tree.column("created_at", width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

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
        self.update_result_label(storage)

    def update_result_label(self, storage):
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

    def undo_terakhir(self):
        last_item, removed_size = self.selector.handle_undo()
        if last_item is None:
            messagebox.showinfo("Info", "Tidak ada pilihan untuk di-undo.")
            return

        kategori_nama = last_item.split(" (")[0]
        if kategori_nama in self.combos:
            self.combos[kategori_nama].set("")

        self.refresh_listbox()

        try:
            storage = float(self.entry_storage.get())
        except ValueError:
            storage = self.selector.total_size

        self.update_result_label(storage)

    def load_from_db(self):
        db = hubungkan_database()
        if db is None:
            return

        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, kategori, item, ukuran, created_at FROM tb_pilihan")
            rows = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            messagebox.showinfo("Sukses", f"Data berhasil dimuat: {len(rows)} records.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal memuat data: {err}")
        finally:
            if cursor:
                cursor.close()
            db.close()

    def hapus_dari_db(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus dari database!")
            return

        item_values = self.tree.item(selected[0])["values"]
        record_id = item_values[0]

        confirm = messagebox.askyesno("Konfirmasi", f"Hapus record ID {record_id} dari database?")
        if not confirm:
            return

        db = hubungkan_database()
        if db is None:
            return

        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM tb_pilihan WHERE id=%s"
            cursor.execute(sql, (record_id,))
            db.commit()

            self.tree.delete(selected[0])
            messagebox.showinfo("Sukses", f"Record ID {record_id} berhasil dihapus dari database!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal menghapus: {err}")
        finally:
            if cursor:
                cursor.close()
            db.close()

    def simpan_ke_db(self):
        db = hubungkan_database()
        if db is None:
            return

        cursor = None
        try:
            cursor = db.cursor()
            sql = "INSERT INTO tb_pilihan (kategori, item, ukuran) VALUES (%s, %s, %s)"

            for category_name, category in self.selector.categories.items():
                if category.selected:
                    val = (category_name, category.selected, category.selected_size)
                    cursor.execute(sql, val)

            db.commit()
            messagebox.showinfo("Sukses", "Data berhasil disimpan ke database!")
            self.load_from_db()
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal menyimpan: {err}")
        finally:
            if cursor:
                cursor.close()
            db.close()


if __name__ == "__main__":
    app = TweakApp()
    app.win.mainloop()
