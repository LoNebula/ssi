# SSI Multi-Computer Recording & Speaker Classification Setup

このフォルダ (`SSI/lonebula`) には、複数コンピュータ間でデータを同期・収集し、簡易的な話者分類を行うためのサンプル・パイプラインが含まれています。

## ファイル構成
*   `sender.pipeline`: データ送信側（各ユーザーのPCで実行）。カメラ、マイク、VAD（発話検出）データをサーバーに送信します。
*   `receiver.pipeline`: データ受信側（集約用PCで実行）。送られてきたデータを表示・保存します。

## 機能解説

### Q1. 複数コンピュータ間でデータを取りたい（同期含む）
SSIのネットワークソケット機能 (`SocketReader`/`SocketWriter`) を使用して実現しています。
`receiver.pipeline` がサーバーとして待受を行い、`sender.pipeline` がデータをUDPでストリーミングします。
`framework` タグの `sync="true"` 設定により、SSIフレームワークレベルでの同期が図られます。

### Q2. 複数コンピュータでそれぞれにカメラと音声データを取得したい
`sender.pipeline` には `Camera` センサーと `Audio` センサーの両方が組み込まれており、それぞれのデータを個別のポートで送信するように設定しています。

### Q3. 「この人がしゃべっている！」と分類したい
`sender.pipeline` に `AudioActivity` (VAD: Voice Activity Detection) コンポーネントを追加しました。
これは音声データから「発話中かどうか」を判定し、0～1の信号を出力します。
受信側 (`receiver.pipeline`) では、このVAD信号 (`vad_A`) を音声・映像と一緒に受け取ります。
**「VAD信号の値が高い＝その人が喋っている」** とみなすことで、誰が発話者かを分類・特定することができます。

## 実行手順

### 1. 受信側 (Receiver) の準備
データの集約を行うPCで `receiver.pipeline` を実行します。
```bash
xmlpipe receiver.pipeline
```
※ `receiver.pipeline` 内の `url="udp://..."` 部分のポート番号が、送信側の設定と合っているか確認してください。

### 2. 送信側 (Sender) の準備
カメラとマイクがついたPCで `sender.pipeline` を編集し、実行します。
編集箇所: `sender.pipeline` 内の `SocketWriter` の `url` を、受信PCのIPアドレスに変更してください。
（例: `url="udp://192.168.1.10:9000"`）

```bash
xmlpipe sender.pipeline
```

これで、受信側のPCに映像・音声・発話状態がリアルタイムで届き、`data` フォルダに保存されます。
