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

Commit SHA, путь внутри источника и локальный canonical id находятся в
`inventory/external-skills.tsv`.

## Правила применения

Эти материалы — on-demand guidance, а не безусловная замена проектным
`AGENTS.md`. При конфликте действует более специфичное правило проекта;
системные и security-инструкции всегда выше. Не загружай весь engineering
профиль в каждый prompt: выбирай только нужные skills.

Лицензии сохранены в `third_party/licenses/`.
