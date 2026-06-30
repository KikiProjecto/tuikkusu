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
    
    def select_tweak(self, category_name):
        category = self.categories[category_name]
        pilihan = input(f"pilih {category.name} anda: ").strip()
        
        if pilihan == "":
            print("ANDA TIDAK MEMILIH APAPUN & lanjut ke tweaks berikutnya.")
            return 0
        
        match, found = category.validate_input(pilihan)
        
        if found:
            print(f"yang anda MAKSUD pasti ->  \"{match}\"")
            size = category.select(match)
            key = f"{category.name} ({match})"
            self.selected_items[key] = size
            self.selected_order.append(key)
            self.total_size += size
            return size
        else:
            print(f"pilihan {pilihan} untuk {category.name} ITU TIDAK TERSEDIA. silahkan coba lagi!")
            return self.select_tweak(category_name)
    
    def display_selections(self):
        print("\nanda telah memilih :")
        for item in self.selected_order:
            print(f"{item}: {self.selected_items[item]} mb")
        print(f"total item yang dipilih: {len(self.selected_order)}")
    
    def handle_undo(self):
        if not self.selected_order:
            print("Tidak ada pilihan yang dapat dibatalkan.")
            return self.total_size
        
        last_item = self.selected_order.pop()
        removed_size = self.selected_items.pop(last_item)
        self.total_size -= removed_size
        
        print(f"pilihan terakhir {last_item} dihapus, total size file dikurangi {removed_size} mb.")
        print("\npilihan tersisa setelah pembatalan:")
        for item in self.selected_order:
            print(f"{item}: {self.selected_items[item]} mb")
        print(f"\ntotal item setelah pembatalan: {len(self.selected_order)}")
        print(f"& total size files yang anda pilih sekarang :", self.total_size, "mb")
        
        return self.total_size


class TweakApp:
    def __init__(self):
        self.storage = 0.0
        self.selector = None
    
    def initialize_storage(self):
        try:
            self.storage = float(input("berapa ukuran storage anda (dalam mb)?? \n"))
            if self.storage < 0:
                raise ValueError("ukuran storage tidak boleh negatif")
        except ValueError as e:
            print(f"input tidak valid: {e}")
            return False
        return True
    
    def setup_categories(self):
        categories = {
            "-theme": {"navy": 9.4, "purple": 7.1, "green": 6.5, "red": 3.9, "yellow": 2.7},
            "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
            "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
            "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
            "-fonts": {"inter": 0.5, "JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
        }
        self.selector = TweakSelector(categories)
    
    def run(self):
        if not self.initialize_storage():
            return
        
        self.setup_categories()
        
        print("kustomisasi tweaks anda!\n")
        print("list pilihan tweaks yg tersedia :")
        print("-----------------------------------")
        
        for category_name, category in self.selector.categories.items():
            print(f"pilihan {category_name}: {list(category.options.keys())}\n")
            self.selector.select_tweak(category_name)
        
        self.selector.display_selections()
        print("\n& total size files yang anda pilih :", self.selector.total_size, "mb")
        
        if self.selector.total_size > self.storage:
            print("total size file yang anda pilih melebihi batas storage yang anda miliki.")
            try:
                undo = input("apakah anda ingin membatalkan pilihan terakhir? (ya/tidak): ").strip().lower()
                if undo in ("ya", "y"):
                    self.selector.handle_undo()
                    
                    if self.selector.total_size <= self.storage:
                        print("sekarang storage anda mencukupi!.")
                    else:
                        print("masih MELEBIHI kapasitas storage anda!")
            except Exception as e:
                print(f"terjadi kesalahan: {e}")
        elif self.selector.total_size <= self.storage:
            print("storage anda mencukupi.")
        
        print("sisa storage yang dimiliki :", "tersisa", self.storage - self.selector.total_size, "mb")


if __name__ == "__main__":
    app = TweakApp()
    app.run()