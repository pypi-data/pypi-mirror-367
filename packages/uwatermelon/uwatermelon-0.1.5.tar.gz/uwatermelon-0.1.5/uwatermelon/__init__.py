import webbrowser
import http.server
import socketserver
import threading

# 内部状態
現在の状態 = {
    "ダイアログ": [],
    "メッセージ": [],
    "サーバー": None
}

# スタート関数
def スタート(スクリプト関数):
    print("🍉 うぉーたーめろん - スタート！")
    スクリプト関数()
    print("🍉 終了します。")
    終了()

# 終了関数
def 終了():
    if 現在の状態["サーバー"]:
        現在の状態["サーバー"].shutdown()
        print("🛑 サーバーを停止しました")
    print("🌙 おやすみなさい！")

# メッセージ関数
def メッセージ(内容):
    print(f"📢 メッセージ：{内容}")

# ダイアログ関数
def ダイアログ(タイトル):
    現在の状態["ダイアログ"].append(タイトル)
    print(f"🗨️ ダイアログ「{タイトル}」を表示しました")

# ダイアログアイコン関数
def ダイアログアイコン(種類):
    アイコン種別 = ["情報", "警告", "注意", "管理者", "エラー"]
    if 種類 in アイコン種別:
        print(f"🔔 アイコン：{種類}")
    else:
        print(f"⚠️ 不明なアイコン種類：{種類}")

# ネット関数（URLオープン）
def ネット(url):
    print(f"🌐 開く：{url}")
    webbrowser.open(url)

# サーバースタート関数
def サーバースタート(port=8080):
    ハンドラ = http.server.SimpleHTTPRequestHandler
    現在の状態["サーバー"] = socketserver.TCPServer(("", port), ハンドラ)
    print(f"🖥️ サーバー開始：http://localhost:{port}")
    threading.Thread(target=現在の状態["サーバー"].serve_forever, daemon=True).start()

# 電卓機能
def 電卓(式):
    try:
        結果 = eval(式, {"__builtins__": {}})
        print(f"🧮 結果：{結果}")
        return 結果
    except Exception as e:
        print(f"❌ 計算エラー：{e}")
