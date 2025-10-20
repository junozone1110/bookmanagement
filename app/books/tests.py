"""
書籍管理システムのテストモジュール
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from .models import Book, RentalHistory, ErrorLog
from .utils.google_books_client import GoogleBooksClient


class BookModelTests(TestCase):
    """書籍モデルのテスト"""
    
    def setUp(self):
        """テストデータのセットアップ"""
        self.book = Book.objects.create(
            application_number="TEST-001",
            applicant_name="テスト太郎",
            approver_name="承認次郎",
            application_date="2025/10/20",
            approval_date="2025/10/21",
            isbn="9784873115658",
            title="リーダブルコード",
            author="Dustin Boswell, Trevor Foucher",
            publisher="オライリー・ジャパン",
            status="available"
        )
    
    def test_create_book(self):
        """書籍作成のテスト"""
        self.assertEqual(self.book.title, "リーダブルコード")
        self.assertEqual(self.book.status, "available")
        self.assertEqual(self.book.isbn, "9784873115658")
    
    def test_book_str(self):
        """書籍の文字列表現のテスト"""
        expected = f"{self.book.title} ({self.book.isbn})"
        self.assertEqual(str(self.book), expected)
    
    def test_book_default_status(self):
        """書籍のデフォルトステータスのテスト"""
        new_book = Book.objects.create(
            application_number="TEST-002",
            isbn="9784873119038"
        )
        self.assertEqual(new_book.status, "ordered")
    
    def test_get_current_borrower_when_rented(self):
        """貸出中の場合の貸出人取得のテスト"""
        self.book.status = "rented"
        self.book.save()
        
        RentalHistory.objects.create(
            book=self.book,
            borrower_name="借りた太郎",
            rental_date=date.today(),
            expected_return_date=date.today() + timedelta(days=14)
        )
        
        borrower = self.book.get_current_borrower()
        self.assertEqual(borrower, "借りた太郎")
    
    def test_get_current_borrower_when_available(self):
        """保管中の場合の貸出人取得のテスト"""
        borrower = self.book.get_current_borrower()
        self.assertIsNone(borrower)
    
    def test_duplicate_application_number(self):
        """申請番号の重複チェックのテスト"""
        # 同じ申請番号の書籍を作成しようとする
        duplicate_exists = Book.objects.filter(
            application_number="TEST-001"
        ).exists()
        self.assertTrue(duplicate_exists)
        
        # 2件目を作成
        Book.objects.create(
            application_number="TEST-001-DUPLICATE",
            isbn="9784873119038"
        )
        
        # 2件になっていることを確認
        self.assertEqual(Book.objects.count(), 2)


class RentalHistoryModelTests(TestCase):
    """貸出履歴モデルのテスト"""
    
    def setUp(self):
        """テストデータのセットアップ"""
        self.book = Book.objects.create(
            application_number="TEST-001",
            isbn="9784873115658",
            title="テスト書籍",
            status="rented"
        )
        
        self.rental = RentalHistory.objects.create(
            book=self.book,
            borrower_name="テスト太郎",
            rental_date=date.today() - timedelta(days=20),
            expected_return_date=date.today() - timedelta(days=6)
        )
    
    def test_create_rental_history(self):
        """貸出履歴作成のテスト"""
        self.assertEqual(self.rental.borrower_name, "テスト太郎")
        self.assertIsNone(self.rental.actual_return_date)
    
    def test_is_overdue(self):
        """延滞判定のテスト"""
        self.assertTrue(self.rental.is_overdue())
    
    def test_is_not_overdue(self):
        """延滞していない場合のテスト"""
        future_rental = RentalHistory.objects.create(
            book=self.book,
            borrower_name="未来太郎",
            rental_date=date.today(),
            expected_return_date=date.today() + timedelta(days=14)
        )
        self.assertFalse(future_rental.is_overdue())
    
    def test_returned_book_not_overdue(self):
        """返却済みの場合は延滞なしのテスト"""
        self.rental.actual_return_date = date.today()
        self.rental.save()
        self.assertFalse(self.rental.is_overdue())
    
    def test_rental_history_str(self):
        """貸出履歴の文字列表現のテスト"""
        expected = f"{self.book.title} - {self.rental.borrower_name} ({self.rental.rental_date})"
        self.assertEqual(str(self.rental), expected)


class ErrorLogModelTests(TestCase):
    """エラーログモデルのテスト"""
    
    def test_create_error_log(self):
        """エラーログ作成のテスト"""
        error = ErrorLog.objects.create(
            application_number="TEST-001",
            isbn="9784873115658",
            error_type="INVALID_ISBN",
            error_message="ISBNの形式が不正です"
        )
        
        self.assertEqual(error.error_type, "INVALID_ISBN")
        self.assertIsNotNone(error.created_at)
    
    def test_error_log_str(self):
        """エラーログの文字列表現のテスト"""
        error = ErrorLog.objects.create(
            error_type="PROCESSING_ERROR",
            error_message="テストエラー"
        )
        
        expected = f"PROCESSING_ERROR - {error.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        self.assertEqual(str(error), expected)


class GoogleBooksClientTests(TestCase):
    """Google Books APIクライアントのテスト"""
    
    def setUp(self):
        """テストデータのセットアップ"""
        self.client = GoogleBooksClient()
    
    def test_validate_isbn_13_digits(self):
        """ISBN-13の妥当性チェックのテスト"""
        self.assertTrue(self.client.validate_isbn("9784873115658"))
    
    def test_validate_isbn_10_digits(self):
        """ISBN-10の妥当性チェックのテスト"""
        self.assertTrue(self.client.validate_isbn("4873115655"))
    
    def test_validate_isbn_with_hyphens(self):
        """ハイフン付きISBNの妥当性チェックのテスト"""
        self.assertTrue(self.client.validate_isbn("978-4-87311-565-8"))
    
    def test_validate_isbn_invalid(self):
        """不正なISBNの妥当性チェックのテスト"""
        self.assertFalse(self.client.validate_isbn("invalid"))
        self.assertFalse(self.client.validate_isbn("123"))
        self.assertFalse(self.client.validate_isbn(""))
    
    def test_validate_isbn_with_x(self):
        """ISBN-10でXを含む場合の妥当性チェックのテスト"""
        self.assertTrue(self.client.validate_isbn("123456789X"))


class BookAPIViewTests(TestCase):
    """書籍情報取得APIのテスト"""
    
    def test_fetch_book_info_no_isbn(self):
        """ISBNなしでのAPI呼び出しのテスト"""
        response = self.client.get('/books/api/fetch-book-info/')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('ISBN', data['error'])
    
    def test_fetch_book_info_invalid_isbn(self):
        """不正なISBNでのAPI呼び出しのテスト"""
        response = self.client.get('/books/api/fetch-book-info/?isbn=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('形式', data['error'])
