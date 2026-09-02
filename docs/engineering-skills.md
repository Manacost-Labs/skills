# Engineering skills

Этот слой установлен в центральный каталог и доступен через профиль
`engineering`, который включён в общий профиль `server`.

## Импортированные источники

- [ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books) —
  импортированы компактные `mini`-версии инженерных rule-set’ов. Сам источник
  рекомендует `mini` для обычной работы, оставляя `full` как полный вариант.
- [nathankim0/clean-architecture-skills](https://github.com/nathankim0/clean-architecture-skills) —
  импортированы skills `clean-architecture` и `kent-beck-style` из plugin-пакета.
- [mattpocock/skills](https://github.com/mattpocock/skills) — импортированы
  только явно выбранные skills: `codebase-design`, `diagnosing-bugs`,
  `domain-modeling`, `improve-codebase-architecture` и
  `resolving-merge-conflicts`. Остальные skills источника не включались.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) —
  импортированы 10 явно выбранных engineering skills: API-контракты,
  CI/CD, context engineering, ADR-документация, frontend UI, Git workflow,
  performance, планирование, source-driven development и использование
  skills.
- [YurunChen/repo-docs-skills](https://github.com/YurunChen/repo-docs-skills) —
  импортированы `repo-docs` и `repo-docs-zh` вместе с их локальными
  reference-файлами и валидаторами. В закреплённой ревизии отдельный файл
  лицензии не найден; это явно отражено в inventory и NOTICE.
- [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) —
  импортирован `dependency-updater` вместе с его вспомогательными скриптами.

Commit SHA, путь внутри источника и локальный canonical id находятся в
`inventory/external-skills.tsv`.

## Правила применения

Эти материалы — on-demand guidance, а не безусловная замена проектным
`AGENTS.md`. При конфликте действует более специфичное правило проекта;
системные и security-инструкции всегда выше. Не загружай весь engineering
профиль в каждый prompt: выбирай только нужные skills.

Лицензии сохранены в `third_party/licenses/`.
