"""
Google Sheets API 疎通確認コマンド

Usage:
    python manage.py test_sheets_connection
"""

from django.core.management.base import BaseCommand
from books.utils.google_sheets_client import GoogleSheetsClient
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Google Sheets API connection'
    
    def handle(self, *args, **options):
        """コマンド実行"""
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Google Sheets API 疎通確認テスト'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        
        # 設定確認
        self.stdout.write(self.style.WARNING('【設定確認】'))
        api_key = getattr(settings, 'GOOGLE_SHEETS_API_KEY', '')
        spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        
        if api_key:
            masked_key = api_key[:10] + '...' + api_key[-5:] if len(api_key) > 15 else '***'
            self.stdout.write(f'API Key: {masked_key}')
        else:
            self.stdout.write(self.style.ERROR('API Key: Not set'))
        
        self.stdout.write(f'Spreadsheet ID: {spreadsheet_id}')
        self.stdout.write('')
        
        if not api_key or not spreadsheet_id:
            self.stdout.write(self.style.ERROR('エラー: APIキーまたはスプレッドシートIDが設定されていません'))
            return
        
        # 接続テスト
        self.stdout.write(self.style.WARNING('【接続テスト】'))
        try:
            # クライアント初期化
            client = GoogleSheetsClient()
            self.stdout.write('✓ クライアント初期化成功')
            
            # 認証
            client.authenticate()
            self.stdout.write('✓ 認証成功')
            
            # データ取得テスト
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('【データ取得テスト】'))
            rows = client.get_all_rows(sheet_name='Sheet1', start_row=2)
            
            self.stdout.write(f'✓ データ取得成功: {len(rows)}行')
            self.stdout.write('')
            
            # データの一部を表示
            if rows:
                self.stdout.write(self.style.WARNING('【取得データサンプル（最大5行）】'))
                for idx, row in enumerate(rows[:5], start=2):
                    # 行の長さを9列に調整
                    if len(row) < 9:
                        row.extend([''] * (9 - len(row)))
                    
                    self.stdout.write(f'行{idx}:')
                    self.stdout.write(f'  申請番号: {row[0]}')
                    self.stdout.write(f'  申請者名: {row[1]}')
                    self.stdout.write(f'  承認者名: {row[2]}')
                    self.stdout.write(f'  申請日: {row[3]}')
                    self.stdout.write(f'  承認日: {row[4]}')
                    self.stdout.write(f'  書籍名: {row[5]}')
                    self.stdout.write(f'  ISBNコード: {row[6]}')
                    self.stdout.write(f'  価格: {row[7]}')
                    self.stdout.write(f'  DB取り込み済み: {row[8]}')
                    self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('データが空です'))
            
            # 取り込み対象データの確認
            self.stdout.write(self.style.WARNING('【取り込み対象データ】'))
            pending_rows = client.get_pending_rows()
            self.stdout.write(f'✓ 取り込み対象行数: {len(pending_rows)}行')
            
            if pending_rows:
                self.stdout.write('')
                self.stdout.write('【取り込み対象データサンプル（最大3行）】')
                for row in pending_rows[:3]:
                    self.stdout.write(f'行{row["row_index"]}:')
                    self.stdout.write(f'  申請番号: {row["application_number"]}')
                    self.stdout.write(f'  申請者名: {row["applicant_name"]}')
                    self.stdout.write(f'  承認者名: {row["approver_name"]}')
                    self.stdout.write(f'  書籍名: {row["book_name"]}')
                    self.stdout.write(f'  ISBNコード: {row["isbn"]}')
                    self.stdout.write('')
            
            # 成功メッセージ
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('疎通確認テスト成功！'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            
        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write(self.style.ERROR('疎通確認テスト失敗'))
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write(self.style.ERROR(f'エラー: {str(e)}'))
            self.stdout.write('')
            
            # デバッグ情報
            import traceback
            self.stdout.write(self.style.ERROR('【詳細エラー情報】'))
            self.stdout.write(traceback.format_exc())
            raise

