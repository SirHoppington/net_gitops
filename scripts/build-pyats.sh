#!/bin/bash
# Build the pyATS test image and load it into the kind cluster.
# Run whenever pyats/run_test.py or pyats/inventory/testbed.yaml change.
#   ./scripts/build-pyats.sh
set -euo pipefail

IMAGE="${IMAGE:-pyats-clab:latest}"
CLUSTER="${CLUSTER:-c9s}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker build -f "${ROOT}/pyats/Dockerfile-pyats" -t "${IMAGE}" "${ROOT}"
kind load docker-image "${IMAGE}" -n "${CLUSTER}"
echo "Loaded ${IMAGE} into kind cluster ${CLUSTER}"
