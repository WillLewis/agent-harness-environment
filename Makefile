.PHONY: dev eval compare validate

dev:
	pnpm dev

validate:
	pnpm validate:fixtures

eval:
	pnpm eval

compare:
	pnpm compare
