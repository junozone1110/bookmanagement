"""
Google Books API クライアント

ISBNコードをキーに書籍情報を取得するクライアントクラス
"""

import requests
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleBooksClient:
    """Google Books API クライアント"""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Google Books API キー（省略時は設定から取得）
        """
        self.api_key = api_key or settings.GOOGLE_BOOKS_API_KEY
    
    def get_book_info_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        ISBNコードから書籍情報を取得
        
        Args:
            isbn: ISBNコード（10桁または13桁）
        
        Returns:
            書籍情報の辞書、取得失敗時はNone
            {
                'title': 書籍名,
                'author': 著者,
                'publisher': 出版社,
                'published_date': 出版日,
                'description': 書籍概要,
                'thumbnail_url': 書影URL
            }
        """
        try:
            # クエリパラメータ設定
            params = {
                'q': f'isbn:{isbn}',
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            # APIリクエスト
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # レスポンスチェック
            if 'items' not in data or len(data['items']) == 0:
                logger.warning(f"Book not found for ISBN: {isbn}")
                return None
            
            # 最初のアイテムから書籍情報を抽出
            volume_info = data['items'][0].get('volumeInfo', {})
            
            # 書影URLを取得してHTTPSに変換
            thumbnail_url = volume_info.get('imageLinks', {}).get('thumbnail', '')
            if thumbnail_url and thumbnail_url.startswith('http://'):
                thumbnail_url = thumbnail_url.replace('http://', 'https://')
            
            book_info = {
                'title': volume_info.get('title', ''),
                'author': ', '.join(volume_info.get('authors', [])),
                'publisher': volume_info.get('publisher', ''),
                'published_date': volume_info.get('publishedDate', ''),
                'description': volume_info.get('description', ''),
                'thumbnail_url': thumbnail_url,
            }
            
            logger.info(f"Successfully fetched book info for ISBN: {isbn}")
            return book_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for ISBN {isbn}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching book info for ISBN {isbn}: {str(e)}")
            return None
    
    def validate_isbn(self, isbn: str) -> bool:
        """
        ISBNコードの妥当性チェック
        
        Args:
            isbn: ISBNコード
        
        Returns:
            妥当な場合True
        """
        # ハイフンを除去
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        
        # 長さチェック（10桁または13桁）
        if len(isbn_clean) not in [10, 13]:
            return False
        
        # 数字のみかチェック（ISBN-10の場合は最後がXの可能性あり）
        if len(isbn_clean) == 10:
            return isbn_clean[:-1].isdigit() and (isbn_clean[-1].isdigit() or isbn_clean[-1].upper() == 'X')
        else:
            return isbn_clean.isdigit()

