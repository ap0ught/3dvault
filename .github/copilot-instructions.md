# GitHub Copilot Instructions for 3D Vault

## Project Overview

3D Vault is a Django-based system for managing collections of 3D models, PDFs, and related files with ZIP import capabilities, security controls, and audit trails.

## Technology Stack

- **Framework**: Django 5.1.1
- **REST API**: Django REST Framework (DRF)
- **Database**: SQLite (development), configurable for production
- **Python Version**: 3.12+
- **Key Dependencies**: Pillow, djangorestframework

## Code Style and Standards

### Python Style
- Follow **PEP 8** for code style
- Use **PEP 257** for docstrings (all public functions, classes, and modules)
- Apply **PEP 484** type hints throughout
- Prefer utility functions outside classes (avoid unnecessary `@staticmethod`)
- Keep code clean, tested, and production-ready

### Django Conventions
- Use Django 5.1.1 best practices
- Atomic transactions for data modifications
- Proper model relationships with appropriate `on_delete` behaviors
- Use `get_user_model()` instead of direct User imports
- Follow Django's URL naming conventions

### Documentation
- All functions must have docstrings explaining:
  - Purpose
  - Args with types
  - Returns with types
  - Raises (exceptions)
- Use type hints for all function parameters and return values
- Keep comments focused on "why" not "what"

## Project Structure

```
3dvault/
├── config/              # Django project settings
├── services/            # Business logic (keep separate from Django apps)
│   └── collections/     # Collection-specific services
├── vault/               # Main Django app
│   ├── models.py        # Collection, VaultFile, UserHistory, EmailQueue
│   ├── views.py         # DRF ViewSets
│   ├── serializers.py   # DRF Serializers
│   ├── admin.py         # Django admin configuration
│   ├── management/      # Management commands
│   ├── tests/           # Test package (not tests.py)
│   └── templates/       # Django templates
├── media/               # User uploads (gitignored)
└── README.md
```

## Key Concepts

### Models
- **Collection**: Container for related files with auto-generated slug
- **VaultFile**: Individual files with type classification (STL, PDF, OTHER)
- **UserHistory**: Audit log for all user actions
- **EmailQueue**: Queue for outgoing notifications

### Security
- **Zip-slip protection**: All file paths must be validated
- **Zip-bomb protection**: Configurable limits on ZIP size and entry count
- **Deduplication**: SHA-256 hashing to prevent duplicate storage
- **Audit trail**: All imports logged in UserHistory

### Settings
- `ZIP_IMPORT_MAX_ENTRIES`: Maximum files in a ZIP (default: 5000)
- `ZIP_IMPORT_MAX_TOTAL_BYTES`: Maximum ZIP size (default: 1GB)

## Development Guidelines

### Adding New Features

1. **Service Layer**: Business logic goes in `services/` directory
   - Keep Django-agnostic where possible
   - Use atomic transactions
   - Handle errors gracefully

2. **API Endpoints**: Add to appropriate ViewSet in `vault/views.py`
   - Use DRF serializers for validation
   - Return appropriate HTTP status codes
   - Document with docstrings

3. **Management Commands**: Place in `vault/management/commands/`
   - Inherit from `BaseCommand`
   - Provide helpful help text
   - Use `CommandError` for user-facing errors

4. **Admin Actions**: Add to relevant ModelAdmin in `vault/admin.py`
   - Use custom forms when needed
   - Provide user feedback via messages
   - Handle errors gracefully

### Testing

- **Location**: All tests in `vault/tests/` package
- **Coverage**: Aim for comprehensive test coverage
  - Unit tests for individual functions
  - Integration tests for workflows
  - Security tests for attack vectors
  - API tests for endpoints
- **Naming**: `test_*.py` files with descriptive test names
- **Best Practices**:
  - Use Django's `TestCase` or `override_settings` as needed
  - Clean up test artifacts (files, directories)
  - Mock external dependencies
  - Test both success and failure paths

### Security Considerations

Always validate:
- File paths (prevent directory traversal)
- File sizes (prevent resource exhaustion)
- User permissions (authenticate and authorize)
- Input data (sanitize and validate)

For ZIP imports:
- Use `safe_join()` to prevent zip-slip
- Check entry count and total size before extraction
- Hash files for deduplication
- Log all operations

## Common Tasks

### Running Tests
```bash
python manage.py test vault.tests -v 2
```

### Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Importing a ZIP Collection
```bash
python manage.py import_zip_to_collection /path/to/file.zip --owner=1
```

### API Import
```bash
POST /api/collections/import-zip/
{
  "zip_path": "/path/to/file.zip",
  "owner_id": 1
}
```

## Future Enhancements (Stubs in Place)

- **RAG Indexing**: PDF semantic search (`vault/rag.py`)
- **Plate Generation**: Auto-generate print plates from STL files
- **Layer XP**: Experience points for user actions
- **Email Routing**: Whitelist-based email delivery
- **ClamAV Integration**: Virus scanning for uploads

## Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Clean up resources in finally blocks
- Use atomic transactions to prevent partial updates

## Code Review Checklist

Before submitting code:
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Tests cover new functionality
- [ ] Security considerations addressed
- [ ] No sensitive data in code/logs
- [ ] Migrations created if models changed
- [ ] Error handling in place
- [ ] Code follows PEP 8
- [ ] No TODO/FIXME in production code

## Dependencies

When adding new dependencies:
- Add to `requirements.txt`
- Document why it's needed
- Consider security implications
- Keep versions pinned for production

## Contact and Resources

- Issue Tracker: GitHub Issues
- Documentation: README.md
- Style Guide: This file + PEP 8/257/484
