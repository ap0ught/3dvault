## ZIP → Collection Importer

### Checklist

- [ ] Service `import_zip_as_new_collection` with safety checks (zip-slip, size caps)
- [ ] Management command `import_zip_to_collection`
- [ ] DRF endpoint POST /api/collections/import-zip/
- [ ] Admin action for ZIP import
- [ ] Tests: happy path, duplicates, zip-slip, size caps, history/emailqueue, RAG enqueue
- [ ] Docs: README + ops notes + settings
- [ ] Type hints, docstrings, PEP 8/257 satisfied

### Description

<!-- Describe the changes made in this PR -->

### Testing

<!-- Describe how you tested these changes -->

### Security Considerations

- [ ] Zip-slip protection verified
- [ ] Zip-bomb protection verified
- [ ] File deduplication working correctly
- [ ] Audit logging in place

### Related Issues

<!-- Link to related issues -->
