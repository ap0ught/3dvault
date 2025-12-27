# 3dvault

A Django-based 3D file vault system with ZIP import capabilities for managing collections of 3D models, PDFs, and related files.

## Features

### ZIP → Collection Importer

Import ZIP archives as organized collections with automatic file classification, deduplication, and safety features.

**Key Features:**
- ✅ Automatic file type detection (STL, PDF, and other formats)
- ✅ SHA-256 based deduplication within collections
- ✅ Zip-slip and zip-bomb protection
- ✅ Configurable size and entry limits
- ✅ User history and email queue integration
- ✅ RAG (Retrieval-Augmented Generation) indexing stub for PDFs
- ✅ Multiple import methods: CLI, API, and Admin interface

## Installation

```bash
# Clone the repository
git clone https://github.com/ap0ught/3dvault.git
cd 3dvault

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
```

## Usage

### Command Line Interface

Import a ZIP file as a new collection:

```bash
python manage.py import_zip_to_collection <path/to/file.zip> [--owner=<user_id>]
```

Example:
```bash
python manage.py import_zip_to_collection /tmp/River_Dragon.zip --owner=1
```

### REST API

**Endpoint:** `POST /api/collections/import-zip/`

**Upload a file:**
```bash
curl -X POST http://localhost:8000/api/collections/import-zip/ \
  -F "file=@/path/to/collection.zip" \
  -F "owner_id=1"
```

**Use a server path:**
```bash
curl -X POST http://localhost:8000/api/collections/import-zip/ \
  -H "Content-Type: application/json" \
  -d '{"zip_path": "/path/to/collection.zip", "owner_id": 1}'
```

**Response:**
```json
{
  "collection_slug": "river-dragon",
  "collection_name": "River Dragon",
  "created_files": 15,
  "skipped_duplicates": 0,
  "total_bytes": 1024000
}
```

### Django Admin

1. Navigate to the admin interface at `/admin/`
2. Go to Collections
3. Select the "Import ZIP as New Collection" action from the actions dropdown
4. Upload your ZIP file and select an optional owner
5. Click "Import"

## Configuration

Add these settings to your Django settings file to customize limits:

```python
# Maximum number of entries allowed in a ZIP file
ZIP_IMPORT_MAX_ENTRIES = 5000

# Maximum total bytes allowed in a ZIP file (default: 1GB)
ZIP_IMPORT_MAX_TOTAL_BYTES = 1_000_000_000
```

## Security

The ZIP importer includes multiple security protections:

- **Zip-slip protection:** Prevents path traversal attacks
- **Zip-bomb protection:** Limits on entries and total extracted size
- **File deduplication:** SHA-256 hashing prevents duplicate storage
- **Audit logging:** All imports are logged in UserHistory

### Best Practices

- Set appropriate `ZIP_IMPORT_MAX_ENTRIES` and `ZIP_IMPORT_MAX_TOTAL_BYTES` for your use case
- Consider adding ClamAV integration for virus scanning
- Implement hash blocklists for known malicious files
- Review audit logs regularly

## Models

### Collection
Represents a collection of related files.

**Fields:**
- `name`: Human-readable collection name
- `slug`: URL-friendly identifier (auto-generated)
- `source`: Origin of the collection (e.g., "zip_import")
- `created_by`: Optional foreign key to User
- `created_at`: Timestamp

### VaultFile
Individual files within a collection.

**Fields:**
- `collection`: Foreign key to Collection
- `file`: FileField with actual file data
- `file_type`: STL, PDF, or OTHER
- `sha256`: Hash for deduplication
- `original_name`: Original filename from ZIP
- `size_bytes`: File size
- `created_at`: Timestamp

### UserHistory
Audit log of user actions.

**Fields:**
- `user`: Foreign key to User (nullable)
- `action`: Action name (e.g., "zip_import")
- `metadata`: JSON field with action details
- `created_at`: Timestamp

### EmailQueue
Queue for outgoing email notifications.

**Fields:**
- `to_email`: Recipient email address
- `subject`: Email subject
- `body`: Email body text
- `classification`: ADMINISTRATIVE, FILE_UPDATES, or USER_ACTIONS
- `is_sent`: Boolean flag
- `created_at`: Timestamp

## Development

### Running Tests

```bash
python manage.py test vault.tests -v 2
```

### Code Style

This project follows:
- PEP 8 for code style
- PEP 257 for docstrings
- PEP 484 for type hints

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Contribution guidelines
- Code review process
- Branch protection requirements
- CI/CD workflow information

## Future Enhancements

- **Plate Generation:** Auto-generate print plates from STL files
- **Layer XP:** Award experience points for successful imports
- **RAG Indexing:** Full implementation for PDF semantic search
- **Email Whitelist:** Admin-configurable email routing rules
- **ClamAV Integration:** Virus scanning for uploaded files

## License

See LICENSE file for details.

