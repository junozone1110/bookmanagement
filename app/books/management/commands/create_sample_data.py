"""
サンプルデータ作成コマンド

Usage:
    python manage.py create_sample_data
    python manage.py create_sample_data --clear  # 既存データを削除してから作成
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from books.models import Book, RentalHistory, ErrorLog


class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Book.objects.all().delete()
            RentalHistory.objects.all().delete()
            ErrorLog.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))
        
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # サンプル書籍データ
        sample_books = [
            {
                'application_number': 'APP-2024-001',
                'applicant_name': '山田太郎',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/01',
                'approval_date': '2024/10/02',
                'price': 3960,
                'isbn': '9784798121963',
                'title': 'エリック・エヴァンスのドメイン駆動設計',
                'author': 'Eric Evans, 和智右桂, 牧野祐子',
                'publisher': '翔泳社',
                'published_date': '2011-04-09',
                'description': 'ドメイン駆動設計の古典的名著。複雑なソフトウェア開発における設計とモデリングの技法を解説。',
                'thumbnail_url': 'http://books.google.com/books/content?id=qOKJzgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
                'status': 'available',
                'location': '本棚A-1',
            },
            {
                'application_number': 'APP-2024-002',
                'applicant_name': '鈴木花子',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/03',
                'approval_date': '2024/10/03',
                'price': 3080,
                'isbn': '9784873119038',
                'title': 'リーダブルコード',
                'author': 'Dustin Boswell, Trevor Foucher, 角征典',
                'publisher': "O'Reilly Media",
                'published_date': '2012-06-23',
                'description': '読みやすいコードを書くための実践的なテクニック集。コードの可読性を高める様々な手法を紹介。',
                'thumbnail_url': 'http://books.google.com/books/content?id=51wqAAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api',
                'status': 'rented',
                'location': '本棚A-2',
            },
            {
                'application_number': 'APP-2024-003',
                'applicant_name': '田中一郎',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/05',
                'approval_date': '2024/10/06',
                'price': 2970,
                'isbn': '9784297114688',
                'title': 'Python実践入門',
                'author': '有山圭二, 横山信弘',
                'publisher': '技術評論社',
                'published_date': '2020-10-08',
                'description': 'Pythonの基本から実践的な開発手法まで、体系的に学べる入門書。',
                'thumbnail_url': 'http://books.google.com/books/content?id=example&printsec=frontcover&img=1&zoom=1&source=gbs_api',
                'status': 'available',
                'location': '本棚B-1',
            },
            {
                'application_number': 'APP-2024-004',
                'applicant_name': '佐々木美咲',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/08',
                'approval_date': '2024/10/09',
                'price': 3520,
                'isbn': '9784873119755',
                'title': 'プログラマのためのSQL 第4版',
                'author': 'Joe Celko, ミック',
                'publisher': "O'Reilly Media",
                'published_date': '2015-03',
                'description': 'SQLの実践的な使い方とベストプラクティスを解説。データベース設計とクエリ最適化の技法。',
                'thumbnail_url': '',
                'status': 'available',
                'location': '本棚B-2',
            },
            {
                'application_number': 'APP-2024-005',
                'applicant_name': '高橋健太',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/10',
                'approval_date': '2024/10/10',
                'price': 4180,
                'isbn': '9784297124021',
                'title': 'Clean Architecture 達人に学ぶソフトウェアの構造と設計',
                'author': 'Robert C. Martin, 角征典, 髙木正弘',
                'publisher': 'KADOKAWA',
                'published_date': '2018-07-27',
                'description': 'アーキテクチャの原理原則を解説。良いソフトウェア設計のための基本概念と実践手法。',
                'thumbnail_url': '',
                'status': 'ordered',
                'location': '',
            },
            {
                'application_number': 'APP-2024-006',
                'applicant_name': '伊藤直樹',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/12',
                'approval_date': '2024/10/13',
                'price': 3300,
                'isbn': '9784873119700',
                'title': 'Webを支える技術',
                'author': '山本陽平',
                'publisher': '技術評論社',
                'published_date': '2010-04-08',
                'description': 'HTTP、URI、HTMLなど、Webの基本技術を体系的に解説。REST、リソース指向の設計手法も紹介。',
                'thumbnail_url': '',
                'status': 'available',
                'location': '本棚C-1',
            },
            {
                'application_number': 'APP-2024-007',
                'applicant_name': '中村優子',
                'approver_name': '佐藤次郎',
                'application_date': '2024/10/14',
                'approval_date': '2024/10/14',
                'price': 2860,
                'isbn': '9784297133610',
                'title': 'Git実践入門',
                'author': '大塚弘記',
                'publisher': '技術評論社',
                'published_date': '2023-03-09',
                'description': 'Gitの基本から高度な使い方まで、実践的なワークフローを解説。',
                'thumbnail_url': '',
                'status': 'rented',
                'location': '本棚C-2',
            },
        ]
        
        created_books = []
        for book_data in sample_books:
            book = Book.objects.create(**book_data)
            created_books.append(book)
            self.stdout.write(f'  ✓ Created: {book.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\n{len(created_books)} books created'))
        
        # 貸出履歴のサンプルデータ
        self.stdout.write('\nCreating rental history...')
        
        # 「リーダブルコード」の貸出履歴（現在貸出中）
        readable_code = Book.objects.get(isbn='9784873119038')
        RentalHistory.objects.create(
            book=readable_code,
            borrower_name='小林誠',
            rental_date=datetime.now().date() - timedelta(days=7),
            expected_return_date=datetime.now().date() + timedelta(days=7),
            actual_return_date=None,
        )
        self.stdout.write('  ✓ Created rental for: リーダブルコード (現在貸出中)')
        
        # 「リーダブルコード」の過去の貸出履歴
        RentalHistory.objects.create(
            book=readable_code,
            borrower_name='山田太郎',
            rental_date=datetime.now().date() - timedelta(days=60),
            expected_return_date=datetime.now().date() - timedelta(days=46),
            actual_return_date=datetime.now().date() - timedelta(days=45),
        )
        self.stdout.write('  ✓ Created past rental for: リーダブルコード')
        
        # 「Git実践入門」の貸出履歴（現在貸出中）
        git_book = Book.objects.get(isbn='9784297133610')
        RentalHistory.objects.create(
            book=git_book,
            borrower_name='鈴木花子',
            rental_date=datetime.now().date() - timedelta(days=3),
            expected_return_date=datetime.now().date() + timedelta(days=11),
            actual_return_date=None,
        )
        self.stdout.write('  ✓ Created rental for: Git実践入門 (現在貸出中)')
        
        # 「エリック・エヴァンスのドメイン駆動設計」の過去の貸出履歴
        ddd_book = Book.objects.get(isbn='9784798121963')
        RentalHistory.objects.create(
            book=ddd_book,
            borrower_name='田中一郎',
            rental_date=datetime.now().date() - timedelta(days=30),
            expected_return_date=datetime.now().date() - timedelta(days=16),
            actual_return_date=datetime.now().date() - timedelta(days=14),
        )
        RentalHistory.objects.create(
            book=ddd_book,
            borrower_name='佐々木美咲',
            rental_date=datetime.now().date() - timedelta(days=90),
            expected_return_date=datetime.now().date() - timedelta(days=76),
            actual_return_date=datetime.now().date() - timedelta(days=75),
        )
        self.stdout.write('  ✓ Created past rentals for: ドメイン駆動設計')
        
        self.stdout.write(self.style.SUCCESS('\nRental history created'))
        
        # エラーログのサンプルデータ
        self.stdout.write('\nCreating error logs...')
        
        ErrorLog.objects.create(
            application_number='APP-2024-999',
            isbn='9999999999999',
            error_type='BOOK_NOT_FOUND',
            error_message='Book information not found for ISBN: 9999999999999',
        )
        self.stdout.write('  ✓ Created error log: BOOK_NOT_FOUND')
        
        ErrorLog.objects.create(
            application_number='APP-2024-998',
            isbn='123',
            error_type='INVALID_ISBN',
            error_message='Invalid ISBN format: 123',
        )
        self.stdout.write('  ✓ Created error log: INVALID_ISBN')
        
        self.stdout.write(self.style.SUCCESS('\nError logs created'))
        
        # サマリー
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Books: {Book.objects.count()}')
        self.stdout.write(f'  - ordered: {Book.objects.filter(status="ordered").count()}')
        self.stdout.write(f'  - available: {Book.objects.filter(status="available").count()}')
        self.stdout.write(f'  - rented: {Book.objects.filter(status="rented").count()}')
        self.stdout.write(f'Rental History: {RentalHistory.objects.count()}')
        self.stdout.write(f'Error Logs: {ErrorLog.objects.count()}')
        self.stdout.write('')
        self.stdout.write('Access admin panel at: http://localhost:8001/admin/')

