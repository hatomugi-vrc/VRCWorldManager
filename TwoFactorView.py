import flet as ft
import requests
import json

# VRChat Web APIのエンドポイント
API_BASE_URL = "https://api.vrchat.cloud/api/1" 

class TwoFactorView(ft.View):
    def __init__(self, page: ft.Page, authToken: str):
        self.page = page
        self.authToken = authToken
        
        self.codeField = ft.TextField(
            label="6桁の2FAコード", 
            width=300, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"[1, 3-10]", replacement_string=""),
            max_length=6
        )
        self.statusLabel = ft.Text("認証アプリまたはメールで受け取ったコードを入力してください。", color=ft.Colors.BLUE_GREY)

        super().__init__(
            route="/2fa",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("二要素認証 (2FA) が必要です", size=20, weight=ft.FontWeight.BOLD),
                            self.codeField,
                            ft.ElevatedButton("コード検証", on_click=self.onVerifyClick),
                            self.statusLabel,
                            ft.TextButton("再ログイン", on_click=lambda e: page.go("/"))
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=30,
                    border_radius=10
                )
            ]
        )

    def verify2FACode(self, code):
        """2FAコードをVRChat APIに送信し、認証を完了させる"""
        
        self.statusLabel.value = "コード検証中..."
        self.page.update()
        
        try:
            cookies = {
                "auth": self.authToken # Basic認証で取得した一時トークンを使用
            }
            headers = {
                "User-Agent": "Flet VRCWM Client",
                "Content-Type": "application/json"
            }
            data = {
                "code": code
            }
            
            # Verify 2FA code POSTエンドポイントを使用 [2]
            verify_url = f"{API_BASE_URL}/auth/twofactor/totp/verify" 
            
            response = requests.post(verify_url, headers=headers, cookies=cookies, data=json.dumps(data))
            response.raise_for_status() 

            # VRChat APIが2FA検証成功時に返すステータスをチェック
            if response.status_code == 200:
                # 2FA検証に成功すると、既存のauthトークンがフルアクセス可能な状態になります
                return True
            
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401 or response.status_code == 400:
                self.statusLabel.value = "❌ 検証失敗: コードが正しくないか、トークンの有効期限が切れました。"
            else:
                self.statusLabel.value = f"❌ HTTPエラー: {err}"
        except requests.exceptions.RequestException as e:
            self.statusLabel.value = f"❌ 接続エラー: {e}"
            
        self.page.update()
        return False

    def onVerifyClick(self, e):
        """検証ボタンクリック時の処理"""
        code = self.codeField.value
        
        if code and len(code) == 6:
            if self.verify2FACode(code):
                self.statusLabel.value = "✅ 2FA認証完了！ワールドリストへ移動します..."
                self.page.update()
                
                # 認証が完了したので、ワールドリスト画面へ遷移
                self.page.go("/worlds")
            # 検証失敗時は verify2FACode 内でステータスラベルが更新済み
        else:
            self.statusLabel.value = "6桁のコードを入力してください。"
            self.page.update()