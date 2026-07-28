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
            user=ENV.get("DB_USER", "tuikkusu"),
            password=ENV.get("DB_PASSWORD", "tuikkusu123"),
            database=ENV.get("DB_NAME", "tweak_db"),
        )
        return db
    except mysql.connector.Error as err:
        messagebox.showerror("Error Database", f"Gagal terhubung: {err}")
        return None


class TweakCategory:
    @classmethod
    def load_options_from_db(cls):
        db = hubungkan_database()
        if db is None:
            return {}
        cursor = None
        options = {}
        try:
            cursor = db.cursor()
            cursor.execute("SELECT kategori, item, ukuran FROM tb_pilihan")
            rows = cursor.fetchall()
            for kategori, item, ukuran in rows:
                options.setdefault(kategori, {})[item] = float(ukuran)
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal memuat opsi: {err}")
        finally:
            if cursor:
                cursor.close()
            db.close()
        return options

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

    @classmethod
    def load_categories_from_db(cls):
        options = TweakCategory.load_options_from_db()
        return cls(options)

    def calculate_total(self):
        self.total_size = sum(self.selected_items.values())
        return self.total_size

    def select_tweak(self, category_name, pilihan):
        category = self.categories[category_name]

        if pilihan == "":
            return 0

        match, found = category.validate_input(pilihan)

        if found:
            size = category.select(match)
            key = f"{category.name} ({match})"
            self.selected_items[key] = size
            if key not in self.selected_order:
                self.selected_order.append(key)
            self.calculate_total()
            return size
        else:
            return None

    def display_selections(self):
        result = []
        for item in self.selected_order:
            result.append(f"{item}: {self.selected_items[item]} mb")
        result.append(f"total item yang dipilih: {len(self.selected_order)}")
        return "\n".join(result)

    def delete_tweak(self, record_id):
        db = hubungkan_database()
        if db is None:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            sql = "DELETE FROM tb_pilihan WHERE id=%s"
            cursor.execute(sql, (record_id,))
            db.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            messagebox.showerror("Error Database", f"Gagal menghapus data: {err}")
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def handle_undo(self):
        if not self.selected_order:
            return None, self.total_size

        last_item = self.selected_order.pop()
        removed_size = self.selected_items.pop(last_item)
        self.total_size -= removed_size

        return last_item, removed_size

    def reset(self):
        self.selected_items = {}
        self.selected_order = []
        self.total_size = 0.0
        for category in self.categories.values():
            category.selected = None
            category.selected_size = 0.0


class TweakApp:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Tuikkusu - Tweak Customizer")
        self.win.geometry("800x650")

        self.storage = 0.0
        self.selector = None
        self.combos = {}

        self.setup_ui()
        self.reset_all()

    def setup_ui(self):
        frame_storage = tk.Frame(self.win)
        frame_storage.pack(pady=5)

        lbl_storage = tk.Label(frame_storage, text="Masukkan Kapasitas Storage (MB):")
        lbl_storage.pack(side=tk.LEFT)

        self.entry_storage = tk.Entry(frame_storage, width=10)
        self.entry_storage.pack(side=tk.LEFT, padx=5)

        categories = TweakCategory.load_options_from_db()
        if not categories:
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
            combo.set("")
            combo.bind("<<ComboboxSelected>>", lambda e: self.on_selection_change())
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

        btn_reset = tk.Button(btn_frame, text="Reset", command=self.reset_all)
        btn_reset.pack(side=tk.LEFT, padx=5)

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

        self.lbl_status = tk.Label(self.win, text="Total Digunakan: 0.0 MB | Sisa Storage: 0.0 MB", justify=tk.LEFT)
        self.lbl_status.pack()

    def reset_all(self):
        db = hubungkan_database()
        if db:
            cursor = None
            try:
                cursor = db.cursor()
                cursor.execute("TRUNCATE TABLE tb_pilihan")
                db.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Error Database", f"Gagal mereset database: {err}")
            finally:
                if cursor:
                    cursor.close()
                db.close()

        self.selector.reset()
        self.storage = 0.0
        self.entry_storage.delete(0, tk.END)
        for combo in self.combos.values():
            combo.set("")
        self.lb_selected.delete(0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_status.config(text="Total Digunakan: 0.0 MB | Sisa Storage: 0.0 MB")
        messagebox.showinfo("Reset", "Semua data lokal dan database telah direset!")

    def on_selection_change(self):
        try:
            storage = float(self.entry_storage.get())
        except ValueError:
            storage = None

        self.selector.selected_items = {}
        self.selector.selected_order = []
        self.selector.total_size = 0.0

        for category_name, combo in self.combos.items():
            pilihan = combo.get()
            if pilihan:
                self.selector.select_tweak(category_name, pilihan)

        self.refresh_listbox()
        self.update_status_label(storage)

    def update_status_label(self, storage):
        total = self.selector.calculate_total()
        if storage is None:
            try:
                storage = float(self.entry_storage.get())
            except ValueError:
                storage = 0.0

        sisa = storage - total
        self.lbl_status.config(text=f"Total Digunakan: {total} MB | Sisa Storage: {sisa} MB")

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
        self.update_status_label(storage)

        if self.selector.total_size > storage:
            messagebox.showwarning("Peringatan", "Total pilihan melebihi kapasitas storage!")
        else:
            messagebox.showinfo("Info", f"Storage mencukupi.\nTotal: {self.selector.total_size} MB\nSisa: {storage - self.selector.total_size} MB")

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
            storage = None

        self.update_status_label(storage)

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
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus dari tabel!")
            return

        item_values = self.tree.item(selected[0])["values"]
        record_id = item_values[0]

        confirm = messagebox.askyesno("Konfirmasi", f"Hapus record ID {record_id} dari database?")
        if not confirm:
            return

        if self.selector.delete_tweak(record_id):
            self.tree.delete(selected[0])
            messagebox.showinfo("Sukses", f"Record ID {record_id} berhasil dihapus!")
            self.on_selection_change()

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
