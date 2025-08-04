# GitOrder AI Agent - Kompleksowy System Zarządzania Projektami

## 🎯 Opis Projektu

**GitOrder AI Agent** to zaawansowany system zarządzania projektami stworzony specjalnie dla deweloperów z ADHD, którzy dążą do zostania "top vibecoder'ami". System automatyzuje uporządkowanie repozytoriów GitHub i lokalnych folderów projektów zgodnie z najlepszymi praktykami IT, takimi jak standardowa struktura repo (np. src, tests, docs), README.md z setupem i usage, CONTRIBUTING.md, licencje oraz CI/CD pipelines. 

Projekt uwzględnia Twoje aktualne skille (Claude Code, Gemini CLI, Codex, Cursor, Hugging Face, Agent Zero) i skupia się na szybkiej monetyzacji poprzez łączenie ich w proste, skalowalne narzędzia (np. AI prompt optimizer deployowany na HF jako SaaS lub freelance tools do automatyzacji bidding na Upwork). Całość jest modularna i łatwa do rozbudowy (np. dodawanie pluginów do Agent Zero). Cel: Utrzymanie porządku, jasności prac i organizacji dla osób z ADHD, z AI-driven wsparciem progresu.

**Główne Cele:**
- Automatyczne uporządkowanie repozytoriów GitHub i lokalnych folderów.
- Kompleksowa analiza kodu i dokumentacji projektów, uzupełnienie brakujących elementów.
- Generowanie pełnej dokumentacji dla agentów AI (np. prompty i kontekst do kontynuacji prac).
- Tworzenie list zadań do wersji MVP (minimal viable product, np. core features z lokalnym deployem) i full (pełna skalowalność, monetyzacja).
- Synchronizacja projektów z GitHub, identyfikacja duplikatów i usuwanie niepotrzebnych plików.
- Stworzenie agenta z MCP integration (jeśli consent) i web dashboardem do monitoringu.
- AI do dbania o progress: sugestie zadań, priorytety, analiza mocnych/słabych stron, pola poprawy.
- Dodatkowe funkcje: Newsy z branży AI (np. via RSS/HF APIs), propozycje monetyzacji (np. "Przekształć w Gumroad product"), wyszukiwarka projektów freelancingu (scrape Upwork, filtr po skillach jak "łatwe AI/Python tasks").
- Rozwiązanie problemów deploymentu: Dynamiczne zarządzanie portami Docker (auto-remap), handling zmiennego IP via DuckDNS/No-IP z cron jobami, auto-deploy na Hostinger VPS z n8n dla stabilności zewnętrznego dostępu.
- Integracja z Agent Zero jako rozszerzenie (np. moduł do repo management i deployment watchdog).

System wspiera vibecoding: Lekki, profesjonalny proces z AI jako co-pilotem, z ciągłym logowaniem promptów/kroków dla analizy improvement (ADHD-friendly: małe kroki, auto-reminders, visual progress).

## 🏗️ Architektura Systemu

### Backend (Python + Agent Zero Extension)
```
GitOrder/
├── core/
│   ├── project_scanner.py      # Skanowanie repo i folderów, identyfikacja duplikatów/junk
│   ├── code_analyzer.py        # Analiza kodu via AI (Hugging Face/Gemini CLI), raporty mocnych/słabych stron
│   ├── doc_generator.py        # Auto-generowanie README, docs dla agentów, listy zadań MVP/full
│   ├── github_sync.py          # Synchronizacja z GitHub, resolvowanie konfliktów
│   └── duplicate_finder.py     # Wykrywanie duplikatów i niepotrzebnych plików
├── ai_agents/
│   ├── progress_manager.py     # AI task generation, priorytety, pola poprawy
│   ├── monetization_advisor.py # Propozycje monetyzacji oparte na skillach (np. szybki SaaS z Twoimi toolami)
│   ├── skill_analyzer.py       # Analiza Twoich skilli i łączenie dla monetyzacji
│   └── freelance_finder.py     # Wyszukiwarka projektów freelancingu (scrape + filter)
├── deployment/
│   ├── port_manager.py         # Dynamiczne zarządzanie portami Docker (auto-detect/remap, chaos resolution)
│   ├── dns_updater.py          # Handling zmiennego IP via DuckDNS, auto-update dla zewnętrznego dostępu
│   └── vps_deployer.py         # Auto-deploy na Hostinger VPS z n8n
├── web/
│   ├── api/                    # Flask REST API dla dashboardu
│   └── dashboard/              # React frontend
└── utils/
    ├── adhd_helpers.py         # ADHD-friendly features (reminders, visual progress, log promptów/kroków)
    ├── prompt_logger.py        # Ciągły zapis promptów i kroków dla raportu improvement
    └── improvement_tracker.py  # Analiza logów pod kątem vibecoding skills (np. "Częściej używaj tests")
```

### Frontend (React Dashboard)
```
dashboard/
├── components/
│   ├── ProjectList.jsx         # Lista projektów z statusem, ostatnimi zmianami (git logs)
│   ├── StatusDashboard.jsx     # Overview statusów, progress %
│   ├── AIProgressPanel.jsx     # Sugestie zadań, priorytety, newsy AI
│   ├── MonetizationPanel.jsx   # Propozycje zarobku, analiza mocnych/słabych stron
│   └── DeploymentMonitor.jsx   # Status deploymentów, alerty konfliktów
├── pages/
│   ├── Overview.jsx            # Główny dashboard
│   ├── ProjectDetails.jsx      # Szczegóły projektu (docs, listy zadań MVP/full)
│   ├── Analytics.jsx           # Raporty (pola poprawy, skill analysis, freelance matches)
│   └── Settings.jsx            # Konfiguracja (np. API keys, MCP consent)
└── services/
    ├── api.js                  # Komunikacja z backend API
    ├── websocket.js            # Real-time updates (np. nowe newsy AI)
    └── notifications.js        # ADHD-friendly powiadomienia (soft, non-overwhelming)
```

## 🚀 Kluczowe Funkcjonalności

### 1. Analiza i Uporządkowanie Projektów
- **Automatyczne skanowanie** repozytoriów GitHub i lokalnych folderów via Gemini CLI.
- **Wykrywanie duplikatów** i niepotrzebnych plików (np. stare backups, temp files).
- **Analiza struktury projektu** zgodnie z best practices IT (np. check for missing .gitignore).
- **Generowanie raportów** o stanie projektów, uwzględniających Twoje skille (np. "Połącz Cursor z HF dla szybszej monetyzacji").

### 2. AI-Powered Documentation
- **Auto-generowanie README.md** z pełną dokumentacją (setup, architecture, usage).
- **Tworzenie specyfikacji dla agentów AI** (prompty, kontekst do kontynuacji via Agent Zero).
- **Listy zadań MVP i Full Version** z priorytetyzacją (np. MVP: Lokalny Docker deploy; Full: Monetyzacja via SaaS).
- **Code review** z sugestiami poprawek, analizą mocnych/słabych stron (np. "Mocna: Dobry użytek Codex; Słaba: Brak tests – popraw dla profesjonalizmu").

### 3. Dashboard i Monitoring
```javascript
// Przykład struktury danych dashboard'a
const projectStatus = {
  id: "project-1",
  name: "AI Chat Bot",
  status: "mvp-ready", // draft, mvp-ready, full-version, deployed
  progress: 75,
  lastUpdate: "2025-08-03T10:30:00Z",
  technologies: ["Python", "FastAPI", "OpenAI"],
  monetizationPotential: "high", // Based on skill analysis (e.g., easy freelance match)
  nextTasks: [
    "Add user authentication",
    "Implement rate limiting",
    "Deploy to production"
  ],
  aiRecommendations: [
    "Ready for MVP launch - consider Gumroad for monetization",
    "Add documentation for API endpoints",
    "Setup GitHub Actions for CI/CD"
  ],
  freelanceMatches: ["Upwork: Build similar bot - $500, matches your HF skills"]
};
```

### 4. Deployment Management
- **Port Conflict Resolution**: Automatyczne zarządzanie portami Docker (dynamic assignment z range 3000-9000, auto-shutdown idle containers).
- **Dynamic IP Handling**: Integracja z DuckDNS/No-IP; cron job co 5 min checkuje IP i update'uje; fallback: Ngrok tunnel dla stałego URL; auto-migracja na Hostinger VPS via n8n workflows.
- **VPS Auto-Deploy**: Skrypt do push deployów na VPS przy wykryciu chaosu lokalnego.
- **Container Monitoring**: Real-time status wszystkich aktywnych kontenerów w dashboardzie.

### 5. AI Progress Manager
- **Task Generation**: AI (Agent Zero + HF) generuje kolejne zadania na podstawie analizy projektu i Twoich skilli (np. "Użyj Gemini CLI do lokalnej analizy").
- **Priority Scoring**: Algorytm priorytetyzacji (np. wysoki priorytet na monetyzację: "Szybki win: Deploy na HF").
- **Skill-Based Recommendations**: Sugestie bazujące na skillach (np. "Połącz Codex z Cursor dla faster coding").
- **Monetization Advisor**: Propozycje dla każdego projektu (np. "Monetyzuj via freelance – oto 3 matching gigs").
- **Dodatkowe: Newsy AI** (daily feed z HF papers/Reddit); **Freelance Finder** (scrape + ROI calc); **Improvement Raport** (ciągły log promptów/kroków, analiza co tydzień: "ADHD tip: Więcej micro-tasks").

## 📋 Lista Zadań

### MVP Version (2-3 tygodnie)
1. **Core Scanner** - Skanowanie repo GitHub i lokalnych folderów.
2. **Basic Dashboard** - Lista projektów z podstawowymi informacjami.
3. **AI Task Generator** - Generowanie podstawowych zadań i priorytetów.
4. **Port Manager** - Rozwiązywanie konfliktów portów Docker.
5. **GitHub Integration** - Podstawowa synchronizacja i cleanup.

### Full Version (1-2 miesiące)
1. **Advanced AI Analysis** - Pełna analiza kodu, mocnych/słabych stron, propozycje monetyzacji.
2. **Monetization Engine** - Zaawansowane sugestie zarobku oparte na skillach.
3. **Freelance Finder** - Wyszukiwarka projektów dopasowanych do umiejętności.
4. **VPS Integration** - Automatyczny deployment na VPS z IP handling.
5. **Real-time Monitoring** - Live updates, newsy AI, notyfikacje.
6. **Analytics Dashboard** - Szczegółowe raporty (pola poprawy, skill improvement).
7. **Agent Zero Extension** - Pełna integracja z logowaniem promptów/kroków.

## 🛠️ Rozwiązanie Problemów Deployment

### Docker Port Management
```python
# port_manager.py (przykład z backendu)
class DockerPortManager:
    def __init__(self):
        self.used_ports = set()
        self.port_mapping = {}
    
    def assign_port(self, project_name, preferred_port=None):
        if preferred_port and preferred_port not in self.used_ports:
            port = preferred_port
        else:
            port = self.find_free_port()
        
        self.used_ports.add(port)
        self.port_mapping[project_name] = port
        return port
    
    def find_free_port(self):
        for port in range(3000, 9000):
            if port not in self.used_ports and self.is_port_available(port):
                return port
```

### Dynamic IP Solution
```python
# dns_updater.py (integracja z DuckDNS)
import asyncio

class DNSUpdater:
    def __init__(self, provider="duckdns"):
        self.provider = provider
        self.current_ip = None
    
    async def monitor_ip_changes(self):
        while True:
            new_ip = await self.get_public_ip()
            if new_ip != self.current_ip:
                await self.update_dns(new_ip)
                self.current_ip = new_ip
            await asyncio.sleep(300)  # Check every 5 minutes
```

Dla zewnętrznego dostępu: Użyj n8n na VPS do triggerowania update'ów; fallback Ngrok dla lokalnych deployów.

## 🤖 Perfect Prompt dla Claude Code

```
Stwórz modularną aplikację Python o nazwie "GitOrder AI Agent" jako rozszerzenie Agent Zero z następującymi specyfikacjami:

ARCHITEKTURA:
- Backend: Python 3.10+ z asyncio, FastAPI dla API
- Frontend: React 18 z TypeScript, Tailwind CSS
- Database: SQLite + Redis dla cache
- AI Integration: OpenAI API, Hugging Face Transformers, Gemini CLI
- Deployment: Docker Compose z nginx reverse proxy

GŁÓWNE MODUŁY:
1. ProjectScanner - skanowanie GitHub repos i lokalnych folderów (via Gemini CLI)
2. CodeAnalyzer - analiza kodu z AI, generowanie raportów (mocne/słabe, pola poprawy)
3. DocumentationGenerator - auto-tworzenie README, docs dla agentów, listy zadań MVP/full
4. GitHubSync - synchronizacja zmian, conflict resolution, cleanup duplikatów
5. DeploymentManager - zarządzanie Docker containers, port allocation, IP handling (DuckDNS)
6. AIProgressManager - task generation, priorytetyzacja, newsy AI
7. MonetizationAdvisor - analiza potencjału zarobkowego oparte na skillach (Claude/Codex/HF)

FUNKCJONALNOŚCI:
- Dashboard z real-time updates (WebSocket) - lista projektów, statusy, ostatnie zmiany
- AI task recommendations bazujące na skillach użytkownika (np. szybka monetyzacja)
- Automatyczne wykrywanie duplikatów projektów i junk files
- Port conflict resolution dla Docker, dynamic IP via DuckDNS
- Freelance finder (scrape Upwork), newsy AI (HF integration)
- Prompt logging i self-improvement analytics (ciągły raport kroków/promptów)
- ADHD-friendly UI (clear priorities, minimal cognitive load, auto-reminders)

WYMAGANIA TECHNICZNE:
- Clean Architecture (SOLID principles)
- Async/await wszędzie gdzie możliwe
- 90%+ test coverage (pytest + jest)
- Type hints w Python, TypeScript w frontend
- Docker multi-stage builds
- GitHub Actions CI/CD
- Monitoring z Prometheus/Grafana

ADHD CONSIDERATIONS:
- Visual progress indicators
- Auto-save wszystkich zmian
- Gentle notifications (nie overwhelming)
- Task breakdown na małe kroki
- Quick wins tracking
- Focus mode (hide distracting elements)
- Ciągły log promptów/kroków z analizą improvement (np. weekly review)

Wyprodukuj pełny kod z:
- requirements.txt i package.json
- Docker Compose setup
- Pełną dokumentację API
- README z quick start guide
- rules.md z coding standards (vibecoding rules)
- Example prompts dla różnych scenariuszy

Kod ma być production-ready, scalable i łatwy do maintenance. Uwzględnij integrację z Agent Zero, n8n na VPS i Twoje skille dla monetyzacji.
```

## 📜 Universal Rules.md

```markdown
# Universal Vibecoding Rules for AI-Assisted Development

## 🎯 Core Philosophy
**Vibecoding** = Kodowanie z flow, używając AI jako partnera, nie zamiennika myślenia. Cel: Spójność, lekkość i profesjonalizm – minimalizm, zero bloat, focus na monetyzację.

### Główne Zasady:
1. **AI as Co-pilot**: AI (Claude/Codex/Gemini) generuje, człowiek weryfikuje i refaktoruje.
2. **Minimalism First**: Tylko to co potrzebne; clean code, no over-engineering.
3. **Documentation Driven**: Kod dokumentuje się sam + AI-generated docs.
4. **Test First Mindset**: Każda funkcja = test + implementation (80%+ coverage).
5. **Continuous Refactoring**: Małe, częste poprawki dla skalowalności.

## 🔄 Coding Process

### 1. Planning Phase
```
1. Zdefiniuj problem w 1-2 zdaniach.
2. Rozłóż na micro-tasks (max 30 min każdy, ADHD-friendly).
3. Stwórz AI prompt dla każdego task'a.
4. Zaloguj plan w project tracker (z priorytetami na quick wins/monetyzację).
```

### 2. Implementation Phase
```
1. Wygeneruj kod via AI (Claude/Codex/Gemini).
2. Code review ręcznie: Czy zrozumiały? SOLID/DRY/KISS? Error handling?
3. Refactor dla czytelności i performance.
4. Napisz/wygeneruj testy.
5. Commit z opisowym message (np. "feat: add port manager [prompt: dynamic port assignment]").
```

### 3. Documentation Phase
```
1. Update README.md (auto via AI jeśli możliwe).
2. Dodaj docstring/JSDoc komentarze.
3. Update API documentation.
4. Zaloguj wykonane kroki i prompty w real-time raporcie.
```

## 🧠 ADHD-Friendly Rules

### Task Management:
- **One Thing Rule**: Jeden task na raz, finish before next.
- **25-Minute Sprints**: Pomodoro z AI assistance dla focus.
- **Visual Progress**: Zawsze widoczny progress bar/checklist.
- **Quick Wins**: Dziel duże zadania na małe, łatwe do ukończenia.
- **Utrzymywanie Aktualności**: Ciągły zapis wykonanych zadań, głównych kroków i promptów w uaktualnianym raporcie narzędzia. Analizuj co tydzień pod kątem improvement vibecoding skills (np. "Częste distraction: Więcej auto-saves").

### Focus Maintenance:
- **Auto-Save Everything**: Żeby nie stracić pracy przez distraction.
- **Context Switching**: Zaloguj gdzie skończyłeś przed przerwą.
- **Gentle Reminders**: Soft notifications, nie aggressive.
- **Energy Management**: Trudne zadania gdy masz najwięcej energii.

## 📊 Continuous Improvement

### Daily Habits:
1. **Prompt Logging**: Zapisuj wszystkie użyte prompty i kroki w raporcie.
2. **Reflection Time**: 10 min na koniec dnia - co poszło dobrze/źle? Analiza pod monetyzację.
3. **Skill Tracking**: Jakie nowe techniki nauczyłeś? Jak połączyć z skillami dla szybszego zarobku?
4. **Code Quality**: Review własnego kodu po 24h.

### Weekly Analysis:
1. **Pattern Recognition**: Jakie błędy się powtarzają? (np. z logów promptów).
2. **Efficiency Metrics**: Ile kodu wygenerowałeś vs napisałeś ręcznie?
3. **Learning Goals**: Co chcesz poprawić? Focus na ADHD: Więcej micro-tasks.
4. **AI Prompt Optimization**: Które prompty działają najlepiej? Update raport.

## 🔒 Security & Performance Standards

### Security Defaults:
- Environment variables dla secrets.
- Input validation wszędzie.
- Rate limiting na API.
- Regular dependency updates.

### Performance Optimization:
- Lazy loading gdzie możliwe.
- Caching strategically.
- Database queries optimized.
- Bundle size monitoring (frontend).

## 🚀 Git Workflow

### Branch Naming:
- `feature/add-user-auth`
- `fix/port-conflict-resolution`
- `docs/update-api-documentation`

### Commit Messages:
```
feat: add AI task generation [claude-prompt: generate todo tasks]
fix: resolve Docker port conflicts [automated solution]
docs: update README with setup instructions [ai-generated]
refactor: simplify code analyzer logic [manual optimization]
```

### Code Review Checklist:
- [ ] Kod jest self-documenting.
- [ ] Testy pokrywają główne scenariusze.
- [ ] Performance impact oceniony.
- [ ] Security implications rozważone.
- [ ] ADHD-friendly (nie overwhelming, log kroków).

## 💰 Monetization Mindset

### Code Quality = Business Value:
- Clean code = easier to sell/maintain.
- Good docs = easier to hand off to client.
- Tests = reliability = client trust.
- AI integration = competitive advantage (np. szybki freelance via skill matching).

### Quick Monetization Strategies:
1. **Package & Sell**: Transform utility scripts into SaaS (np. na HF).
2. **Template Creation**: Sell project templates on Gumroad.
3. **Freelance Automation**: Use AI to bid on relevant projects.
4. **Content Creation**: Document your vibecoding process (np. blog o ADHD coding).

This rules.md ensures consistency, quality, and continuous improvement across all projects while supporting ADHD-friendly development practices.
```

## 🎯 Propozycje Dodatkowych Funkcjonalności

### 1. AI Industry News Feed
- Integracja z Hugging Face Paper releases.
- Reddit r/MachineLearning trending posts.  
- Twitter AI influencers feed.
- Personalized news based na Twoje projekty i skille (np. "Nowe w Codex – połącz z Twoim workflow").

### 2. Freelance Project Matcher
- Scraping Upwork/Freelancer dla AI/Python projektów.
- Automatic bid generation based na Twoje skills (np. "Łatwy task: $300, matches Gemini CLI").
- Project difficulty assessment i ROI calculator.
- Filtr: "Łatwe do zrobienia w 1-2 dni dla quick monetyzacji".

### 3. Skill Development Tracker
- Analiza Twoich commitów dla skill progression (np. "Wzrost w HF usage o 20%").
- Identification skill gaps dla lepszej monetyzacji (np. "Dodaj Docker scaling dla SaaS").
- Learning path recommendations (np. "Kurs na Cursor dla faster coding").
- Integracja z online courses (Coursera/Udemy).

### 4. Automated Portfolio Generator
- Auto-update portfolio website z latest projektów.
- AI-generated project descriptions.
- Screenshots i demo links (z handlingiem IP zmian).
- Client testimonial integration dla vibecoder profile.

## 🔧 Setup i Deployment

### Wymagania Systemowe:
- Python 3.10+.
- Node.js 18+.
- Docker & Docker Compose.
- Git.
- 8GB RAM minimum.
- API keys: GitHub, OpenAI, HF, DuckDNS.

### Quick Start:
```bash
git clone https://github.com/yourusername/gitorder-ai-agent
cd gitorder-ai-agent
cp .env.example .env  # Edytuj z API keys, MCP consent
docker-compose up -d
# Otwórz dashboard: http://localhost:3000
# Uruchom agent: python main.py --scan
```

### Environment Variables:
```env
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_TOKEN=your_hf_token
DUCKDNS_TOKEN=your_duckdns_token
VPS_HOST=your_hostinger_ip
VPS_USER=your_ssh_user
DATABASE_URL=sqlite:///./gitorder.db
MCP_ENABLED=true  # Dla integracji MCP
```

## 📈 Oczekiwane Rezultaty

### Po 1 miesiącu:
- 100% projektów z pełną dokumentacją i listami zadań.
- Zero konfliktów portów przy deployment.
- Automatyczna synchronizacja z GitHub.
- 5+ potential monetization opportunities identified (np. freelance matches).

### Po 3 miesiącach:
- Pierwszy projekt successfully monetized (np. SaaS na HF).
- Portfolio showcase z 10+ clean projektów.
- Advanced AI recommendations working (newsy, skill analysis).
- Measurable improvement w coding efficiency via log analysis.

### Po 6 miesiącach:
- Stable income stream z 2-3 projektów.
- Recognition jako "top vibecoder" w community.
- Multiple passive income sources (np. templates sales).
- Advanced Agent Zero integration completed z pełnym raportem improvement.

Ten projekt to kompletne rozwiązanie dla uporządkowania chaosu projektowego, wykorzystania AI do maksymalizacji produktywności i szybkiej monetyzacji umiejętności programistycznych, szczególnie dostosowane do potrzeb osób z ADHD. Wyniki analizy i realizacji opierają się na Twoich skillach – np. szybka monetyzacja via proste integracje HF/Codex w freelance tools. Jeśli potrzeba zmian, daj znać!