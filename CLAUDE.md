# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

書籍管理システム - A Django-based book management system that:
- Imports approved book purchase requests from Google Sheets (hourly batch process)
- Fetches book information from Google Books API using ISBN codes
- Manages book status lifecycle (ordered → available → rented)
- Tracks rental/return history with borrower information
- Provides Django admin interface for management

**Tech Stack**: Django 5.0.9, MySQL 8.0, Docker, Google Sheets/Books APIs

## Development Commands

### Container Management
All Docker commands use the `docker/docker-compose.yml` file:

```bash
# Start containers
docker-compose -f docker/docker-compose.yml up -d

# Stop containers
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f app

# Restart containers
docker-compose -f docker/docker-compose.yml restart
```

### Database Operations

```bash
# Run migrations
docker-compose -f docker/docker-compose.yml exec app python manage.py migrate

# Create migrations
docker-compose -f docker/docker-compose.yml exec app python manage.py makemigrations

# Create superuser
docker-compose -f docker/docker-compose.yml exec app python manage.py createsuperuser

# Access MySQL shell
docker-compose -f docker/docker-compose.yml exec db mysql -u bookadmin -p book_management

# Django shell
docker-compose -f docker/docker-compose.yml exec app python manage.py shell
```

### Testing

```bash
# Run all tests
docker-compose -f docker/docker-compose.yml exec app python manage.py test

# Run with verbose output
docker-compose -f docker/docker-compose.yml exec app python manage.py test books --verbosity=2

# Run specific test class
docker-compose -f docker/docker-compose.yml exec app python manage.py test books.tests.BookModelTests
```

**Note**: Test suite includes 20+ test cases covering models, API clients, and endpoints.

### Batch Processing

```bash
# Manual import from Google Sheets
docker-compose -f docker/docker-compose.yml exec app python manage.py import_from_sheets

# Test Google Sheets connection
docker-compose -f docker/docker-compose.yml exec app python manage.py test_sheets_connection

# Create sample data (for development)
docker-compose -f docker/docker-compose.yml exec app python manage.py create_sample_data
docker-compose -f docker/docker-compose.yml exec app python manage.py create_sample_data --clear

# Run via scripts
./scripts/run_batch.sh
./scripts/test_batch.sh
```

**Production**: Batch is scheduled via cron (hourly) - see `config/crontab`

## Architecture

### Django Project Structure

- **Project root**: `app/`
- **Settings module**: `config/` (not the Django app name)
- **Main app**: `books/` - single app handling all book management functionality

### Key Components

**Models** (`app/books/models.py`):
- `Book`: Master table for books with application info, book metadata (from Google Books API), and status management
- `RentalHistory`: Tracks borrowing/return with dates and borrower names
- `ErrorLog`: Records batch processing errors for admin review

**Google API Integrations** (`app/books/utils/`):
- `google_sheets_client.py`: Fetches approved requests from Google Sheets
- `google_books_client.py`: Retrieves book metadata by ISBN from Google Books API

**Batch Processing** (`app/books/management/commands/`):
- `import_from_sheets.py`: Main hourly batch job
  - Reads rows from Google Sheets
  - Checks for duplicates by `application_number`
  - Fetches book info from Google Books API
  - Creates Book records with error handling
  - Logs errors to `ErrorLog` model (not files)
- `test_sheets_connection.py`: Diagnostic tool for Google Sheets API
- `create_sample_data.py`: Development data generator

**Admin Interface** (`app/books/admin.py`):
- Customized Django admin with search, filters, and inline rental history
- Access at http://localhost:8001/admin
- Default credentials: admin/admin123 (change in production)

### Configuration Pattern

Environment variables are loaded from `credentials/.env` (use `credentials/.env.example` as template):
- Database credentials (MySQL connection)
- Google API paths and keys
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)

**Critical**:
- `GOOGLE_SHEETS_CREDENTIALS_PATH`: Path to service account JSON file (must share spreadsheet with this service account)
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Extract from spreadsheet URL
- Logs are written to `/var/log/book-management/` (mounted from `./logs`)

### Status Flow

Books follow this state machine:
1. `ordered` (購入中): Initial state from sheet import
2. `available` (本棚保管中): Book received and shelved
3. `rented` (貸出中): Currently borrowed (Book.get_current_borrower() returns name)
4. `other` (その他): Exceptional states

### Duplicate Prevention

The batch import uses `application_number` (申請番号) as the unique identifier. Check for existing records with matching `application_number` before creating new Book entries.

### Error Handling Philosophy

Batch processing is designed to be resilient:
- Errors for individual rows are logged to `ErrorLog` model
- Processing continues for remaining rows
- Admins review errors via Django admin interface
- No manual log file parsing needed

## Common Development Patterns

### Adding New Management Commands

Create in `app/books/management/commands/` following Django's BaseCommand pattern. See existing commands for reference.

### Modifying Batch Logic

Edit `import_from_sheets.py`. Key considerations:
- Maintain duplicate check via `application_number`
- Log errors to `ErrorLog` model, don't raise exceptions
- Use transactions for data consistency
- Test with `test_sheets_connection.py` first

### Extending Models

When adding fields:
1. Edit `app/books/models.py`
2. Create migration: `docker-compose -f docker/docker-compose.yml exec app python manage.py makemigrations`
3. Apply migration: `docker-compose -f docker/docker-compose.yml exec app python manage.py migrate`
4. Update `admin.py` if field should appear in admin interface
5. Write tests in `app/books/tests.py`

### Working with Google APIs

Both API clients are in `app/books/utils/`:
- Google Sheets client uses service account authentication (JSON file)
- Google Books API uses optional API key (works without but has stricter rate limits)
- Credentials configured via environment variables in `credentials/.env`

## Important Notes

- **Port**: Application runs on port 8001 (not 8000) to avoid conflicts
- **Timezone**: Asia/Tokyo (configured in settings.py and docker-compose.yml)
- **Language**: Japanese (LANGUAGE_CODE='ja')
- **Character Encoding**: UTF-8 (MySQL configured with utf8mb4)
- **Working Directory**: Always relative to project root (`/app` in container)
