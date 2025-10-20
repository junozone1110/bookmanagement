from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils.google_books_client import GoogleBooksClient
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def fetch_book_info(request):
    """
    ISBNから書籍情報を取得するAPIエンドポイント
    
    GET /books/api/fetch-book-info/?isbn=9784873115658
    """
    isbn = request.GET.get('isbn', '').strip()
    
    if not isbn:
        return JsonResponse({
            'success': False,
            'error': 'ISBNコードを入力してください'
        }, status=400)
    
    try:
        # Google Books APIクライアント初期化
        client = GoogleBooksClient()
        
        # ISBN妥当性チェック
        if not client.validate_isbn(isbn):
            return JsonResponse({
                'success': False,
                'error': 'ISBNコードの形式が正しくありません（10桁または13桁の数字）'
            }, status=400)
        
        # 書籍情報取得
        book_info = client.get_book_info_by_isbn(isbn)
        
        if book_info:
            return JsonResponse({
                'success': True,
                'data': {
                    'title': book_info.get('title', ''),
                    'author': book_info.get('author', ''),
                    'publisher': book_info.get('publisher', ''),
                    'published_date': book_info.get('published_date', ''),
                    'description': book_info.get('description', ''),
                    'thumbnail_url': book_info.get('thumbnail_url', ''),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'このISBNコードの書籍情報が見つかりませんでした'
            }, status=404)
            
    except Exception as e:
        logger.error(f'Error fetching book info for ISBN {isbn}: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'書籍情報の取得中にエラーが発生しました: {str(e)}'
        }, status=500)
