from django.db import models
from django.utils import timezone


class Book(models.Model):
    """書籍マスタ"""
    
    STATUS_CHOICES = [
        ('ordered', '購入中'),
        ('available', '本棚保管中'),
        ('rented', '貸出中'),
        ('other', 'その他'),
    ]
    
    # 申請情報
    application_number = models.CharField('申請番号', max_length=50)
    applicant_name = models.CharField('申請者名', max_length=100)
    approver_name = models.CharField('承認者名', max_length=100)
    application_date = models.CharField('申請日', max_length=10)  # YYYY/MM/DD形式
    approval_date = models.CharField('承認日', max_length=10)  # YYYY/MM/DD形式
    price = models.DecimalField('価格', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 書籍情報
    isbn = models.CharField('ISBNコード', max_length=20)
    title = models.CharField('書籍名', max_length=255, blank=True, null=True)
    author = models.CharField('著者', max_length=255, blank=True, null=True)
    publisher = models.CharField('出版社', max_length=255, blank=True, null=True)
    published_date = models.CharField('出版日', max_length=50, blank=True, null=True)
    description = models.TextField('書籍概要', blank=True, null=True)
    thumbnail_url = models.CharField('書影URL', max_length=512, blank=True, null=True)
    
    # 管理情報
    status = models.CharField('ステータス', max_length=10, choices=STATUS_CHOICES, default='ordered')
    location = models.CharField('保管場所', max_length=255, blank=True, null=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = '書籍'
        verbose_name_plural = '書籍'
        indexes = [
            models.Index(fields=['isbn'], name='idx_isbn'),
            models.Index(fields=['status'], name='idx_status'),
            models.Index(fields=['application_number'], name='idx_application_number'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.isbn})"
    
    def get_current_borrower(self):
        """現在の貸出人を取得"""
        if self.status == 'rented':
            current_rental = self.rental_history.filter(actual_return_date__isnull=True).first()
            if current_rental:
                return current_rental.borrower_name
        return None


class RentalHistory(models.Model):
    """貸出履歴"""
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='rental_history', verbose_name='書籍')
    borrower_name = models.CharField('貸出人名', max_length=100)
    rental_date = models.DateField('貸出日')
    expected_return_date = models.DateField('返却予定日')
    actual_return_date = models.DateField('実際の返却日', null=True, blank=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'rental_history'
        verbose_name = '貸出履歴'
        verbose_name_plural = '貸出履歴'
        indexes = [
            models.Index(fields=['book'], name='idx_book_id'),
            models.Index(fields=['borrower_name'], name='idx_borrower_name'),
            models.Index(fields=['rental_date'], name='idx_rental_date'),
        ]
        ordering = ['-rental_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.borrower_name} ({self.rental_date})"
    
    def is_overdue(self):
        """延滞しているかどうか"""
        if not self.actual_return_date:
            from datetime import date
            return date.today() > self.expected_return_date
        return False


class ErrorLog(models.Model):
    """エラーログ"""
    
    application_number = models.CharField('申請番号', max_length=50, blank=True, null=True)
    isbn = models.CharField('ISBNコード', max_length=20, blank=True, null=True)
    error_type = models.CharField('エラー種別', max_length=50)
    error_message = models.TextField('エラーメッセージ')
    created_at = models.DateTimeField('発生日時', default=timezone.now)
    
    class Meta:
        db_table = 'error_logs'
        verbose_name = 'エラーログ'
        verbose_name_plural = 'エラーログ'
        indexes = [
            models.Index(fields=['created_at'], name='idx_created_at'),
            models.Index(fields=['application_number'], name='idx_error_application_number'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.error_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
