import flet as ft
import requests
import base64

# VRChat Web APIのエンドポイント
API_BASE_URL = "https://api.vrchat.cloud/api/1" 

def login_to_vrchat(username, password, status_label):
    """VRChat Web APIにログインし、認証トークンを取得する"""
    
    status_label.value = "認証を試行中..."
    status_label.update()
    
    try:
        # Basic認証のためのヘッダーを作成
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "User-Agent": "Flet VRCWM Client"
        }

        login_url = f"{API_BASE_URL}/auth/user"
        
        # リクエストの実行
        response = requests.get(login_url, headers=headers)
        response.raise_for_status() 

        # 成功時の処理
        if 'auth' in response.cookies:
            auth_token = response.cookies.get('auth')
            status_label.value = f"✅ 認証成功！トークン取得：{auth_token[:20]}..."
            # 取得したトークン（auth_token）をローカルに保存して次回以降に利用します
        else:
            status_label.value = "⚠️ ログイン成功だが、トークンが見つかりませんでした。"
            
    except requests.exceptions.HTTPError as err:
        if response.status_code == 401:
            status_label.value = "❌ 認証失敗: ユーザー名またはパスワードが正しくありません。"
        else:
            status_label.value = f"❌ HTTPエラー: {err}"
    except requests.exceptions.RequestException as e:
        status_label.value = f"❌ 接続エラー: {e}"
        
    status_label.update()


def main(page: ft.Page):
    page.title = "VRChat API ログイン"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- UI要素の定義 ---
    
    # ユーザー名入力フィールド
    username_field = ft.TextField(label="VRChat ID / メールアドレス", width=300)
    # パスワード入力フィールド (非表示設定)
    password_field = ft.TextField(label="パスワード", password=True, can_reveal_password=True, width=300)
    
    # ステータス表示ラベル
    status_label = ft.Text(value="IDとパスワードを入力してください。", color=ft.Colors.BLACK)

    def on_login_click(e):
        """ログインボタンがクリックされたときに実行される関数"""
        id = username_field.value
        pw = password_field.value
        
        if id and pw:
            # 入力値を読み取り、APIログイン関数を呼び出す
            login_to_vrchat(id, pw, status_label)
        else:
            status_label.value = "IDとパスワードの両方を入力してください。"
            page.update()

    # ログインボタン
    login_button = ft.ElevatedButton("ログイン", on_click=on_login_click)

    # ページに要素を追加
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("VRChat Web API 認証", size=20, weight=ft.FontWeight.BOLD),
                    username_field,
                    password_field,
                    login_button,
                    status_label,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=30,
            border_radius=10
        )
    )

ft.app(target=main)