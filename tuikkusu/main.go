package main

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/charmbracelet/bubbles/progress"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type Phase int

const (
	PhaseLanguage Phase = iota
	PhaseStorageLimit
	PhaseCustomization
	PhaseUndo
	PhaseSuccess
)

type LocalizationDict struct {
	AppTitle          string
	SelectLang        string
	StoragePrompt     string
	SelectedHeader    string
	TotalSizeText     string
	StorageExceeded   string
	UndoPrompt        string
	StorageSufficient string
	RemainingStorage  string
	SkipNotice        string
	ItemCountText     string
}

var Localizations = map[string]LocalizationDict{
	"en": {
		AppTitle:          "Tuikkusu v1.0.0",
		SelectLang:        "Select Language / Pilih Bahasa:",
		StoragePrompt:     "Enter your system storage size capacity limit (in Megabytes):",
		SelectedHeader:    "You have selected the following configurations:",
		TotalSizeText:     "Total aggregate deployment file size:",
		StorageExceeded:   "CRITICAL ERROR: Selected file payload exceeds available storage space!",
		UndoPrompt:        "Would you like to undo your last choice stack entry? (y/n):",
		StorageSufficient: "STORAGE CLEARANCE VERIFIED: Target space parameters are within safe thresholds.",
		RemainingStorage:  "Available allocation space overhead remaining:",
		SkipNotice:        "SKIPPED: No allocation selected for this category. Advancing forward.",
		ItemCountText:     "Total individual objects queued for deployment:",
	},
	"id": {
		AppTitle:          "TUIKKUSU // ENGINE KUSTOMISASI SISTEM v1.0.0",
		SelectLang:        "Pilih Bahasa / Select Language:",
		StoragePrompt:     "Masukkan kapasitas batas ukuran storage perangkat anda (dalam Megabytes):",
		SelectedHeader:    "Anda telah berhasil memilih konfigurasi berikut:",
		TotalSizeText:     "Total keseluruhan ukuran size file item:",
		StorageExceeded:   "PERINGATAN KRITIKAL: Total ukuran file melebihi batas kapasitas storage!",
		UndoPrompt:        "Apakah anda ingin membatalkan entri pilihan terakhir pada sistem? (y/n):",
		StorageSufficient: "VERIFIKASI SUKSES: Kapasitas ruang penyimpanan mencukupi untuk deployment.",
		RemainingStorage:  "Sisa ruang kapasitas penyimpanan yang tersedia:",
		SkipNotice:        "DILEWATKAN: Tidak ada pilihan untuk kategori ini. Melanjutkan ke menu berikutnya.",
		ItemCountText:     "Total item yang berhasil dijadwalkan untuk dipasang:",
	},
}

type TweakOption struct {
	Name        string
	SizeMB      float64
	Description string
	ColorStart  string
	ColorEnd    string
}

type Category struct {
	Key     string
	Options []TweakOption
}

var categories = []Category{
	{
		Key: "-theme",
		Options: []TweakOption{
			{"navy", 9.4, "Deep Ocean Aesthetic", "#000080", "#1E3A8A"},
			{"purple", 7.1, "Cyberpunk neon magenta/purple accents", "#8B5CF6", "#D946EF"},
			{"green", 2.5, "High-contrast Matrix green terminal text", "#10B981", "#059669"},
			{"red", 3.0, "Vampiric crimson accents", "#EF4444", "#991B1B"},
			{"yellow", 2.7, "Industrial alert amber", "#F59E0B", "#D97706"},
		},
	},
	{
		Key: "-cursor",
		Options: []TweakOption{
			{"skyrim", 11.2, "Nordic iron gray paired with dragonborn gold", "#D1D5DB", "#B45309"},
			{"hatsuneMiku", 13.5, "Vibrant Vocaloid teal body with sharp pink trim", "#00FFCC", "#FF66CC"},
			{"frierenBLZ", 7.8, "Celestial white and elven mana-blue", "#E0F2FE", "#A5B4FC"},
			{"fluttershy", 9.3, "Pastel soft yellow and butterfly pink borders", "#FDE68A", "#F472B6"},
			{"janeDoe", 15.9, "Underground urban tactical orange", "#111827", "#F97316"},
		},
	},
	{
		Key: "-shell",
		Options: []TweakOption{
			{"TST", 2.7, "Tactical military specops dark slate grid", "#4B5563", "#374151"},
			{"obsidian", 2.5, "High-gloss reflective glassmorphic dark sheen", "#1F2937", "#111827"},
			{"darkSolid", 1.9, "Brutalist high-contrast monochrome design", "#000000", "#FFFFFF"},
			{"whiteSkin", 2.2, "Ultra-clean minimalist linen cream setup", "#F9FAFB", "#E5E7EB"},
			{"retroSH", 1.2, "Amber/Green phosphorus CRT monitor style", "#00FF00", "#1F2937"},
		},
	},
	{
		Key: "-icons",
		Options: []TweakOption{
			{"adwaita", 1.9, "Flat enterprise workstation slate blue", "#3B82F6", "#64748B"},
			{"MacTahoe", 1.3, "Retro Aqua aluminum gradient curves", "#0EA5E9", "#E2E8F0"},
			{"whitesur", 1.6, "Curved modern desktop scheme", "#FFFFFF", "#38BDF8"},
			{"overDose", 1.4, "Intense high-intensity acid pink", "#F43F5E", "#06B6D4"},
			{"Papirus", 1.2, "Clean vector layout with geometric shading", "#F59E0B", "#10B981"},
		},
	},
	{
		Key: "-fonts",
		Options: []TweakOption{
			{"inter", 0.5, "Modern technical crisp slate", "#F3F4F6", "#F3F4F6"},
			{"JetbrainsMono", 0.6, "Developer cyan IDE framework accent", "#00E5FF", "#00E5FF"},
			{"poppins", 0.8, "Round geometric energetic hot pink", "#EC4899", "#EC4899"},
			{"SF Pro", 0.4, "Premium clean uniform gray scale formatting", "#9CA3AF", "#9CA3AF"},
			{"TimesNewRoman", 0.2, "Deep academic classical typewriter mahogany", "#78350F", "#78350F"},
		},
	},
}

type Selection struct {
	Category string
	Option   TweakOption
}

type model struct {
	phase           Phase
	lang            string
	storageLimit    float64
	textInput       textinput.Model
	progress        progress.Model
	langCursor      int
	catIndex        int
	optCursor       int
	selections      []Selection
	width           int
	height          int
	err             string
	blink           bool
	skipMessage     string
	skipMessageTime time.Time
	undoFlash       bool
	undoFlashTime   time.Time
}

type tickMsg time.Time

func tick() tea.Cmd {
	return tea.Tick(time.Millisecond*500, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "500.0"
	ti.Focus()
	ti.CharLimit = 10
	ti.Width = 20

	return model{
		phase:      PhaseLanguage,
		lang:       "en",
		langCursor: 0,
		textInput:  ti,
		progress:   progress.New(progress.WithDefaultGradient()),
		selections: []Selection{},
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(textinput.Blink, tick())
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil
	case tickMsg:
		m.blink = !m.blink
		if m.skipMessage != "" && time.Since(m.skipMessageTime) > 3*time.Second {
			m.skipMessage = ""
		}
		if m.undoFlash && time.Since(m.undoFlashTime) > 200*time.Millisecond {
			m.undoFlash = false
		}
		return m, tick()
	}

	switch m.phase {
	case PhaseLanguage:
		return m.updateLanguage(msg)
	case PhaseStorageLimit:
		return m.updateStorageLimit(msg)
	case PhaseCustomization:
		return m.updateCustomization(msg)
	case PhaseUndo:
		return m.updateUndo(msg)
	case PhaseSuccess:
		return m.updateSuccess(msg)
	}

	return m, nil
}

func (m model) updateLanguage(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k":
			if m.langCursor > 0 {
				m.langCursor--
			}
		case "down", "j":
			if m.langCursor < 1 {
				m.langCursor++
			}
		case "enter", " ":
			if m.langCursor == 0 {
				m.lang = "en"
			} else {
				m.lang = "id"
			}
			m.phase = PhaseStorageLimit
		}
	}
	return m, nil
}

func (m model) updateStorageLimit(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "enter":
			val, err := strconv.ParseFloat(m.textInput.Value(), 64)
			if err == nil && val > 0 {
				m.storageLimit = val
				m.phase = PhaseCustomization
				m.err = ""
			} else {
				m.err = "Please enter a valid positive number"
			}
		}
	}
	m.textInput, cmd = m.textInput.Update(msg)
	return m, cmd
}

func (m model) updateCustomization(msg tea.Msg) (tea.Model, tea.Cmd) {
	opts := categories[m.catIndex].Options
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k", "left", "h":
			if m.optCursor > 0 {
				m.optCursor--
			}
		case "down", "j", "right", "l":
			if m.optCursor < len(opts)-1 {
				m.optCursor++
			}
		case "enter":
			// User pressed enter on an option
			m.selections = append(m.selections, Selection{
				Category: categories[m.catIndex].Key,
				Option:   opts[m.optCursor],
			})
			m.advanceCategory()
		case "esc", "s":
			// Skip mechanism
			m.skipMessage = Localizations[m.lang].SkipNotice
			m.skipMessageTime = time.Now()
			m.advanceCategory()
		}
	}
	return m, nil
}

func (m *model) advanceCategory() {
	m.catIndex++
	m.optCursor = 0
	if m.catIndex >= len(categories) {
		m.checkStorageAndTransition()
	}
}

func (m *model) checkStorageAndTransition() {
	var total float64
	for _, s := range m.selections {
		total += s.Option.SizeMB
	}
	if total > m.storageLimit {
		m.phase = PhaseUndo
	} else {
		m.phase = PhaseSuccess
	}
}

func (m model) updateUndo(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "backspace", "delete":
			if len(m.selections) > 0 {
				m.selections = m.selections[:len(m.selections)-1]
				m.undoFlash = true
				m.undoFlashTime = time.Now()
			}
			var total float64
			for _, s := range m.selections {
				total += s.Option.SizeMB
			}
			if total <= m.storageLimit {
				m.phase = PhaseSuccess
			}
		case "esc":
			m.selections = []Selection{}
			m.catIndex = 0
			m.phase = PhaseCustomization
		}
	}
	return m, nil
}

func (m model) updateSuccess(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "esc", "enter":
			return m, tea.Quit
		}
	}
	return m, nil
}

// ---------------------------------------------------------
// View Methods
// ---------------------------------------------------------

var (
	titleStyle = lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#00E5FF")).
		Padding(0, 1).
		BorderStyle(lipgloss.DoubleBorder()).
		BorderForeground(lipgloss.Color("#EC4899"))

	boxStyle = lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		Padding(1, 2)

	activeItemStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#000000")).
		Background(lipgloss.Color("#00FFCC")).
		Bold(true)

	inactiveItemStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FFFFFF"))

	errorStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#EF4444")).
		Bold(true)
)

func (m model) View() string {
	if m.width == 0 {
		return "Initializing..."
	}

	var content string
	switch m.phase {
	case PhaseLanguage:
		content = m.viewLanguage()
	case PhaseStorageLimit:
		content = m.viewStorageLimit()
	case PhaseCustomization:
		content = m.viewCustomization()
	case PhaseUndo:
		content = m.viewUndo()
	case PhaseSuccess:
		content = m.viewSuccess()
	}

	return lipgloss.Place(m.width, m.height, lipgloss.Center, lipgloss.Center, content)
}

func (m model) viewLanguage() string {
	header := titleStyle.Render("[tuikkusu] | Language Selection / Kustomisasi Storage")
	
	choices := ""
	enPrefix := "[ ] "
	idPrefix := "[ ] "
	if m.langCursor == 0 {
		enPrefix = "[X] "
	} else {
		idPrefix = "[X] "
	}

	choices += lipgloss.NewStyle().Foreground(func() lipgloss.Color {
		if m.langCursor == 0 { return lipgloss.Color("#00FFCC") }
		return lipgloss.Color("#FFFFFF")
	}()).Render(fmt.Sprintf("%sEnglish (Default)\n", enPrefix))
	
	choices += lipgloss.NewStyle().Foreground(func() lipgloss.Color {
		if m.langCursor == 1 { return lipgloss.Color("#00FFCC") }
		return lipgloss.Color("#FFFFFF")
	}()).Render(fmt.Sprintf("%sIndonesia", idPrefix))

	box := boxStyle.Render(fmt.Sprintf("Phase 0: Language Gate\n\n%s", choices))
	
	return lipgloss.JoinVertical(lipgloss.Center, header, box)
}

func (m model) viewStorageLimit() string {
	loc := Localizations[m.lang]
	header := titleStyle.Render(loc.AppTitle)
	
	prompt := loc.StoragePrompt
	input := m.textInput.View()
	
	errStr := ""
	if m.err != "" {
		errStr = errorStyle.Render("\n" + m.err)
	}

	box := boxStyle.Render(fmt.Sprintf("Phase 1: Max Capacity Gate\n\n%s\n%s%s", prompt, input, errStr))
	
	return lipgloss.JoinVertical(lipgloss.Center, header, box)
}

func (m model) getBanner() string {
	// A simple stylized ASCII banner for tuikkusu
	banner := `
  _         _ _    _                    
 | |_ _   _(_) | _| | ___   _ ___ _   _ 
 | __| | | | | |/ / |/ / | | / __| | | |
 | |_| |_| | |   <|   <| |_| \__ \ |_| |
  \__|\__,_|_|_|\_\_|\_\\__,_|___/\__,_|
`
	// soft color shift based on blink state
	color := "#00E5FF"
	if m.blink {
		color = "#EC4899"
	}
	return lipgloss.NewStyle().Foreground(lipgloss.Color(color)).Bold(true).Render(banner)
}

func (m model) viewCustomization() string {
	loc := Localizations[m.lang]
	
	headerText := titleStyle.Render(loc.AppTitle)
	bannerView := m.getBanner()
	header := lipgloss.JoinVertical(lipgloss.Center, bannerView, headerText)

	// Sidebar
	sidebar := "CATEGORIES\n"
	for i, cat := range categories {
		prefix := "[ ]"
		if i == m.catIndex {
			prefix = "[*]"
		} else if i < m.catIndex {
			prefix = "[v]" // completed
		}
		sidebar += fmt.Sprintf("%s %s\n", prefix, cat.Key)
	}
	sidebarView := lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(0, 1).Width(20).Render(sidebar)

	// Selection Matrix
	opts := categories[m.catIndex].Options
	matrix := "SELECTION MATRIX\n"
	
	for i, opt := range opts {
		prefix := "[ ] "
		if i == m.optCursor {
			prefix = "> [X] "
		}
		
		// Render dynamic styles
		style := lipgloss.NewStyle()
		if i == m.optCursor {
			if m.blink {
				style = style.Foreground(lipgloss.Color(opt.ColorStart)).Bold(true)
			} else {
				style = style.Foreground(lipgloss.Color(opt.ColorEnd)).Bold(true)
			}
		} else {
			style = style.Foreground(lipgloss.Color("#888888"))
		}
		
		matrix += style.Render(fmt.Sprintf("%s%-12s (%.1f MB)\n", prefix, opt.Name, opt.SizeMB))
	}
	matrixView := lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(0, 1).Width(45).Render(matrix)

	topRow := lipgloss.JoinHorizontal(lipgloss.Top, sidebarView, matrixView)

	// Real-Time Analytics
	var total float64
	for _, s := range m.selections {
		total += s.Option.SizeMB
	}
	percent := total / m.storageLimit
	if percent > 1.0 { percent = 1.0 }
	
	prog := m.progress.ViewAs(percent)
	analytics := fmt.Sprintf("REAL-TIME METRICS\nAllocated: %s %.1f%%\nStorage Left: %.1f MB / %.1f MB", 
		prog, percent*100, m.storageLimit-total, m.storageLimit)
	analyticsView := lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(0, 1).Width(67).Render(analytics)

	// Status line
	status := fmt.Sprintf("STATUS: Hovering over '%s' (%s)", opts[m.optCursor].Name, opts[m.optCursor].Description)
	if m.skipMessage != "" {
		status += " | " + m.skipMessage
	}
	statusView := lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(0, 1).Width(67).Render(status)

	// Combine
	body := lipgloss.JoinVertical(lipgloss.Left, topRow, analyticsView, statusView)
	return lipgloss.JoinVertical(lipgloss.Center, header, body)
}

func (m model) viewUndo() string {
	var total float64
	for _, s := range m.selections {
		total += s.Option.SizeMB
	}
	deficit := total - m.storageLimit

	warningHeader := lipgloss.NewStyle().
		Bold(true).Background(lipgloss.Color("#EF4444")).Foreground(lipgloss.Color("#FFFFFF")).
		Padding(0, 1).Render("[WARNING: OUT OF STORAGE CAPACITY!]")
	
	text1 := fmt.Sprintf("Your selections require %.1f MB above your current physical limit.", deficit)
	
	history := "HISTORY STACK (Press [Backspace] to Pop / Undo last action):\n"
	for i := len(m.selections) - 1; i >= 0; i-- {
		s := m.selections[i]
		history += fmt.Sprintf("  [%d] %s (%s) : %.1f MB\n", i+1, s.Category, s.Option.Name, s.Option.SizeMB)
	}

	text2 := fmt.Sprintf("\nCurrent Deficit: +%.1f MB", deficit)
	
	borderColor := lipgloss.Color("#EF4444")
	if m.undoFlash {
		borderColor = lipgloss.Color("#DC143C") // Crimson flash
	}

	box := lipgloss.NewStyle().Border(lipgloss.ThickBorder(), true).BorderForeground(borderColor).Padding(1, 2).Render(
		lipgloss.JoinVertical(lipgloss.Left, warningHeader, "", text1, "", history, text2),
	)

	footer := "[Backspace] Undo Last  |  [Esc] Reset All Choices"
	
	return lipgloss.JoinVertical(lipgloss.Center, box, footer)
}

func (m model) viewSuccess() string {
	loc := Localizations[m.lang]
	
	var total float64
	for _, s := range m.selections {
		total += s.Option.SizeMB
	}

	header := titleStyle.Render(loc.AppTitle)
	
	successMsg := lipgloss.NewStyle().Foreground(lipgloss.Color("#10B981")).Bold(true).Render(loc.StorageSufficient)
	
	info := fmt.Sprintf("%s\n%.1f MB\n\n%s %d\n\n%s %.1f MB", 
		loc.TotalSizeText, total, 
		loc.ItemCountText, len(m.selections),
		loc.RemainingStorage, m.storageLimit-total)

	box := boxStyle.Render(lipgloss.JoinVertical(lipgloss.Left, successMsg, "", info))
	
	footer := "[Press Enter to Exit]"
	
	return lipgloss.JoinVertical(lipgloss.Center, header, box, footer)
}

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}
}
