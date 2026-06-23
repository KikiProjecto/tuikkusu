storage = float(input("berapa ukuran storage anda (dalam mb)?? \n"))
print("kustomisasi tweaks anda!\n")
print("list pilihan tweaks yg tersedia :")
print("-----------------------------------")

categories = {
    "-theme": {"navy": 9.4, "purple": 7.1, "green": 2.5, "red": 3.0, "yellow": 2.7},
    "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
    "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
    "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
    "-fonts": {"inter": 0.5,"JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
}

size_file = 0
selected_items = {}
selected_order = []

for category, options in categories.items():

    print(f"pilihan {category}: {list(options.keys())}\n")

    while True: 
        pilihan = input(f"pilih {category} anda: ").strip()
        if pilihan == "":
            print("ANDA TIDAK MEMILIH APAPUN & lanjut ke tweaks berikutnya.")
            break
        if pilihan in options:
            key = f"{category} ({pilihan})"
            size_file += options[pilihan] 
            selected_items[key] = options[pilihan]
            selected_order.append(key)
            break
        
        pilihan_lower = pilihan.lower()
        pilihan_upper = pilihan.upper()
        match = None
        for opt in options:
            if opt.lower() == pilihan_lower or opt.upper() == pilihan_upper:
                match = opt
                break
        if match:
            print(f"yang anda MAKSUD pasti ->  \"{match}\"")
            key = f"{category} ({match})"
            size_file += options[match]
            selected_items[key] = options[match]
            selected_order.append(key)
            break
        print(f"pilihan {pilihan} untuk {category} ITU TIDAK TERSEDIA. silahkan coba lagi!")

print("\nanda telah memilih :")
for item in selected_order:
    print(f"{item}: {selected_items[item]} mb")

print(f"total item yang dipilih: {len(selected_order)}")
print("\n& total size files yang anda pilih :", size_file, "mb")

if size_file > storage:
    print("MAAF! total size file yang anda pilih melebihi batas storage yang anda miliki.")
    if selected_order:
        undo = input("apakah anda ingin membatalkan pilihan terakhir? (ya/tidak): ").strip().lower()
        if undo in ("ya", "y"):
            last_item = selected_order.pop()
            last_item_value = last_item
            removed_size = selected_items.pop(last_item_value)
        
            size_file -= removed_size
            
            print(f"pilihan terakhir {last_item} dihapus, total size file dikurangi {removed_size} mb.")
            print("\npilihan tersisa setelah pembatalan:")
            for item in selected_order:
                print(f"{item}: {selected_items[item]} mb")
            
            print(f"\ntotal item setelah pembatalan: {len(selected_order)}")
            print("\n& total size files yang anda pilih sekarang :", size_file, "mb")
            
            if size_file <= storage:
                print("sekarang storage anda mencukupi!.")
            else:
                print("masih MELEBIHI kapasitas storage anda!")

elif size_file <= storage:
    print("storage anda mencukupi.")

print("sisa storage yang dimiliki :", "tersisa", storage - size_file, "mb")
