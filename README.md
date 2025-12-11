# Hue Entertainment Light ID Checker

Philips Hueの「エンターテイメントエリア」に登録されているライトの **ID（インデックス番号）** を特定するためのPythonユーティリティです。

エンターテイメントAPIを使用する際、プログラム上の配列インデックス（0, 1, 2...）が、部屋にある「どの物理的な電球」に対応しているか分からない場合に役立ちます。指定したIDのライトを一時的に青く点灯させることで、位置関係を即座に把握できます。

## 機能

  * **ID確認**: コンソールで数字（0, 1...）を入力すると、対応するライトが1秒間だけ**青色**に光ります。
  * **設定ファイル対応**: `default.ini` からブリッジ情報やエリア名を読み込みます。
  * **自動接続**: 設定ファイルにIPやキーがない場合、自動的にブリッジを検索し、Linkボタンによる認証を行います。

## 必要要件

  * Python 3.x
  * [hue-entertainment-pykit](https://www.google.com/search?q=https://github.com/phue/hue-entertainment-pykit)

### インストール

```bash
pip install hue-entertainment-pykit
```

## セットアップ

スクリプトと同じディレクトリに `default.ini` ファイルを作成し、以下の内容を記述してください。

**default.ini**

```ini
[hue]
; ブリッジのIPアドレス（空欄でも自動検索しますが、指定すると高速です）
BridgeIp = 192.168.1.50

; Hueアプリで作成したエンターテイメントエリアの名前（必須）
EntertainmentAreaName = My PC Room

; 初回実行後に生成された値をここにコピーしておくと、次回からボタンを押さずに接続できます
Username = 
Clientkey = 
```

## 使い方

1.  スクリプトを実行します。
    ```bash
    python hue_light_id_checker.py
    ```
2.  初回接続時は、コンソールの指示に従って **Hueブリッジ本体のリンクボタン** を押してください。
3.  接続が成功すると、そのエリアに含まれるライトの数が表示されます。
4.  テストしたい **ID（0 から N-1）** を入力して Enter を押してください。
5.  対象のライトが青く光ります。
6.  `q` を入力すると終了します。

### 実行例

```text
--- Hue Light ID Checker (default.ini Ver.) ---
設定ファイルのUsernameとClientkeyを使って接続を試みます...
ブリッジ 'Philips Hue' (192.168.1.50) に接続しました。
エリア 'My PC Room' を制御します。
このエリアには 3個 のライトがあります。(IDは 0 から 2)

テストしたいライトのID (0-2) を入力してください ('q'で終了): 0
   => Light ID 0 を1秒間、青色で点灯します...

テストしたいライトのID (0-2) を入力してください ('q'で終了): 1
   => Light ID 1 を1秒間、青色で点灯します...
```

## License

MIT License