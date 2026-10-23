# Contributing

Thanks for helping improve Enterprise AI Platform.

## Before making changes

1. Check existing issues and documentation to avoid duplicating work.
2. Keep each pull request focused on one improvement.
3. Never commit API keys, `.env` files, user documents, database dumps, or generated vector-store data.
4. Update documentation when changing configuration, API behavior, or setup steps.

## Validation checklist

### Backend

- Activate the project's virtual environment.
- Install dependencies from the backend dependency file.
- Run the available tests with `pytest -v` from the backend directory.
- Check imports and application startup when changing application wiring.

### Frontend

- Install dependencies using the package manager and lockfile used by the project.
- Run the available lint, type-check, and production-build scripts defined in `package.json`.
- Manually verify relevant screens and loading/error states for UI changes.

## Pull request checklist

- [ ] Explain the problem and the proposed solution.
- [ ] Keep changes scoped and avoid unrelated formatting churn.
- [ ] Add or update tests when behavior changes.
- [ ] Document new environment variables without including their secrets.
- [ ] Confirm no credentials or private data are included.
- [ ] Describe checks performed and any known limitations.

Security-sensitive changes should explain the threat being addressed and any remaining risks. Do not claim a security issue is resolved unless the fix has been verified.
