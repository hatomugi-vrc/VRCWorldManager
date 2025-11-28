import flet as ft
import requests
import base64

# VRChat Web APIのエンドポイント
API_BASE_URL = "https://api.vrchat.cloud/api/1" 

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        # Fletのカラー定数修正済み
        self.usernameField = ft.TextField(label="VRChat ID / メールアドレス", width=300)
        self.passwordField = ft.TextField(label="パスワード", password=True, can_reveal_password=True, width=300)
        self.statusLabel = ft.Text(value="IDとパスワードを入力してください。", color=ft.Colors.BLACK)
        
        super().__init__(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("VRChat API 認証", size=20, weight=ft.FontWeight.BOLD),
                            self.usernameField,
                            self.passwordField,
                            ft.ElevatedButton("ログイン", on_click=self.onLoginClick),
                            self.statusLabel,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=30,
                    border_radius=10
                )
            ]
        )
        self.page = page

    def loginToVRChat(self, username, password):
        """Basic認証でログインし、認証トークン(auth Cookie)を取得する"""
        
        self.statusLabel.value = "認証を試行中..."
        self.page.update()
        
        try:
            auth_string = f"{username}:{password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "User-Agent": "Flet VRCWM Client"
            }

            # Login and/or Get Current User Info GETエンドポイントを使用 [5]
            login_url = f"{API_BASE_URL}/auth/user" 
            
            response = requests.get(login_url, headers=headers)
            response.raise_for_status() 

            if 'auth' in response.cookies:
                authToken = response.cookies.get('auth')
                # return authToken
                
                # Basic認証成功後、2FAが要求されているかを確認する
                if response.json().get('requiresTwoFactorAuth'):
                    # VRChat APIは通常、Basic認証成功時に2FAが必要な場合、
                    # レスポンスボディにその旨を返します（コミュニティドキュメントより）
                    return (False, authToken, True) # 成功フラグ: False, 2FA必要: True
                else:
                    # 2FA不要で認証完了
                    return (True, authToken, False) # 成功フラグ: True
                                

            return (False, None, False)                
        
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                self.statusLabel.value = "❌ 認証失敗: IDまたはPWが正しくありません。"
            else:
                self.statusLabel.value = f"❌ HTTPエラー: {err}"
        except requests.exceptions.RequestException as e:
            self.statusLabel.value = f"❌ 接続エラー: {e}"
            
        self.page.update()
        return None

    def onLoginClick(self, e):
        """ログインボタンクリック時の処理"""
        id = self.usernameField.value
        pw = self.passwordField.value
        
        if id and pw:
            # authToken = self.loginToVRChat(id, pw)
            success, authToken, requires2FA = self.loginToVRChat(id, pw)
            
            if authToken:
                # トークンをセッションに保存
                self.page.client_storage.set("authToken", authToken)

                if requires2FA:
                    self.statusLabel.value = "⚠️ 2FAが必要です。コードを入力してください。"
                    self.page.update()
                    self.page.go("/2fa") # 2FA画面へ遷移
                elif success:
                    self.statusLabel.value = "✅ 認証成功！ワールドリストへ移動します..."
                    self.page.update()
                    self.page.go("/worlds")
                    
        else:
            self.statusLabel.value = "IDとパスワードの両方を入力してください。"
            self.page.update()