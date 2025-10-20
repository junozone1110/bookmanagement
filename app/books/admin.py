from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import Book, RentalHistory, ErrorLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_image', 'title_with_status', 'author', 'isbn', 'status_badge', 'current_borrower', 'location', 'created_at']
    list_filter = ['status', 'application_date', 'approval_date', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'application_number', 'applicant_name', 'approver_name']
    readonly_fields = ['created_at', 'updated_at', 'thumbnail_preview']
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('書籍情報', {
            'fields': ('isbn', 'title', 'author', 'publisher', 'published_date', 'description', 'thumbnail_url', 'thumbnail_preview'),
            'description': 'ISBNコードを入力後、「ISBNから書籍情報を取得」ボタンをクリックすると自動入力されます。'
        }),
        ('申請・承認情報', {
            'fields': ('application_number', 'applicant_name', 'approver_name', 'application_date', 'approval_date', 'price'),
        }),
        ('管理情報', {
            'fields': ('status', 'location')
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def _get_secure_thumbnail_url(self, url):
        """書影URLをHTTPSに変換"""
        if url and url.startswith('http://'):
            return url.replace('http://', 'https://')
        return url
    
    def thumbnail_image(self, obj):
        """一覧画面用の書影サムネイル"""
        if obj.thumbnail_url:
            secure_url = self._get_secure_thumbnail_url(obj.thumbnail_url)
            return format_html(
                '<img src="{}" style="width: 40px; height: 60px; object-fit: cover;" />',
                secure_url
            )
        return format_html('<div style="width: 40px; height: 60px; background: #ddd; display: flex; align-items: center; justify-content: center; font-size: 10px;">No Image</div>')
    thumbnail_image.short_description = '書影'
    
    def thumbnail_preview(self, obj):
        """詳細画面用の書影プレビュー"""
        if obj.thumbnail_url:
            secure_url = self._get_secure_thumbnail_url(obj.thumbnail_url)
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 300px;" />',
                secure_url
            )
        return 'なし'
    thumbnail_preview.short_description = '書影プレビュー'
    
    def title_with_status(self, obj):
        """書籍名とステータスアイコン"""
        return format_html(
            '<strong>{}</strong>',
            obj.title
        )
    title_with_status.short_description = '書籍名'
    title_with_status.admin_order_field = 'title'
    
    def status_badge(self, obj):
        """ステータスバッジ - Cursorコンソールスタイル"""
        colors = {
            'ordered': '#f0ad4e',    # オレンジ
            'available': '#5cb85c',  # グリーン
            'rented': '#2c3e50',     # ダークグレー
            'other': '#999999',      # グレー
        }
        labels = {
            'ordered': '購入中',
            'available': '本棚保管中',
            'rented': '貸出中',
            'other': 'その他',
        }
        color = colors.get(obj.status, '#999999')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 3px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            label
        )
    status_badge.short_description = 'ステータス'
    status_badge.admin_order_field = 'status'
    
    def current_borrower(self, obj):
        """現在の貸出人 - Cursorコンソールスタイル"""
        if obj.status == 'rented':
            borrower = obj.get_current_borrower()
            if borrower:
                return format_html(
                    '<span style="background-color: #2c3e50; color: white; padding: 5px 12px; border-radius: 3px; font-size: 12px; font-weight: 600;">👤 {}</span>',
                    borrower
                )
        return format_html('<span style="color: #999;">-</span>')
    current_borrower.short_description = '貸出人'


@admin.register(RentalHistory)
class RentalHistoryAdmin(admin.ModelAdmin):
    list_display = ['book_with_status', 'borrower_badge', 'rental_date', 'expected_return_date', 'actual_return_date', 'overdue_badge']
    list_filter = ['rental_date', 'expected_return_date', 'actual_return_date']
    search_fields = ['book__title', 'borrower_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'rental_date'
    list_per_page = 20
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('貸出情報', {
            'fields': ('book', 'borrower_name', 'rental_date', 'expected_return_date', 'actual_return_date')
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def book_with_status(self, obj):
        """書籍名と現在の貸出状況 - Cursorコンソールスタイル"""
        if obj.actual_return_date:
            status_icon = '✓'
            status_color = '#5cb85c'  # グリーン
            status_text = '返却済み'
        else:
            status_icon = '📖'
            status_color = '#f0ad4e'  # オレンジ
            status_text = '貸出中'
        return format_html(
            '<span style="color: {};"><strong>{}</strong> {}</span><br/><small style="color: #000;">{}</small>',
            status_color,
            status_icon,
            status_text,
            obj.book.title
        )
    book_with_status.short_description = '書籍'
    book_with_status.admin_order_field = 'book'
    
    def borrower_badge(self, obj):
        """貸出人バッジ - Cursorコンソールスタイル"""
        return format_html(
            '<span style="background-color: #2c3e50; color: white; padding: 5px 12px; border-radius: 3px; font-size: 12px; font-weight: 600;">👤 {}</span>',
            obj.borrower_name
        )
    borrower_badge.short_description = '貸出人'
    borrower_badge.admin_order_field = 'borrower_name'
    
    def overdue_badge(self, obj):
        """延滞バッジ - Cursorコンソールスタイル"""
        if obj.is_overdue():
            from datetime import date
            overdue_days = (date.today() - obj.expected_return_date).days
            return format_html(
                '<span style="background-color: #d9534f; color: white; padding: 5px 12px; border-radius: 3px; font-size: 12px; font-weight: 600;">⚠ {}日延滞</span>',
                overdue_days
            )
        elif not obj.actual_return_date:
            return format_html(
                '<span style="color: #5cb85c; font-size: 12px; font-weight: 600;">✓ 期限内</span>'
            )
        else:
            return format_html(
                '<span style="color: #999; font-size: 12px;">-</span>'
            )
    overdue_badge.short_description = '延滞状況'


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['error_type_badge', 'application_number', 'isbn', 'error_message_short', 'created_at']
    list_filter = ['error_type', 'created_at']
    search_fields = ['application_number', 'isbn', 'error_message']
    readonly_fields = ['application_number', 'isbn', 'error_type', 'error_message', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('エラー情報', {
            'fields': ('error_type', 'error_message')
        }),
        ('関連情報', {
            'fields': ('application_number', 'isbn')
        }),
        ('発生日時', {
            'fields': ('created_at',)
        }),
    )
    
    def error_type_badge(self, obj):
        """エラー種別バッジ - Cursorコンソールスタイル"""
        colors = {
            'INITIALIZATION_ERROR': '#d9534f',  # レッド（重大エラー）
            'INVALID_ISBN': '#f0ad4e',          # オレンジ
            'BOOK_NOT_FOUND': '#f0ad4e',        # オレンジ
            'PROCESSING_ERROR': '#d9534f',      # レッド（重大エラー）
            'BATCH_ERROR': '#d9534f',           # レッド（重大エラー）
        }
        color = colors.get(obj.error_type, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 3px; font-size: 12px; font-weight: 600;">⚠ {}</span>',
            color,
            obj.error_type
        )
    error_type_badge.short_description = 'エラー種別'
    error_type_badge.admin_order_field = 'error_type'
    
    def error_message_short(self, obj):
        """エラーメッセージ（短縮版）"""
        if len(obj.error_message) > 100:
            return format_html(
                '<span title="{}">{}</span>',
                obj.error_message,
                obj.error_message[:100] + '...'
            )
        return obj.error_message
    error_message_short.short_description = 'エラーメッセージ'
    
    def has_add_permission(self, request):
        """追加権限を無効化（システムが自動作成するため）"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """変更権限を無効化（読み取り専用）"""
        return False
