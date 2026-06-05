.PHONY: dev eval compare validate eval-suite eval-ci

dev:
	pnpm dev

validate:
	pnpm validate:fixtures

eval:
	pnpm eval

eval-suite:
	pnpm eval:suite

eval-ci:
	pnpm eval:ci

compare:
	pnpm compare
