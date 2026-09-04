# Единая политика AI-агентов

## Источник

Единственный глобальный источник политики для поддерживаемых AI-клиентов на
этом сервере — [`AGENTS.md`](../AGENTS.md) в репозитории
`/srv/projects/tools/skills`.

## Активные точки входа

Все перечисленные пути должны быть символическими ссылками на источник:

- серверные рабочие корни: `/home/debian/AGENTS.md`, `/srv/projects/AGENTS.md`,
  `/home/debian/server/AGENTS.md`;
- глобальные клиенты: `/home/debian/.codex/AGENTS.md`,
  `/home/debian/.config/opencode/AGENTS.md`, `/home/debian/.claude/CLAUDE.md`,
  `/home/debian/.gemini/GEMINI.md`.

Проверка:

```bash
/srv/projects/tools/skills/scripts/check-agent-entrypoints.sh
```

Установка глобальных клиентских ссылок:

```bash
/srv/projects/tools/skills/scripts/install-global-agent-entrypoints.sh --adopt-existing
```

Обычные существующие файлы перед заменой перемещаются в тот же каталог с
суффиксом `.legacy-<timestamp>-<pid>`, поэтому миграция обратима. Чужие ссылки,
каталоги и проектные/vendor policy-файлы скрипт не заменяет.

## Границы гарантии

Это покрывает обнаруженные на сервере клиенты и стандартные пути поиска
инструкций. Произвольный AI-клиент может проигнорировать `AGENTS.md`, если он
не поддерживает файловые инструкции. Ближайший `AGENTS.md` проекта и
vendor-specific policy остаются более узким контекстом и применяются согласно
иерархии в центральной политике.
