# Contributing to PDET Solar Rooftop Analysis

## Project Workflow

This project follows a structured deliverable-based workflow. All contributions should align with the current deliverable timeline.

## Deliverables Timeline

- **Deliverable 1**: October 27, 2:00 PM - NoSQL Database Schema Design
- **Deliverable 2**: November 3, 2:00 PM - PDET Municipality Boundaries Integration
- **Deliverable 3**: November 10, 2:00 PM - Building Footprint Data Loading
- **Deliverable 4**: November 17, 2:00 PM - Geospatial Analysis Workflow
- **Deliverable 5**: November 24, 2:00 PM - Final Technical Report

## Git Workflow

### Branch Naming Convention

- `main` - Production-ready code
- `develop` - Development branch
- `deliverable-N` - Branch for deliverable N
- `feature/feature-name` - Feature branches
- `fix/bug-name` - Bug fix branches

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `deliverable`: Deliverable-related commits

**Example:**
```
feat: add MongoDB connection module

Implemented MongoDB connection handler with spatial indexing support
for building footprint data.

Relates to Deliverable #1
```

## Code Style

### Python

- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters (Black default)

### Documentation

- Use docstrings for all functions, classes, and modules
- Follow Google-style docstring format
- Include type hints where applicable

## Testing

- Write unit tests for all new functions
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes
3. Run tests and ensure they pass
4. Update documentation if needed
5. Submit PR to `develop` branch
6. Request review from team members
7. Address review comments
8. Merge after approval

## Directory Structure

```
pdet-solar-rooftop-analysis/
├── data/
│   ├── raw/              # Original datasets (gitignored)
│   └── processed/        # Processed data (gitignored)
├── src/                  # Source code
├── notebooks/            # Jupyter notebooks
├── docs/                 # Documentation
├── deliverables/         # Deliverable submissions
├── results/              # Analysis results
├── config/               # Configuration files
└── tests/                # Unit tests
```

## Questions?

If you have questions about the project or contribution process, please:
1. Check existing documentation
2. Review project requirements in `docs/project_requirements.tex`
3. Contact team members

## License

This project is developed as part of an academic assignment.
