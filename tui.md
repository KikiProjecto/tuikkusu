Here is a comprehensive, production-ready specification document written in English. It is explicitly structured to serve as an ultimate system prompt for advanced AI software engineering agents to build your dream Go-based TUI application.

---

# AI Agent Build Specification: `tuikkusu` — Gamified OS Tweak Selector TUI

## 1. Project Overview & Philosophy

`tuikkusu` is a highly stylized, gamified Terminal User Interface (TUI) utility built in **Go (Golang)**. It reimagines a linear Python CLI storage-allocation script into a responsive, visually engaging desktop configuration suite.

The application utilizes an advanced terminal graphics stack to render animations, distinct category-specific color palettes, and real-time state changes resembling premium video game inventory or selection screens.

### Core Architecture Requirements

* **Language**: Go (Golang 1.21+)
* **TUI Stack Framework**: Charmbracelet ecosystem:
* `bubbletea`: The core runtime engine leveraging the Elm Architecture (Model-View-Update).
* `lipgloss`: For strict, terminal-agnostic layout structures, custom borders, padding, and hex-color processing.
* `bubbles`: For pre-built functional UI components (e.g., text inputs, progress bars, viewports).


* **Performance Goals**: Zero-allocation frame refreshes, native handling of ANSI escape sequences, smooth terminal rendering, and explicit handling of window resizing events.

---

## 2. Core Logic Mapping & Enhancements

The fundamental resource management logic from `main.py` must be cleanly translated into idiomatic Go data structures while preserving mathematical parity and option values.

### 2.1 State Representation

```go
type TweakOption struct {
    Name        string
    SizeMB      float64
    Description string // Gamified lore/flavor text
}

type Category struct {
    Key     string // e.g., "-theme"
    Options []TweakOption
}

```

### 2.2 Functional Rules Blueprint

1. **Storage Capacity Input**: The runtime must securely capture the user's base storage allocation (in Megabytes) via an interactive numeric text field component before customization starts.
2. **Sequential Progression**: Customization iterates through the exact structural sequence of the original Python script: `-theme` $\rightarrow$ `-cursor` $\rightarrow$ `-shell` $\rightarrow$ `-icons` $\rightarrow$ `-fonts`.
3. **The "Skip" Mechanism**: If a user hits `Enter` or selects a specialized "Skip/None" element without actively selecting an item in a category, it must mimic the logic of `main.py` (`return 0` cost), outputting a localized skip notice and gracefully progressing to the next stage.
4. **Real-Time Accumulator**: The application must actively aggregate the total payload size across choices.
5. **Multi-Step Undo Stack**: If the structural payload exceeds the input storage capacity threshold, the system halts final execution and presents an interactive undo panel. Unlike the original script's single-pass check, this interface must allow the user to systematically pop items from the selection history slice step-by-step until the aggregate size satisfies the physical storage limit constraints.

---

## 3. Screen Layout & Application Flow

```
+-----------------------------------------------------------------------+
|  [tuikkusu]  |  Language Selection / Kustomisasi Storage              |
+-----------------------------------------------------------------------+
|                                                                       |
|   Phase 0: Language Gate     --->     Phase 1: Max Capacity Gate     |
|   [ ] English (Default)               Enter Storage Limit: [_______]  |
|   [ ] Indonesia                                                       |
|                                                                       |
+-----------------------------------------------------------------------+

```

```
+-----------------------------------------------------------------------+
| TUIKKUSU // SYSTEM TWEAKS ENGINE v1.0.0                               |
+-----------------------------------------------------------------------+
| CATEGORIES          | SELECTION MATRIX                                |
| [*] -theme          | > [X] navy        [ ] purple      [ ] green     |
| [ ] -cursor         |   [ ] red         [ ] yellow                    |
| [ ] -shell          +-------------------------------------------------+
| [ ] -icons          | REAL-TIME METRICS                               |
| [ ] -fonts          | Allocated: [██████████░░░░░░] 74.2%             |
|                     | Storage Left: 120.5 MB / 500.0 MB               |
+-----------------------------------------------------------------------+
| STATUS: Hovering over 'navy' (Deep Ocean Aesthetic)                   |
+-----------------------------------------------------------------------+

```

### Phase 0: The Language Gate

Before accessing configuration layers, the TUI must display a clean initialization interface offering a language selection toggle:

* **English (Default)**
* **Indonesia**

Selecting a language dynamically swaps the global localization map string references across the entire application ecosystem (e.g., matching the contextual warnings, sizes, menu options, and interactive alerts).

### Phase 1: Storage Limit Initialization

An input field wrapped in a high-contrast box prompting the user for their total storage capacity (`float64`). The application blocks transition to Phase 2 until a valid positive numeric float is confirmed.

### Phase 2: Main Gamified Customization Workspace

The layout splits into a robust grid utilizing `lipgloss` panels:

* **Header Panel**: Displays a large ASCII banner reading `tuikkusu` with soft terminal color shifts.
* **Sidebar Panel**: Lists all 5 categories. Displays custom state markers indicating completed, active, or upcoming phases.
* **Main Selection Grid**: A dynamic tile-based menu mapping the available options for the active category. Users navigate using keyboard arrow keys or `H/J/K/L` inputs.
* **Real-Time Analytics Footer**: Houses an interactive status indicator showing itemized costs and an animated ASCII progress bar illustrating memory/storage consumption relative to the configured capacity.

---

## 4. Visual Themes & Animation Specification Matrix

Every selection element must feel unique, radiating distinct visual feedback upon selection or hover states through the use of specific ANSI colors, blinking text effects, and text animations.

| Category | Key Identifier | Hex Theme / Palette | Gamified Motion Effect & Visual Flavor |
| --- | --- | --- | --- |
| **-theme** | `navy` | `#000080` to `#1E3A8A` | Deep ocean blue gradient backdrop. Slowly pulses text intensity when highlighted. |
|  | `purple` | `#8B5CF6` to `#D946EF` | Cyberpunk neon magenta/purple accents. Features a subtle rapid-glitch text frame blink. |
|  | `green` | `#10B981` to `#059669` | High-contrast Matrix green terminal text. Displays a cascading character effect when chosen. |
|  | `red` | `#EF4444` to `#991B1B` | Vampiric crimson accents. Triggers a rhythmic dual-pulse flash on selection. |
|  | `yellow` | `#F59E0B` to `#D97706` | Industrial alert/cyber-bee amber frame. Fast warning blink style. |
| **-cursor** | `skyrim` | `#D1D5DB` to `#B45309` | Nordic iron gray paired with dragonborn gold accents. Shimmers text on highlight. |
|  | `hatsuneMiku` | `#00FFCC` to `#FF66CC` | Vibrant Vocaloid teal body with sharp pink trim. Bounces a miniature text equalizer layout. |
|  | `frierenBLZ` | `#E0F2FE` to `#A5B4FC` | Celestial white and elven mana-blue. Emits a soft fading trailing particle sequence. |
|  | `fluttershy` | `#FDE68A` to `#F472B6` | Pastel soft yellow and butterfly pink borders. Soft ease-in/ease-out text breathing movement. |
|  | `janeDoe` | `#111827` to `#F97316` | Underground urban tactical orange on charcoal gray. Mimics a spray-painted text rendering style. |
| **-shell** | `TST` | `#4B5563` to `#374151` | Tactical military specops dark slate grid. Renders an active looping sonar scanning bar. |
|  | `obsidian` | `#1F2937` to `#111827` | High-gloss reflective glassmorphic dark sheen. Flashes a sharp light streak across the border. |
|  | `darkSolid` | `#000000` to `#FFFFFF` | Brutalist high-contrast monochrome design. Completely inverts foreground/background block styling. |
|  | `whiteSkin` | `#F9FAFB` to `#E5E7EB` | Ultra-clean minimalist linen cream setup. Soft glow expansion frame layout. |
|  | `retroSH` | `#00FF00` to `#1F2937` | Amber/Green phosphorus CRT monitor style. Steady scrolling scanline text overlay. |
| **-icons** | `adwaita` | `#3B82F6` to `#64748B` | Flat enterprise workstation slate blue. Smooth sliding panel shift upon selection. |
|  | `MacTahoe` | `#0EA5E9` to `#E2E8F0` | Retro Aqua aluminum gradient curves. Quick elastic bouncy icon scale up. |
|  | `whitesur` | `#FFFFFF` to `#38BDF8` | Curved modern desktop scheme. Simulates a fluid magnifying dock layout expansion. |
|  | `overDose` | `#F43F5E` to `#06B6D4` | Intense high-intensity acid pink and toxic cyan clash. Shakes the viewport box on selection. |
|  | `Papirus` | `#F59E0B` to `#10B981` | Clean vector layout with distinct geometric shading. Mimics an origami paper fold unfold pattern. |
| **-fonts** | `inter` | `#F3F4F6` | Modern technical crisp slate. Smooth horizontal text stretching transition. |
|  | `JetbrainsMono` | `#00E5FF` | Developer cyan IDE framework accent. Alternates terminal syntax highlighting code flashes. |
|  | `poppins` | `#EC4899` | Round geometric energetic hot pink. Elastic bounce expand text effect. |
|  | `SF Pro` | `#9CA3AF` | Premium clean uniform gray scale formatting. Gentle ease-in-out breathing text lighting. |
|  | `TimesNewRoman` | `#78350F` | Deep academic classical typewriter mahogany tint. Stepped character typing animation sequence. |

---

## 5. Multi-Step Undo & Boundary Mechanics

```
+-----------------------------------------------------------------------+
|  [WARNING: OUT OF STORAGE CAPACITY!]                                  |
+-----------------------------------------------------------------------+
| Your selections require 45.2 MB above your current physical limit.    |
|                                                                       |
| HISTORY STACK (Press [Backspace] to Pop / Undo last action):          |
|  -> [5] -fonts (inter)       : 0.5 mb                                 |
|     [4] -icons (overDose)    : 1.4 mb                                 |
|     [3] -shell (TST)         : 2.7 mb                                 |
|                                                                       |
| Current Deficit: +45.2 MB                                             |
+-----------------------------------------------------------------------+
| [Backspace] Undo Last  |  [Esc] Reset All Choices                     |
+-----------------------------------------------------------------------+

```

When the calculated aggregate size profile exceeds the available capacity threshold at the final evaluation cycle, the system transitions into an explicit **Interactive Rollback State**:

1. **System Lockdown**: Standard progression menus lock down and transition into a high-visibility hazard warning panel.
2. **Visual Deficit Trackers**: Display a real-time tracking element showing exactly how much space needs to be reclaimed before validation succeeds ($SizeFile - Storage$).
3. **The Interactive Rollback Stack**: Render a clean history breakdown tracking chosen components in exact reverse order (LIFO - Last In, First Out).
4. **Live Updates**: Hitting `Backspace` instantly pops the top item off the stack, adjusts the storage deficit tally, updates the underlying state machine, and flashes the window border crimson to provide direct visual feedback.
5. **Resolution Liftoff**: The application blocks access to the success screen until the required threshold balance is restored. Once cleared, the layout transitions to a success panel confirming clean storage alignment.

---

## 6. Multi-Language Dictionary Localization

Implement this dictionary map structure explicitly to support instant runtime language updates.

```go
type LocalizationDict struct {
    AppTitle         string
    SelectLang       string
    StoragePrompt    string
    SelectedHeader   string
    TotalSizeText    string
    StorageExceeded  string
    UndoPrompt       string
    StorageSufficient string
    RemainingStorage string
    SkipNotice       string
    ItemCountText    string
}

var Localizations = map[string]LocalizationDict{
    "en": {
        AppTitle:         "TUIKKUSU // SYSTEM TWEAKS ENGINE v1.0.0",
        SelectLang:       "Select Language / Pilih Bahasa:",
        StoragePrompt:    "Enter your system storage size capacity limit (in Megabytes):",
        SelectedHeader:   "You have selected the following configurations:",
        TotalSizeText:    "Total aggregate deployment file size:",
        StorageExceeded:  "CRITICAL ERROR: Selected file payload exceeds available storage space!",
        UndoPrompt:       "Would you like to undo your last choice stack entry? (y/n):",
        StorageSufficient:"STORAGE CLEARANCE VERIFIED: Target space parameters are within safe thresholds.",
        RemainingStorage: "Available allocation space overhead remaining:",
        SkipNotice:       "SKIPPED: No allocation selected for this category. Advancing forward.",
        ItemCountText:    "Total individual objects queued for deployment:",
    },
    "id": {
        AppTitle:         "TUIKKUSU // ENGINE KUSTOMISASI SISTEM v1.0.0",
        SelectLang:       "Pilih Bahasa / Select Language:",
        StoragePrompt:    "Masukkan kapasitas batas ukuran storage perangkat anda (dalam Megabytes):",
        SelectedHeader:   "Anda telah berhasil memilih konfigurasi berikut:",
        TotalSizeText:    "Total keseluruhan ukuran size file item:",
        StorageExceeded:  "PERINGATAN KRITIKAL: Total ukuran file melebihi batas kapasitas storage!",
        UndoPrompt:       "Apakah anda ingin membatalkan entri pilihan terakhir pada sistem? (y/n):",
        StorageSufficient:"VERIFIKASI SUKSES: Kapasitas ruang penyimpanan mencukupi untuk deployment.",
        RemainingStorage: "Sisa ruang kapasitas penyimpanan yang tersedia:",
        SkipNotice:       "DILEWATKAN: Tidak ada pilihan untuk kategori ini. Melanjutkan ke menu berikutnya.",
        ItemCountText:    "Total item yang berhasil dijadwalkan untuk dipasang:",
    },
}

```

---

## 7. Execution Instructions for the AI Engineering Agent

To successfully build this application, execute the following steps in sequence:

1. **Initialize Project Ecosystem**: Set up a clean Go module structure (`go mod init tuikkusu`). Install the `bubbletea`, `lipgloss`, and `bubbles` library components.
2. **Implement State Machine Foundation**: Write out the strict Elm Architecture scaffolding (`Model`, `Init`, `Update`, `View`).
3. **Build Phase 0 & Phase 1 Interfaces**: Write the localized language selection gate and numeric input handling validations. Ensure clear fallback checks prevent users from providing corrupted or non-numeric inputs.
4. **Develop Phase 2 Grid & Controls**: Wire up keybind handling routines (`Up/Down/Left/Right`, `H/J/K/L`, `Space/Enter` for execution selection, `Esc` for factory resets). Embed style variations and custom animations for each row element using pure `lipgloss` properties.
5. **Build Real-Time Calculations & Progress Gauges**: Integrate automated float computation trackers alongside an updating progress bar rendering implementation.
6. **Program Boundary Checks & Undo Routines**: Code the LIFO stack data processing loops to cleanly handle storage allocation warnings and step-by-step item popping.
7. **Polishing Phase**: Verify the interface handles window layout adjustments gracefully, clear out arbitrary visual artifacts, ensure full color fidelity inside standard terminal environments, and run test cycles confirming zero memory leaks during animation loops.
