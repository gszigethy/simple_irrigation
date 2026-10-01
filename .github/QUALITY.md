# Simple irrigation CI checks

The workflows run tests, frontend builds, hassfest, HACS validation and coverage
reporting. The additional quality workflow validates Python syntax, compares Ruff
and frontend ESLint defect findings against the PR base, and runs ShellCheck.
Push comparisons use the previous commit; manual requests or new branches with
no valid prior commit report the current baseline. Findings are counted by file,
rule and message so line shifts do not fail CI. New findings are blocking.

Both Ruff scans use explicit isolated rules and scan gitignored Python files.
Both ESLint scans use the same explicit configuration and parser. The base scan
uses the installed tools and configuration from the current checkout.

Mypy and TypeScript checks start as nonblocking diagnostics. Mypy skips missing
third-party imports, so it is not a complete Home Assistant type check. Coverage
is reported in logs and uploaded as an artifact, without an arbitrary threshold.
The existing Home Assistant test dependency supplies the coverage plugin.

## CI dependencies

Python analyzers and transitive dependencies are pinned with artifact hashes in
`.github/ci/requirements.txt` for Python 3.13. CI verifies hashes and installs
wheels only. Update the direct versions in `requirements.in`, then run:

```sh
uv pip compile --python-version 3.13 --generate-hashes --only-binary :all: \
  --no-emit-index-url .github/ci/requirements.in -o .github/ci/requirements.txt
```

Frontend analyzers live in `.github/ci/node-tools`; their npm lock file includes
transitive versions and integrity hashes. CI installs them with `npm ci
--ignore-scripts`. To update the versions and lock file locally, run:

```sh
npm install --prefix .github/ci/node-tools --package-lock-only --ignore-scripts
```

The real frontend retains its own package and lock file. CI installs its
packages without lifecycle scripts and explicitly runs the existing build.

GitHub Action references are pinned to commits and maintained by Dependabot,
as are the CI npm analyzers. The HACS and hassfest validator container tags
remain managed by upstream; Action pins do not freeze those images.

## HACS publishing requirements

HACS file/schema checks are blocking. Repository publishing checks for enabled
issues and valid topics are skipped pending repository owner configuration.

These changes do not modify integration behavior, frontend source or versions,
and they do not publish a release.
