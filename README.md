# Manacost Labs Skills

Единый каталог навыков для AI-агентов и инженерных workflow на Debian-сервере.

Репозиторий решает две разные задачи:

- хранит проверенные локальные навыки в одном месте;
- показывает, где ещё существуют старые копии, пока проекты мигрируют.

Он не удаляет файлы из `/srv/projects` и не изменяет production-копии в
`/var/www` автоматически.

## Структура

```text
AGENTS.md                 главный контракт каталога
registry.yaml             машинный реестр, профили и источники
profiles/                 наборы навыков для типов проектов
skills/                   канонические SKILL.md
inventory/skills.tsv      снимок навыков и хэшей исходных копий
inventory/sources.tsv     все найденные исходные пути и их хэши
scripts/                  безопасные проверки и аудит
docs/migration.md         порядок подключения проектов
docs/upstream-skills-roadmap.md  решения по новым upstream skills
```

Канонический путь навыка:

```text
skills/<namespace>/<skill-id>/SKILL.md
```

Одинаковые тексты дедуплицируются. Разные версии одного имени получают
разные namespace, например `wordpress/hs-manacost` и
`wordpress/kolodahearthstone`.

## Как агент выбирает навыки

Сначала применяются системные и проектные правила, затем профиль проекта и
только после этого — минимальный набор подходящих `SKILL.md`. Наличие навыка в
каталоге не означает автоматического включения или разрешения на опасное
действие.

Профили первой версии:

- `server` — общая работа сервера и координация агентов;
- `openbot` — OpenBot и интерфейс чата;
- `hearthpulse` — сервисы HearthPulse;
- `wordpress` — WordPress-сайты и плагины;
- `data` — парсеры, контроль данных и Python.
- `engineering` — общий слой архитектуры, отладки, DDD, UI/design system и
  безопасного рефакторинга.

Профиль `server` включает `engineering` как общий on-demand слой; это делает
skills доступными всему серверу, но не заставляет загружать их все в каждый
запрос.

## Проверка

```bash
./scripts/validate-registry.sh
# после изменений в старых каталогах
./scripts/refresh-sources-inventory.sh
# посмотреть активный набор
./scripts/skillctl list openbot
# общий инженерный слой
./scripts/skillctl list engineering
# построить план миграции без изменений
./scripts/skillctl plan /srv/projects/web/work.kolodahearthstone.com
# проверить расхождения локальных копий
./scripts/skillctl audit /srv/projects/web/work.kolodahearthstone.com
# проверить краткий итог агента (из файла или stdin)
./scripts/skillctl check-response < response.md
```

Серверные entrypoint-файлы `/home/debian/AGENTS.md`,
`/srv/projects/AGENTS.md` и `/home/debian/server/AGENTS.md`, а также глобальные
файлы обнаруженных клиентов `/home/debian/.codex/AGENTS.md`,
`/home/debian/.config/opencode/AGENTS.md`, `/home/debian/.claude/CLAUDE.md`,
`/home/debian/.gemini/GEMINI.md`, `/home/debian/.dsh/AGENTS.md`,
`/home/debian/.hermes/AGENTS.md` и `/home/debian/.cursor/rules/AGENTS.md`
должны быть ссылками на этот `AGENTS.md`. Для Cursor дополнительно действует
always-on адаптер `/home/debian/.cursor/rules/manacost-global.mdc`, который
ссылается на `integrations/cursor/manacost-global.mdc`.
Серверные ссылки устанавливаются через `scripts/install-server-entrypoints.sh`.
Глобальные ссылки клиентов устанавливаются через
`scripts/install-global-agent-entrypoints.sh --adopt-existing`; перед заменой
обычного файла он сохраняется как обратимый `.legacy-*` backup. Все ссылки
проверяются командой `scripts/check-agent-entrypoints.sh`.

Это гарантирует единый источник для обнаруженных клиентов и рабочих корней,
но не может заставить произвольный ИИ-клиент, который игнорирует файловые
инструкции, прочитать их. Для Hermes `SOUL.md` намеренно остаётся отдельным
файлом личности, а ближайшие project/vendor policy-файлы сохраняются и могут
дополнять правила для своего проекта.

Проверка не требует установки Node или Bun: она валидирует структуру,
уникальность ids, обязательные frontmatter-поля и отсутствие очевидных
секретов в каноническом каталоге.

## Миграция проектов

Подключение выполняется по одному проекту. Сначала добавляется ссылка на
профиль, затем проект прогоняет свои проверки, и только после успешного
наблюдения удаляются локальные копии. Подробный runbook находится в
`docs/migration.md`.
