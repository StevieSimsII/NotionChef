# AGENTS.md — NotionChef Workspace Rules

## Mission
Build and maintain NotionChef as a reliable recipe-capture system:
- URL -> parsed recipe -> structured Notion entry
- Optional Telegram bot for fast capture

## Operating Priorities
1. Reliability first (clear errors, safe retries, no silent failure)
2. Keep setup simple for Stevie
3. Protect secrets and avoid token leaks
4. Prefer small, testable changes

## Workflow
- Use short implementation plans before major changes
- Keep commits focused and readable
- Update README when behavior changes
- Add troubleshooting notes when fixes are discovered

## Safety & Secrets
- Never commit `.env`
- Never log raw tokens
- Redact secrets in examples and screenshots
- If a token is exposed, rotate immediately

## Definition of Done (for features/fixes)
- Code updated
- README updated (if needed)
- Local test run completed
- Error handling verified
- Ready for commit/push