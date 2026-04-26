# Repository Guidelines

## Project Structure & Module Organization

This repository contains coursework infrastructure labs for cloud computing.

- `README.md`: top-level Vagrant overview and basic workflow.
- `IaC/`: base three-node Ubuntu 24.04 Vagrant cluster definition.
- `DSS/`: distributed storage lab built on a three-node GlusterFS cluster.
- `DSS/fio_failover_test.sh`: failover test script that runs `fio`, halts one Vagrant node, and records JSON output.
- `DSS/logs/`: generated `fio` result files. Treat these as experiment artifacts.
- `S3/`: currently empty; use it for future S3-related lab material if needed.

## Build, Test, and Development Commands

Run commands from the relevant lab directory unless noted.

```bash
cd IaC && vagrant up
```
Creates the base `node1` to `node3` cluster.

```bash
cd DSS && vagrant up
```
Creates the GlusterFS-enabled cluster and provisions volume `gv0`.

```bash
vagrant status
vagrant ssh node1
vagrant destroy
```
Inspect VM state, connect to a node, or remove lab VMs.

```bash
cd DSS && ./fio_failover_test.sh node1
```
Runs a read/write failover scenario and stores JSON output in `DSS/logs/`.

## Coding Style & Naming Conventions

Vagrantfiles are Ruby files; use two-space indentation and descriptive snake_case variables such as `node_count`, `ip_base`, and `hosts_entries`. Shell scripts should use Bash with `set -euo pipefail`, uppercase environment-configurable variables, and quoted expansions. Keep node names and host entries consistent with `node1`, `node2`, `node3` and the `192.168.56.11-13` range.

## Testing Guidelines

There is no unit test framework. Validate changes by reprovisioning the affected Vagrant environment and checking `vagrant status`. For DSS changes, run `./fio_failover_test.sh <node>` and review the exit code plus the generated JSON log. When changing provisioning logic, prefer destroying and recreating VMs to confirm a clean bootstrap path.

## Commit & Pull Request Guidelines

Existing history uses short Korean commit summaries, for example `README.md 수정` and `IaC, DSS dir 추가`. Keep commits focused and imperative, naming the touched area when useful. Pull requests should include the lab area changed, commands executed, observed results, and any generated logs worth reviewing. Link issues when available and include terminal excerpts instead of screenshots unless UI output is involved.

## Security & Configuration Tips

Private keys named `cluster_key` are used for local VM SSH. Do not introduce new reusable secrets or publish real credentials. If replacing keys, update both `cluster_key` and `cluster_key.pub` together and verify node-to-node SSH before running storage tests.
