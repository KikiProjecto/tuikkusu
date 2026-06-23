def validate_input(pilihan, options):
    if pilihan in options:
        return pilihan, True
    for opt in options:
        if opt.lower() == pilihan.lower() or opt.upper() == pilihan.upper():
            return opt, True
    return None, False

def process_selection(category, match, options, selected_items, selected_order):
    key = f"{category} ({match})"
    size_value = options[match]
    selected_items[key] = size_value
    selected_order.append(key)
    return size_value

def select_tweak(category, options, selected_items, selected_order):
    pilihan = input(f"pilih {category} anda: ").strip()
    
    if pilihan == "":
        print("ANDA TIDAK MEMILIH APAPUN & lanjut ke tweaks berikutnya.")
        return 0
    
    match, found = validate_input(pilihan, options)
    
    if found:
        print(f"yang anda MAKSUD pasti ->  \"{match}\"")
        return process_selection(category, match, options, selected_items, selected_order)
    else:
        print(f"pilihan {pilihan} untuk {category} ITU TIDAK TERSEDIA. silahkan coba lagi!")
        return select_tweak(category, options, selected_items, selected_order)

def display_selections(selected_items, selected_order):
    print("\nanda telah memilih :")
    for item in selected_order:
        print(f"{item}: {selected_items[item]} mb")
    print(f"total item yang dipilih: {len(selected_order)}")

def handle_undo(selected_items, selected_order, size_file):
    if not selected_order:
        print("Tidak ada pilihan yang dapat dibatalkan.")
        return size_file
        
    last_item = selected_order.pop()
    removed_size = selected_items.pop(last_item)
    size_file -= removed_size
    
    print(f"pilihan terakhir {last_item} dihapus, total size file dikurangi {removed_size} mb.")
    print("\npilihan tersisa setelah pembatalan:")
    for item in selected_order:
        print(f"{item}: {selected_items[item]} mb")
    print(f"\ntotal item setelah pembatalan: {len(selected_order)}")
    print(f"& total size files yang anda pilih sekarang :", size_file, "mb")
    
    return size_file

def main():
    storage = float(input("berapa ukuran storage anda (dalam mb)?? \n"))
    print("kustomisasi tweaks anda!\n")
    print("list pilihan tweaks yg tersedia :")
    print("-----------------------------------")
    
    categories = {
        "-theme": {"navy": 9.4, "purple": 7.1, "green": 2.5, "red": 3.0, "yellow": 2.7},
        "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
        "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
        "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
        "-fonts": {"inter": 0.5, "JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
    }
    
    size_file = 0
    selected_items = {}
    selected_order = []
    
    for category, options in categories.items():
        print(f"pilihan {category}: {list(options.keys())}\n")
        size_file += select_tweak(category, options, selected_items, selected_order)
    
    display_selections(selected_items, selected_order)
    print("\n& total size files yang anda pilih :", size_file, "mb")

    if size_file > storage:
        print("MAAF! total size file yang anda pilih melebihi batas storage yang anda miliki.")
        undo = input("apakah anda ingin membatalkan pilihan terakhir? (ya/tidak): ").strip().lower()
        if undo in ("ya", "y"):
            size_file = handle_undo(selected_items, selected_order, size_file)
            
            if size_file <= storage:
                print("sekarang storage anda mencukupi!.")
            else:
                print("masih MELEBIHI kapasitas storage anda!")
    elif size_file <= storage:
        print("storage anda mencukupi.")
    
    print("sisa storage yang dimiliki :", "tersisa", storage - size_file, "mb")

if __name__ == "__main__":
    main()
