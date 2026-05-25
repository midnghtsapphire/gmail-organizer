# Security Policy

## Supported Scope
Security practices apply to all Python scripts, tests, and documentation in this repository.

## Credential Requirements
- Never commit `credentials.json`, `token.json`, or any `.env` secrets.
- Use least-privilege Gmail scopes where practical.
- Restrict file permissions on local token/credential storage.

## Reporting a Vulnerability
Open a private security report in GitHub security advisories or contact the repository owner directly with:
- Impact summary
- Reproduction steps
- Suggested remediation

## Secure Validation Checklist
- Run `npm test` and `npm run build` before release.
- Confirm no secrets are present in changed files.
- Re-run baseline checks after any security-sensitive change.
