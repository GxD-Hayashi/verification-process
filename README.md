# 検証手順
## 0\. 検証計画時の注意点
 - OncoStationに未登録の検体を使用するとPDFレポートの作成ができません。\
　（rule: report_json 実行時、DBにアクセスして検体情報を検索する際に、登録情報がなくエラー終了するため）
 - 開発サーバーで解析を行うと、API通信制限のためか、PDFが作成されないことがあります。\
　（すべての検体で起こるわけではありません）
 - 開発サーバーで検証する際は、臨床検体を使用せず、標準物質またはCAP PT検体等を使用すること。\
　（セキュリティ面で安全が担保できていません）
 - 検証スクリプトのダウンロード(git clone)や解析の実行は gxd_pipeline ユーザーで実施してください。\
データのコピーやbashファイルの作成等は他のユーザーでも問題ないですが、gxd_pipelineユーザーに閲覧・実行権限を付与しておいてください。
 - CAPサーバーでの検証は、やむを得ない場合を除き、現行のパイプラインが稼働しているときには行わないこと。\
リソースが限られているため。また改修内容によっては仕様と異なるリファレンスファイルを参照するので、想定した検証ができない可能性があります。
 - レポートの「Additional Information」項目のバージョン値について\
Pipelineで作成されるJSON,PDFは /modules/report_json/main.py に固定値で記載されている値が反映されます。\
OncoStationで作成されるPDFはデータベースの report_version テーブルの値が反映されます。\
→ 必ずしも同じ値ではないことに留意してください。
 - 通常は以下のフォルダを検証用の解析フォルダとして使用する。\
   CAPサーバ： /data1/data/result/[analysis type]/Validation/[version] \
   開発サーバ： /data1/data/result/[analysis type]/[version]

## 1\. 検体の準備
<details>
  <summary> 
    詳細
  </summary>

sshクライアントからgxd_pipelineユーザーでログインし、検証に使用する検体のfastq.gzの存在を確認する。
<img src="https://github.com/user-attachments/assets/fa699745-c0ed-4b07-a3f0-18af9aaaf471" width="500"> \
① batch name ② sample ID 

ファイルがない場合は、CAPサーバーまたはBackUpサーバーからコピーする。\
CAPサーバの場合:
```
rsync -avzru /data2/backup/NovaseqX/[batch name]/[sample ID].R*.fastq.gz /data1/data/NovaseqX/[batch name]/
```
開発サーバの場合:
```
rsync -avzru gxd_pipeline@192.168.9.100:/data1/data/NovaseqX/[batch name]/[sample ID].R*.fastq.gz /data1/data/NovaseqX/[batch name]/
rsync -avzru gxd_pipeline@192.168.9.100:/data2/backup/NovaseqX/[batch name]/[sample ID].R*.fastq.gz /data1/data/NovaseqX/[batch name]/
```
Fastqフォルダを含む解析ディレクトリを作成し、fastq.gzのシンボリックリンクを作成する。\
CAPサーバの場合:
```
mkdir -p /data1/data/result/[analysis type]/Validation/[version]/[sample ID]/Fastq
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/[analysis type]/Validation/[version]/[sample ID]/Fastq/
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/[analysis type]/Validation/[version]/[sample ID]/Fastq/
```
開発サーバの場合:
```
mkdir -p /data1/data/result/[analysis type]/[version]/[sample ID]/Fastq
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/[analysis type]/[version]/[sample ID]/Fastq/
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/[analysis type]/[version]/[sample ID]/Fastq/
```
eWESの場合はリンクファイル名が元ファイルと異なることに注意。
CAPサーバの場合:
```
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/[analysis type]/Validation/[version]/[sample ID]/Fastq/[sample ID].tumour.R1.fastq.gz
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/[analysis type]/Validation/[version]/[sample ID]/Fastq/[sample ID].tumour.R2.fastq.gz
```
開発サーバの場合:
```
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/[analysis type]/[version]/[sample ID]/Fastq/[sample ID].tumour.R1.fastq.gz
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/[analysis type]/[version]/[sample ID]/Fastq/[sample ID].tumour.R2.fastq.gz
```
解析ディレクトリの直下にrun.shを作成、解析実行コマンドを記載する。
```
vi /data1/data/result/[analysis type]/[batch name]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --snakefile /data1/[analysis type]/version/[version]/workflow/Snakefile --directory /data1/GxD --profile /data1/[analysis type]/version/[version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/eWES/20250527_LH00432_0059_B22YVM3LT3' & 
```

</details>
