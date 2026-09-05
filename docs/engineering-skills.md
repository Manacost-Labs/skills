# Engineering skills

Этот слой установлен в центральный каталог и доступен через профиль
`engineering`, который включён в общий профиль `server`.

## Импортированные источники

- [obra/superpowers](https://github.com/obra/superpowers) — адаптированы
  brainstorming, writing-plans и requesting-code-review; они не заменяют
  общий policy-файл и не устанавливают второй глобальный workflow.
- [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) — добавлен
  явный code-only server-map workflow с изолированными результатами; полное
  индексирование сервера намеренно не запускается автоматически.
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
- [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) —
  импортированы 7 выбранных навыков по сжатию, деградации, оптимизации и
  архитектуре context engineering.
- [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch) —
  импортирована одна canonical-копия `autoresearch` из plugin-пути; четыре
  дублирующие установочные копии не размножались.
- [netresearch/github-project-skill](https://github.com/netresearch/github-project-skill) —
  импортирован skill для GitHub Projects, branch protection, Issues и PR
  workflow.
- [synthesisengineering/synthesis-skills](https://github.com/synthesisengineering/synthesis-skills) —
  импортированы 63 skills каталога Synthesis с локальными references,
  scripts и templates.
- [fugazi/test-automation-skills-agents](https://github.com/fugazi/test-automation-skills-agents) —
  импортированы 10 QA-навыков для API, Playwright, Selenium, accessibility,
  E2E и regression testing.
- [balyakin/skill-eval-runner](https://github.com/balyakin/skill-eval-runner) —
  добавлен локальный wrapper для CLI `ser`; upstream fixtures и исходники
  runner не устанавливались как skills.
- [LambdaTest/agent-skills](https://github.com/LambdaTest/agent-skills) —
  импортированы 72 навыка тестовой автоматизации для API, browser/mobile
  frameworks и CI. В Selenium Maven template добавлено явное безопасное
  ограничение `io.opentelemetry:opentelemetry-api` до `1.62.0` после security
  scan; исходный commit и изменение companion-файла отражены в provenance.
- [me2resh/agent-decision-record](https://github.com/me2resh/agent-decision-record) —
  добавлены универсальный `decide` и Codex-совместимый `agdr-decide` для
  структурированной фиксации архитектурных решений. Это две разные
  интеграционные формы одного upstream-стандарта.
- [vladikk/modularity](https://github.com/vladikk/modularity) — добавлены
  `balanced-coupling`, `design`, `document` и `review` для проектирования и
  проверки модульной архитектуры.
- [millionco/react-doctor](https://github.com/millionco/react-doctor) —
  добавлены `improve-react`, `improve-threejs` и `performance`. Базовый
  `react-doctor` уже был установлен как `core/react-doctor` и повторно не
  импортировался.
- [vercel-labs/next-skills](https://github.com/vercel-labs/next-skills) —
  репозиторий является redirect на version-matched skills в
  [vercel/next.js](https://github.com/vercel/next.js/tree/canary/skills).
  Добавлены четыре актуальных навыка из `vercel/next.js`: Cache Components,
  instant navigation/dev loop и Partial Prefetching.
- [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills) —
  добавлены шесть навыков для Core Web Vitals, accessibility, SEO, performance,
  best practices и общего web-quality audit.
- [jezweb/claude-skills](https://github.com/jezweb/claude-skills) — добавлен
  запрошенный `react-patterns`. В исходнике он помечен
  `compatibility: claude-code-only`; это ограничение сохранено в canonical
  файле и требует явного выбора только в совместимом агентском runtime.
- [mblode/agent-skills](https://github.com/mblode/agent-skills) — добавлен
  `ui-design` с режимами direction, build, audit, retrofit и componentize,
  а также связанными правилами accessibility, responsive UI и performance.
- [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) — к
  ранее импортированному `dependency-updater` добавлен
  `design-system-starter` с design tokens, компонентной архитектурой,
  темизацией и WCAG-чеклистом.
- [nutlope/hallmark](https://github.com/nutlope/hallmark) — добавлен
  `hallmark` для структурного дизайна, anti-slop аудита, responsive-проверок
  и аккуратных motion-паттернов. Самостоятельный Hallmark CLI не копировался в
  каталог навыков.
- [arvindrk/extract-design-system](https://github.com/arvindrk/extract-design-system)
  — добавлен `extract-design-system` для извлечения стартовых токенов из
  публичных сайтов. Он не заменяет существующую дизайн-систему и не изменяет
  проектный код без отдельного подтверждения.

Commit SHA, путь внутри источника и локальный canonical id находятся в
`inventory/external-skills.tsv`.

## Правила применения

Эти материалы — on-demand guidance, а не безусловная замена проектным
`AGENTS.md`. Приоритет: system/platform → developer/security → явный запрос
пользователя → project AGENTS.md → server AGENTS.md → профиль → skill.
Профили содержат `available:`, а не автоматически загружаемый `load:`.
Используй `skillctl route` для ограниченного набора, а `list` — только для
просмотра каталога. Исполняемые проверки и переход со старого формата описаны
в [engineering-system.md](engineering-system.md).

## Security baseline

Новые файлы прошли staged gitleaks scan и OSV scan без находок. Полный
исторический `ai-security-check` всё ещё показывает пять pre-existing
совпадений в ранее импортированных файлах
`skills/engineering/qa/lambdatest/appium-skill/SKILL.md`,
`skills/engineering/qa/lambdatest/xcuitest-skill/reference/playbook.md` и
`skills/engineering/synthesis/synthesis-git-hooks/scripts/test_pre_commit.py`;
они не изменялись в этом импорте и требуют отдельного baseline-review.

Лицензии сохранены в `third_party/licenses/`.
