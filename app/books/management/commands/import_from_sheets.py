"""
書籍情報取り込みDjango管理コマンド

Google Sheetsから承認済み申請を取得し、Google Books APIで書籍情報を取得してDBに登録する

Usage:
    python manage.py import_from_sheets
"""

import logging
from typing import Dict, Any, Tuple
from django.core.management.base import BaseCommand
from books.models import Book, ErrorLog
from books.utils.google_sheets_client import GoogleSheetsClient
from books.utils.google_books_client import GoogleBooksClient

logger = logging.getLogger(__name__)


class BookImportBatch:
    """書籍取り込みバッチクラス"""
    
    def __init__(self):
        """初期化"""
        self.sheets_client = None
        self.books_client = None
        self.success_count = 0
        self.error_count = 0
        self.skip_count = 0
        
    def initialize_clients(self) -> bool:
        """
        APIクライアントを初期化
        
        Returns:
            初期化成功時True
        """
        try:
            logger.info("Initializing API clients...")
            
            # Google Sheets クライアント初期化
            self.sheets_client = GoogleSheetsClient()
            self.sheets_client.authenticate()
            logger.info("Google Sheets client initialized")
            
            # Google Books クライアント初期化
            self.books_client = GoogleBooksClient()
            logger.info("Google Books client initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {str(e)}")
            self._record_error(
                application_number=None,
                isbn=None,
                error_type="INITIALIZATION_ERROR",
                error_message=f"API client initialization failed: {str(e)}"
            )
            return False
    
    def process(self) -> Tuple[int, int, int]:
        """
        メイン処理
        
        Returns:
            (成功件数, エラー件数, スキップ件数)
        """
        logger.info("=" * 50)
        logger.info("Book import batch started")
        logger.info("=" * 50)
        
        try:
            # APIクライアント初期化
            if not self.initialize_clients():
                logger.error("Batch terminated due to initialization failure")
                return (0, 1, 0)
            
            # スプレッドシートから取り込み対象データを取得
            logger.info("Fetching pending rows from spreadsheet...")
            pending_rows = self.sheets_client.get_pending_rows()
            
            if not pending_rows:
                logger.info("No pending rows found")
                return (0, 0, 0)
            
            logger.info(f"Found {len(pending_rows)} pending rows")
            
            # 各行を処理
            for idx, row_data in enumerate(pending_rows, 1):
                logger.info(f"Processing row {idx}/{len(pending_rows)}: Application #{row_data.get('application_number')}")
                self._process_row(row_data)
            
            # 結果サマリー
            logger.info("=" * 50)
            logger.info("Batch processing completed")
            logger.info(f"Success: {self.success_count}")
            logger.info(f"Error: {self.error_count}")
            logger.info(f"Skip: {self.skip_count}")
            logger.info("=" * 50)
            
            return (self.success_count, self.error_count, self.skip_count)
            
        except Exception as e:
            logger.error(f"Unexpected error in batch process: {str(e)}")
            self._record_error(
                application_number=None,
                isbn=None,
                error_type="BATCH_ERROR",
                error_message=f"Batch process failed: {str(e)}"
            )
            return (self.success_count, self.error_count + 1, self.skip_count)
    
    def _process_row(self, row_data: Dict[str, Any]) -> None:
        """
        1行分のデータを処理
        
        Args:
            row_data: スプレッドシートの行データ
        """
        application_number = row_data.get('application_number', '')
        isbn = row_data.get('isbn', '').strip()
        row_index = row_data.get('row_index')
        
        try:
            # ISBNの妥当性チェック
            if not isbn:
                logger.warning(f"Application #{application_number}: ISBN is empty, skipping")
                self.skip_count += 1
                return
            
            if not self.books_client.validate_isbn(isbn):
                logger.error(f"Application #{application_number}: Invalid ISBN format: {isbn}")
                self._record_error(
                    application_number=application_number,
                    isbn=isbn,
                    error_type="INVALID_ISBN",
                    error_message=f"Invalid ISBN format: {isbn}"
                )
                self.error_count += 1
                return
            
            # Google Books APIから書籍情報を取得
            logger.info(f"Fetching book info for ISBN: {isbn}")
            book_info = self.books_client.get_book_info_by_isbn(isbn)
            
            if not book_info:
                logger.error(f"Application #{application_number}: Book not found for ISBN: {isbn}")
                self._record_error(
                    application_number=application_number,
                    isbn=isbn,
                    error_type="BOOK_NOT_FOUND",
                    error_message=f"Book information not found for ISBN: {isbn}"
                )
                self.error_count += 1
                return
            
            # DBに書籍を登録（重複チェック付き）
            book, is_created = self._create_book(row_data, book_info)
            
            if is_created:
                logger.info(f"Successfully created book: {book.title} (ID: {book.id})")
                self.success_count += 1
            else:
                logger.info(f"Book already exists, skipping: {book.title} (ID: {book.id})")
                self.skip_count += 1
            
            # スプレッドシートにフラグを立てる
            self.sheets_client.mark_as_imported(row_index)
            logger.info(f"Marked row {row_index} as imported")
            
        except Exception as e:
            logger.error(f"Failed to process row {row_index}: {str(e)}")
            self._record_error(
                application_number=application_number,
                isbn=isbn,
                error_type="PROCESSING_ERROR",
                error_message=f"Failed to process row: {str(e)}"
            )
            self.error_count += 1
    
    def _create_book(self, row_data: Dict[str, Any], book_info: Dict[str, Any]) -> Tuple[Book, bool]:
        """
        書籍をDBに登録（重複チェック付き）
        
        Args:
            row_data: スプレッドシートの行データ
            book_info: Google Books APIから取得した書籍情報
        
        Returns:
            (Bookオブジェクト, 新規作成されたかどうか)
        """
        application_number = row_data.get('application_number', '')
        
        # 申請番号での重複チェック
        existing_book = Book.objects.filter(application_number=application_number).first()
        if existing_book:
            logger.warning(f"Book with application number {application_number} already exists (ID: {existing_book.id}), skipping")
            return existing_book, False
        
        # 価格の処理（文字列から数値に変換）
        price_str = row_data.get('price', '0')
        try:
            # カンマを除去して数値に変換
            price = float(price_str.replace(',', '')) if price_str else 0
        except (ValueError, AttributeError):
            price = 0
            logger.warning(f"Invalid price format: {price_str}, set to 0")
        
        # Bookオブジェクト作成
        book = Book.objects.create(
            # 申請情報
            application_number=row_data.get('application_number', ''),
            applicant_name=row_data.get('applicant_name', ''),
            approver_name=row_data.get('approver_name', ''),
            application_date=row_data.get('application_date', ''),
            approval_date=row_data.get('approval_date', ''),
            price=price,
            
            # 書籍情報
            isbn=row_data.get('isbn', ''),
            title=book_info.get('title', ''),
            author=book_info.get('author', ''),
            publisher=book_info.get('publisher', ''),
            published_date=book_info.get('published_date', ''),
            description=book_info.get('description', ''),
            thumbnail_url=book_info.get('thumbnail_url', ''),
            
            # 初期ステータス
            status='ordered',
        )
        
        return book, True
    
    def _record_error(
        self,
        application_number: str = None,
        isbn: str = None,
        error_type: str = '',
        error_message: str = ''
    ) -> None:
        """
        エラーログをDBに記録
        
        Args:
            application_number: 申請番号
            isbn: ISBNコード
            error_type: エラー種別
            error_message: エラーメッセージ
        """
        try:
            ErrorLog.objects.create(
                application_number=application_number,
                isbn=isbn,
                error_type=error_type,
                error_message=error_message
            )
            logger.info(f"Error log recorded: {error_type}")
        except Exception as e:
            logger.error(f"Failed to record error log: {str(e)}")


class Command(BaseCommand):
    help = 'Import approved book applications from Google Sheets'
    
    def add_arguments(self, parser):
        """コマンドライン引数の追加"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run mode (no DB updates)',
        )
    
    def handle(self, *args, **options):
        """コマンド実行"""
        self.stdout.write(self.style.SUCCESS('Starting book import batch...'))
        
        # dry-runモードの場合は警告
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write(self.style.ERROR('Dry run mode not implemented yet'))
            return
        
        # バッチ処理実行
        try:
            batch = BookImportBatch()
            success, error, skip = batch.process()
            
            # 結果表示
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 50))
            self.stdout.write(self.style.SUCCESS('Batch completed'))
            self.stdout.write(self.style.SUCCESS(f'Success: {success}'))
            
            if error > 0:
                self.stdout.write(self.style.ERROR(f'Error: {error}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Error: {error}'))
            
            if skip > 0:
                self.stdout.write(self.style.WARNING(f'Skip: {skip}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Skip: {skip}'))
            
            self.stdout.write(self.style.SUCCESS('=' * 50))
            
            # エラーがある場合は終了コード1
            if error > 0:
                self.stdout.write(self.style.ERROR('Batch completed with errors'))
            else:
                self.stdout.write(self.style.SUCCESS('Batch completed successfully'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Batch failed: {str(e)}'))
            raise
