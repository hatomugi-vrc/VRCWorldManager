import flet as ft
from LoginView import LoginView
from WorldListView import WorldListView
from TwoFactorView import TwoFactorView

# VRChat APIはVRChatによって公式にはサポートまたは文書化されていないことに注意してください [3, 4]。
# APIのエンドポイントは予告なく変更される可能性があるため、利用には注意が必要です [4]。

def main(page: ft.Page):
    page.title = "VRC Worlds Manager (Flet)"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # 認証トークンを保持
    page.client_storage.set("authToken", "") 

    def route_change(route):
        page.views.clear()
        
        # --- ログイン画面 ---
        if page.route == "/":
            # LoginViewクラスをインポートして利用
            page.views.append(LoginView(page))
            
        # --- 二段階認証画面 ---
        elif page.route == "/2fa":
            authToken = page.client_storage.get("authToken")
            if authToken:
                page.views.append(TwoFactorView(page, authToken))
            else:
                page.go("/")
        
        # --- ワールドリスト画面 ---
        elif page.route == "/worlds":
            authToken = page.client_storage.get("authToken")
            
            if authToken:
                # WorldListViewクラスにトークンを渡して利用
                page.views.append(WorldListView(page, authToken))
            else:
                # トークンがない場合はログイン画面に戻す
                page.go("/")
        
        page.update()

    page.on_route_change = route_change
    page.go("/") 

if __name__ == "__main__":
    ft.app(target=main)