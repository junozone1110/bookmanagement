"""
Google Sheets API クライアント

スプレッドシートから申請データを取得し、フラグを書き戻すクライアントクラス
"""

import os
import logging
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Google Sheets API クライアント"""
    
    # APIスコープ
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # スプレッドシート列の定義（A列=0, B列=1, ...）
    COL_APPLICATION_NUMBER = 0  # A列: 申請番号
    COL_APPLICANT_NAME = 1      # B列: 申請者名
    COL_APPROVER_NAME = 2       # C列: 承認者名
    COL_APPLICATION_DATE = 3    # D列: 申請日
    COL_APPROVAL_DATE = 4       # E列: 承認日
    COL_BOOK_NAME = 5           # F列: 書籍名
    COL_ISBN = 6                # G列: ISBNコード
    COL_PRICE = 7               # H列: 価格
    COL_DB_IMPORTED = 8         # I列: DB取り込み済み
    
    def __init__(self, api_key: Optional[str] = None, credentials_path: Optional[str] = None, spreadsheet_id: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Google Sheets API キー（読み取り専用、省略時は設定から取得）
            credentials_path: 認証情報ファイルのパス（書き込み用、省略時は設定から取得）
            spreadsheet_id: スプレッドシートID（省略時は設定から取得）
        """
        self.api_key = api_key or getattr(settings, 'GOOGLE_SHEETS_API_KEY', None)
        self.credentials_path = credentials_path or settings.GOOGLE_SHEETS_CREDENTIALS_PATH
        self.spreadsheet_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.service = None
        self.use_api_key = bool(self.api_key)
    
    def authenticate(self):
        """Google Sheets APIに認証"""
        try:
            if self.use_api_key and self.api_key:
                # APIキーを使用した認証（読み取り専用）
                self.service = build('sheets', 'v4', developerKey=self.api_key)
                logger.info("Successfully authenticated with Google Sheets API using API key")
            else:
                # サービスアカウントを使用した認証（読み書き可能）
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
                
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Successfully authenticated with Google Sheets API using service account")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets API: {str(e)}")
            raise
    
    def get_all_rows(self, sheet_name: str = 'Sheet1', start_row: int = 2) -> List[List[Any]]:
        """
        スプレッドシートから全行を取得
        
        Args:
            sheet_name: シート名
            start_row: 開始行番号（1始まり、デフォルトは2行目＝ヘッダー除外）
        
        Returns:
            行データのリスト
        """
        try:
            if not self.service:
                self.authenticate()
            
            # データ範囲を指定（例: Sheet1!A2:I）
            range_name = f"{sheet_name}!A{start_row}:I"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            logger.info(f"Fetched {len(rows)} rows from spreadsheet")
            
            return rows
            
        except HttpError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch rows from spreadsheet: {str(e)}")
            raise
    
    def get_pending_rows(self, sheet_name: str = 'Sheet1') -> List[Dict[str, Any]]:
        """
        取り込み対象の行を取得（承認済み＆未取り込み）
        
        取り込み条件:
        - 承認者名（C列）が入力されている
        - 承認日（E列）が入力されている
        - DB取り込み済みフラグ（I列）が空
        
        Args:
            sheet_name: シート名
        
        Returns:
            取り込み対象行の辞書のリスト
            各辞書には行データ + row_index（実際の行番号）が含まれる
        """
        try:
            all_rows = self.get_all_rows(sheet_name)
            pending_rows = []
            
            for idx, row in enumerate(all_rows, start=2):  # 2行目から開始（ヘッダー除く）
                # 行の長さチェック（少なくとも9列必要）
                if len(row) < 9:
                    row.extend([''] * (9 - len(row)))  # 足りない列を空文字で埋める
                
                # 取り込み条件チェック
                approver_name = row[self.COL_APPROVER_NAME].strip() if len(row) > self.COL_APPROVER_NAME else ''
                approval_date = row[self.COL_APPROVAL_DATE].strip() if len(row) > self.COL_APPROVAL_DATE else ''
                db_imported = row[self.COL_DB_IMPORTED].strip() if len(row) > self.COL_DB_IMPORTED else ''
                
                if approver_name and approval_date and not db_imported:
                    pending_rows.append({
                        'row_index': idx,
                        'application_number': row[self.COL_APPLICATION_NUMBER],
                        'applicant_name': row[self.COL_APPLICANT_NAME],
                        'approver_name': approver_name,
                        'application_date': row[self.COL_APPLICATION_DATE],
                        'approval_date': approval_date,
                        'book_name': row[self.COL_BOOK_NAME],
                        'isbn': row[self.COL_ISBN],
                        'price': row[self.COL_PRICE],
                    })
            
            logger.info(f"Found {len(pending_rows)} pending rows")
            return pending_rows
            
        except Exception as e:
            logger.error(f"Failed to get pending rows: {str(e)}")
            raise
    
    def mark_as_imported(self, row_index: int, sheet_name: str = 'Sheet1', value: str = '✓'):
        """
        指定行にDB取り込み済みフラグを立てる
        
        Args:
            row_index: 行番号（1始まり）
            sheet_name: シート名
            value: 書き込む値（デフォルト: ✓）
        """
        try:
            if not self.service:
                self.authenticate()
            
            # I列（9列目）にフラグを書き込む
            range_name = f"{sheet_name}!I{row_index}"
            
            body = {
                'values': [[value]]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Marked row {row_index} as imported")
            
        except HttpError as e:
            logger.error(f"HTTP error occurred while marking row {row_index}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to mark row {row_index} as imported: {str(e)}")
            raise

