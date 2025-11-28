import flet as ft
import requests
import json

API_BASE_URL = "https://api.vrchat.cloud/api/1" 

def fetchFavoriteWorlds(authToken):

    if not authToken:
        print("デバッグ: authTokenが空です。")
        return None
    print(f"デバッグ: authTokenの長さ: {len(authToken)} (値は表示しません)")
        
    """認証トークンを使ってお気に入りワールドリストを取得する (Session利用で強化)"""
    
    # Sessionオブジェクトを作成し、Cookieを直接セット
    session = requests.Session()
    session.cookies.set("auth", authToken, domain="api.vrchat.cloud") 
    # domain設定により、確実にCookieが送信されるようにします
    
    headers = {
        "User-Agent": "Flet VRCWM Client"
    }

    # List Favorited Worlds GETエンドポイントを使用 [1]
    favorites_url = f"{API_BASE_URL}/favorites/worlds"

    try:
        # Sessionオブジェクトを通じてリクエストを実行
        response = session.get(favorites_url, headers=headers)
        response.raise_for_status() 
        return response.json()

    except requests.exceptions.RequestException as e:
        # ここに到達した場合、トークンの有効期限切れ、または接続の問題の可能性が高い
        print(f"APIリクエスト失敗: {e}")
        return None

class WorldListView(ft.View):
    def __init__(self, page: ft.Page, authToken: str):
        
        self.page = page
        
        # --- 1. ワールドデータの取得 ---
        worldData = fetchFavoriteWorlds(authToken)

        if worldData is None:
            # データ取得失敗時
            controlsList = [
                ft.Text("データの取得に失敗しました。トークンが無効の可能性があります。", color=ft.Colors.RED),
                ft.ElevatedButton("再ログイン", on_click=lambda e: page.go("/"))
            ]
        else:
            # VRC Worlds Manager v2はフォルダへの整理機能を持つ [2]。
            worldItems = []
            
            for world in worldData:
                item = ft.ListTile(
                    title=ft.Text(world.get('name', 'N/A')),
                    subtitle=ft.Text(f"Creator: {world.get('authorName', 'N/A')}"),
                    leading=ft.Icon(ft.icons.MAP),
                    trailing=ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(text="フォルダに追加"),
                            ft.PopupMenuItem(text="インスタンス作成") # インスタンス生成機能もVRC Worlds Manager v2の機能 [6]
                        ]
                    )
                )
                worldItems.append(item)

            controlsList = [
                ft.Text(f"✨ お気に入りワールドリスト ({len(worldData)}件)", size=24, weight=ft.FontWeight.BOLD),
                ft.ListView(
                    controls=worldItems,
                    expand=True,
                    spacing=10,
                    padding=20
                )
            ]

        super().__init__(
            route="/worlds",
            controls=[
                ft.Container(
                    content=ft.Column(
                        controlsList,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        expand=True
                    ),
                    padding=30
                )
            ]
        )
