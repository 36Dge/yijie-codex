.PHONY: sync apply-patches build test runtime-test lint generate runtime-baseline

.PHONY: input-only-build
input-only-build:
	bash scripts/build-input-only.sh

sync:
	./scripts/sync-upstream.sh

apply-patches:
	./scripts/apply-yijie-patches.sh

build:
	./scripts/build-all.sh

test:
	./scripts/test-fork-management.sh

runtime-test:
	./scripts/test-runtime.sh

lint:
	bash -n scripts/*.sh
	./scripts/lint-python.sh

generate:
	./scripts/generate-app-server-schema.sh

runtime-baseline: sync apply-patches build generate runtime-test
