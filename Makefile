.PHONY: sync apply-patches build test runtime-test lint generate

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

generate:
	echo "No generated assets yet"
