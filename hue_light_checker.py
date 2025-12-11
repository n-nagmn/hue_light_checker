from time import sleep
from configparser import RawConfigParser
import os
import sys
import logging
import warnings
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# InsecureRequestWarningを非表示にする
warnings.simplefilter('ignore', InsecureRequestWarning)

from hue_entertainment_pykit import Bridge, Discovery, Entertainment, Streaming, setup_logs

def main():
    """
    Philips HueのライトIDを簡単に確認するツール【default.ini対応版】
    入力されたIDのライトを1秒間だけ青く光らせます。
    """
    print("\n--- Hue Light ID Checker (default.ini Ver.) ---")

    # --- 設定ファイルの読み込み ---
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    config_path = os.path.join(script_dir, 'default.ini')

    if not os.path.exists(config_path):
        print(f"エラー: 設定ファイル 'default.ini' が見つかりません。")
        return

    config = RawConfigParser()
    config.read(config_path, encoding='utf-8-sig')

    setup_logs(level=logging.WARNING)
    streaming_session = None

    try:
        # --- Hueブリッジへの接続 ---
        my_bridge = None
        
        # default.iniから接続情報を取得
        bridge_ip = config.get('hue', 'BridgeIp', fallback=None)
        username = config.get('hue', 'Username', fallback=None)
        clientkey = config.get('hue', 'Clientkey', fallback=None)

        # ユーザー名とクライアントキーがあれば、直接接続を試みる
        if username and clientkey:
            print("設定ファイルのUsernameとClientkeyを使って接続を試みます...")
            try:
                # IPが指定されていない場合は自動検索
                if not bridge_ip:
                    discovered_bridges = Discovery().discover_bridges()
                    if discovered_bridges:
                        bridge_ip = list(discovered_bridges.values())[0].get_ip_address()
                
                if bridge_ip:
                    my_bridge = Bridge(ip=bridge_ip, username=username, clientkey=clientkey)
                    # 接続確認のため、仮のサービスを叩いてみる
                    Entertainment(my_bridge).get_entertainment_configs()
                    print(f"ブリッジ '{my_bridge.get_name()}' ({my_bridge.get_ip_address()}) に接続しました。")
                else:
                    print("ブリッジが見つからなかったため、自動検索に移行します。")
                    my_bridge = None # 失敗した場合はNoneに戻す

            except Exception as e:
                print(f"保存されたキーでの接続に失敗しました: {e}\nブリッジの自動検索に移行します。")
                my_bridge = None # 失敗した場合はNoneに戻す

        # 直接接続が失敗したか、キーがない場合は自動検索と認証を行う
        if my_bridge is None:
            discovery = Discovery()
            while my_bridge is None:
                print("ネットワーク上のHueブリッジを検索・認証します...")
                bridges = discovery.discover_bridges(ip_address=bridge_ip)
                if bridges:
                    my_bridge = list(bridges.values())[0]
                    break 
                else:
                    print("\nブリッジの認証に失敗しました。Hueブリッジ本体のリンクボタンを押してください。")
                    print("15秒後に再試行します...")
                    sleep(15)
            print(f"ブリッジ '{my_bridge.get_name()}' ({my_bridge.get_ip_address()}) を使用します。")


        # --- エンターテイメントエリアの選択 ---
        area_name = config.get('hue', 'EntertainmentAreaName', fallback=None)
        if not area_name:
            print("エラー: default.iniで EntertainmentAreaName を設定してください。")
            return

        entertainment_service = Entertainment(my_bridge)
        my_area = next((area for area in entertainment_service.get_entertainment_configs().values() if area.name == area_name), None)

        if not my_area:
            print(f"エラー: '{area_name}' という名前のエンターテイメントエリアが見つかりませんでした。")
            return
            
        print(f"エリア '{my_area.name}' を制御します。")
        num_lights_in_area = len(my_area.channels)
        print(f"このエリアには {num_lights_in_area}個 のライトがあります。(IDは 0 から {num_lights_in_area - 1})")

        # --- ストリーミングセッションの開始 ---
        streaming_session = Streaming(my_bridge, my_area, entertainment_service.get_ent_conf_repo())
        streaming_session.start_stream()
        streaming_session.set_color_space("rgb")
        
        # --- IDテストのメインループ ---
        while True:
            prompt = f"\n💡 テストしたいライトのID (0-{num_lights_in_area - 1}) を入力してください ('q'で終了): "
            user_input_id = input(prompt)

            if user_input_id.lower() == 'q':
                break

            try:
                light_id = int(user_input_id)
                if not (0 <= light_id < num_lights_in_area):
                    print(f"   => ❌ IDは 0 から {num_lights_in_area - 1} の範囲で入力してください。")
                    continue
            except ValueError:
                print("   => ❌ 数値を入力してください。")
                continue

            # 選択されたライトを1秒間、青で点灯させる
            print(f"   => ✅ Light ID {light_id} を1秒間、青色で点灯します...")
            streaming_session.set_input((0, 0, 255, light_id))  # 青色で点灯 (R, G, B, LightID)
            sleep(1)  # 1秒待つ
            streaming_session.set_input((0, 0, 0, light_id))   # 消灯

    except KeyboardInterrupt:
        print("\n終了します...")
    except Exception as e:
        print(f"致命的なエラーが発生しました: {e}")
    finally:
        if streaming_session:
            print("\nストリームを停止します...")
            streaming_session.stop_stream()
        print("プログラムを終了しました。")


if __name__ == "__main__":
    main()