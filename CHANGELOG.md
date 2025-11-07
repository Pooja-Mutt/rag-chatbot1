# Changelog

## Latest Commit: Complete Implementation

### Enhancements Added:
1. **Clear Chat Button** - Reset conversation while keeping PDF loaded
2. **Remove PDF Button** - Remove uploaded PDF from session
3. **Better Error Messages** - User-friendly error handling for uploads and chat
4. **PDF Metadata Display** - Shows pages, size, character count after upload
5. **Input Validation** - Prevents empty messages
6. **Enhanced Status Messages** - Async status updates during processing
7. **Performance Optimization** - Removed slow recursive file search in upload handler

### Tests Added:
- Integration test for multiple streamed chunks
- Integration test for upload → parse → query → answer flow
- Sample PDF in tests/data for real file testing

### Deployment:
- Dockerfile for containerized deployment
- AWS deployment documentation
- Elastic Beanstalk configuration
- Requirements.txt for production

### Testing:
- All 17 tests passing (9 unit + 8 integration)
- Real PDF file in tests/data
- Full RAG flow verified

