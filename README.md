# 検証手順
## 0\. 検証計画時の注意点
 - 以下に記載する手順は2025年12月時点のものです。SOPではありませんので、状況に合わせて各自やりやすいように適宜変更してください。
 - OncoStationに未登録の検体を使用した場合、解析自体はできますがPDFレポートの作成ができません。（rule: report_json 実行時、DBにアクセスして検体情報を検索する際に、登録情報がなくエラー終了するため）
 - 開発サーバーで解析を行うと、API通信制限のためか、PDFが作成されないことがあります。（すべての検体で起こるわけではありません）
 - 開発サーバーで検証する際は、臨床検体を使用せず、標準物質またはCAP PT検体等を使用すること。（セキュリティ面で安全が担保できていません）
 - 検証スクリプトのダウンロード(git clone)や解析の実行は **gxd_pipeline ユーザーで実施**してください。fastq.gz のコピーや実行ファイル(bash)の作成等は他のユーザーでも問題ないですが、gxd_pipelineユーザーに閲覧・実行権限を付与しておいてください。
 - CAPサーバーでの検証は、やむを得ない場合を除き、**現行のパイプラインが稼働しているときには行わない**こと。**改修内容によっては仕様と異なるリファレンスファイルを参照してしまうので**、想定した検証ができない可能性があります。
 - レポートの「Additional Information」項目のバージョン値は以下の値が反映されます。\
&ensp;&ensp; Pipeline: スクリプトファイルに固定値として記載されている値\
&ensp;&ensp; OncoStation: データベースの report_version テーブルの値\
⇒ Pipelineの検証ではOncoStationで作成されるPDFファイル(=レポートシステムにuploadされる報告書)の検証はできません。

## 1\. 検体の準備
通常は以下のフォルダを検証用の解析フォルダとして使用してください。\
&ensp;&ensp;&ensp; CAPサーバー： /data1/data/result/[analysis type]/Validation/[new version] \
&ensp;&ensp;&ensp; 開発サーバー： /data1/data/result/[analysis type]/[new version]
<details>
  <summary> 
    Detail
  </summary>

#### 1-1\. sshクライアントからgxd_pipelineユーザーでログインし、検証に使用する検体の fastq.gz の存在を確認する。
<img src="https://github.com/user-attachments/assets/fec5ee81-0350-4e41-8d55-316b051762c6" width="500"> \
① batch name ② sample ID \
ファイルがない場合は、backup storage (/data2/backup/NovaseqX/) を確認する。\
<img src="https://github.com/user-attachments/assets/ad7912f6-846e-4877-8722-54549a969045" width="500"> \
① batch name ② sample ID \
/data1/data/NovaseqX/[batch name] にファイルがない場合は、backup storageからコピーする。※開発サーバーのみ 
```
rsync -avzru gxd_pipeline@192.168.9.100:/data2/backup/NovaseqX/[batch name]/[sample ID].R*.fastq.gz /data1/data/NovaseqX/[batch name]/
```
※ backup storageはCAPサーバーにマウントされているので、CAPサーバーでの検証時は backup storage の fastq.gz に直接リンクを張って使用する。

#### 1-2\. Fastqフォルダを含む解析ディレクトリを作成し、fastq.gz のシンボリックリンクを作成する。
WTSの場合は、リンクファイル名と元ファイル名は同じ。\
CAPサーバーの場合:
```
mkdir -p /data1/data/result/[analysis type]/Validation/[new version]/[sample ID]/Fastq
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/WTS/Validation/[new version]/[sample ID]/Fastq/
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/WTS/Validation/[new version]/[sample ID]/Fastq/
```
fastq.gzが backup storage に移動していた場合:
```
mkdir -p /data1/data/result/[analysis type]/Validation/[new version]/[sample ID]/Fastq
ln -s /data2/backup/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/WTS/Validation/[new version]/[sample ID]/Fastq/
ln -s /data2/backup/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/WTS/Validation/[new version]/[sample ID]/Fastq/
```
開発サーバーの場合:
```
mkdir -p /data1/data/result/[analysis type]/[new version]/[sample ID]/Fastq
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/WTS/[new version]/[sample ID]/Fastq/
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/WTS/[new version]/[sample ID]/Fastq/
```
**※ eWESの場合はリンクファイル名が元ファイルと異なることに注意。**\
CAPサーバーの場合:
```
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/eWES/Validation/[new version]/[sample ID]/Fastq/[sample ID].tumour.R1.fastq.gz
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/eWES/Validation/[new version]/[sample ID]/Fastq/[sample ID].tumour.R2.fastq.gz
```
fastq.gzが backup storage に移動していた場合:
```
ln -s /data2/backup/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/eWES/Validation/[new version]/[sample ID]/Fastq/[sample ID].tumour.R1.fastq.gz
ln -s /data2/backup/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/eWES/Validation/[new version]/[sample ID]/Fastq/[sample ID].tumour.R2.fastq.gz
```
開発サーバーの場合:
```
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R1.fastq.gz /data1/data/result/eWES/[new version]/[sample ID]/Fastq/[sample ID].tumour.R1.fastq.gz
ln -s /data1/data/NovaseqX/[batch name]/[sample ID].R2.fastq.gz /data1/data/result/eWES/[new version]/[sample ID]/Fastq/[sample ID].tumour.R2.fastq.gz
```

#### 1-3\. 解析ディレクトリの直下にrun.shを作成、解析実行コマンドを記載する。
1検体毎にrun.shを作成した場合、解析の実行も1検体毎に実施することになるので、複数の検体の実行コマンドをまとめて1つの run.sh を作成しても構いません。\
CAPサーバーの .fastq.gzを参照している場合:
```
vi /data1/data/result/[analysis type]/Validation/[new version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --snakefile /data1/GxD_[analysis type]/versions/[new version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[new version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/Validation/[new version]' & 
```
backup storage の .fastq.gz を参照している場合: \
snakemake 実行時のオプションを追加して backup storage のデータを参照できるようにする。
```
vi /data1/data/result/[analysis type]/Validation/[new version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --singularity-args '--bind /data2:/data2 --bind /data1:/data1’ --snakefile /data1/GxD_[analysis type]/versions/[new version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[new version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/Validation/[new version]' & 
```
開発サーバーの場合:
```
vi /data1/data/result/[analysis type]/[new version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --snakefile /data1/GxD_[analysis type]/versions/[new version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[new version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/[new version]' & 
```
</details>

## 2\. 検証するパイプラインのインストール
<details>
  <summary> 
    Detail
  </summary>

#### 2-1\. sshクライアントからgxd_pipelineユーザーでログインし、Bitbucket からソースコードをダウンロードする。
```
git clone -b dev git@bitbucket.org:geninus/gxd_ewes.git
git clone -b dev git@bitbucket.org:geninus/gxd_wts.git
```
※ -b dev オプションで dev branch のコードをDLする。\
※ dev 以外のbranchで開発されていた場合は、該当するbranch名を指定する。main branch の場合はオプション不要。
#### 2-2\. パイプラインのソースコード置き場（/data1/GxD_[analysis type]/versions/）の下に移動させてフォルダ名を適宜付与する。
```
mv gxd_ewes /data1/GxD_eWES/versions/[new version]
mv gxd_wts /data1/GxD_WTS/versions/[new version]
```
#### 2-3\. containers フォルダを削除する。
```
rm -rf /data1/GxD_eWES/versions/[new version]/containers
rm -rf /data1/GxD_WTS/versions/[new version]/containers
```
#### 2-4\. 親ディレクトリの containers フォルダのシンボリックリンクを作成する。
※ Pipelineの改修に伴い、コンテナファイルに変更がある場合は適宜変更する
```
ln -s /data1/GxD_eWES/containers /data1/GxD_eWES/versions/[new version]/
ln -s /data1/GxD_WTS/containers /data1/GxD_WTS/versions/[new version]/
```
</details>

## 3\. 検証するパイプラインの修正
初回解析時に作成されたファイルや、データベースに登録済みの解析結果を変更しないよう、一部のコードを一時的に変更する。
<details>
  <summary> 
    Detail
  </summary>

#### 3-1\. */[new version]/workflow/layer/summarize.smk: report_json rule のuploadオプションをFalseに変更する。
※ データベースの更新をしないようにするための処理。\
<img src="https://github.com/user-attachments/assets/42610d69-97ff-4df7-8e06-9c170c3a7b35" width="400"> 
#### 3-2\. */[new version]/workflow/configs/files.py の self.report_pdf を修正してPDFレポートの出力先を変更する。（開発サーバーのみ）
※ API（レポートシステム）でレポートを作成するとCAPサーバーに出力されるので、上書きしないように任意のファイルパスを指定する。\
<img src="https://github.com/user-attachments/assets/4a04bc67-e6af-4b71-8a73-29752132f98e" width="500"> 
</details>

## 4\. 検証の実行
<details>
  <summary> 
    Detail
  </summary>

#### 4-1\. 1-3.で作成した run.sh を実行する
```
cd /data1/data/result/[analysis type]/Validation/[new version]/[sample ID] && sh run.sh
```
開発サーバーの場合
```
cd /data1/data/result/[analysis type]/[new version]/[sample ID] && run.sh
```
### 4-2\. 解析結果をまとめる
全ての検体で解析完了が確認できたら、解析結果をまとめて1つのExcelファイルに書き出す。\
サンプル毎の解析フォルダにアクセスし、summarized.*.tsv を読み込んで集約するスクリプト post_process.py を利用する。
```
singularity exec --bind /data1 /data1/labTools/labTools.sif python post_process.py -d [analysis dirpath] -o [outputfile.xlsx]
```
開発サーバーの場合
```
singularity exec --bind /data1 /data1/labTools/labTools.sif python post_process.py -d [analysis dirpath] -o [outputfile.xlsx]
```
</details>

## 5\. 現行バージョンでの解析（必要に応じて実施）
検証に用いる検体が現行バージョンで解析されたものではない場合、新旧パイプラインの解析結果を比較するために現行バージョンのパイプラインでも解析を行う。\
データベースの更新を防ぐためにパイプラインを一部変更して実行する必要があるので、**検査がない期間に実施する**こと。
<details>
  <summary> 
    Detail
  </summary>

#### 5-1\. 解析の準備
検証用の解析フォルダの下に、現行バージョンの解析フォルダをFastqを含めて作成する。\
&nbsp;&nbsp;&nbsp;&nbsp; CAPサーバー： /data1/data/result/[analysis type]/Validation/[new version]/[current version] \
&nbsp;&nbsp;&nbsp;&nbsp; 開発サーバー： /data1/data/result/[analysis type]/[new version]/[current version] \
CAPサーバーの場合:
```
mkdir -p /data1/data/result/[analysis type]/Validation/[new version]/[current version]/[sample ID]/Fastq
```
開発サーバーの場合:
```
mkdir -p /data1/data/result/[analysis type]/[new version]/[sample ID]/Fastq
```
#### 5-2\. fastq.gz のシンボリックリンクを作成する。
リンク元のファイルは 1-1.で確認したものを使用。リンクの作成コマンドは 1-2.を参照。
#### 5-3\. 解析ディレクトリの直下にrun.shを作成、解析実行コマンドを記載する。
1検体毎にrun.shを作成した場合、解析の実行も1検体毎に実施することになるので、複数の検体の実行コマンドをまとめて1つの run.sh を作成しても構いません。\
CAPサーバーの場合:
```
vi /data1/data/result/[analysis type]/Validation/[new version]/[current version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --snakefile /data1/GxD_[analysis type]/versions/[current version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[current version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/Validation/[new version]/[current version]' & 
```
fastq.gz が backup storage に移動していた場合: \
snakemake 実行時にオプションを追加する。（backup storageのデータを参照できるようにする）
```
vi /data1/data/result/[analysis type]/Validation/[new version]/[current version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --singularity-args '--bind /data2:/data2 --bind /data1:/data1’ --snakefile /data1/GxD_[analysis type]/versions/[current version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[current version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/Validation/[new version]/[current version]' & 
```
開発サーバーの場合:
```
vi /data1/data/result/[analysis type]/[new version]/[current version]/[sample ID]/run.sh
source /data1/iGeniPipe/miniconda3/bin/activate cs && 
snakemake --snakefile /data1/GxD_[analysis type]/versions/[current version]/workflow/Snakefile --directory /data1/GxD --profile /data1/GxD_[analysis type]/versions/[current version]/profiles/all.q --config patient_id='[sample ID]' output_dir='/data1/data/result/[analysis type]/[new version]/[current version]' & 
```
#### 5-4\. パイプラインの修正
*/[current version]/workflow/layer/summarize.smk: report_json rule のuploadオプションをFalseに変更する。\
※ データベースの更新をしないようにするための処理。3-1. を参照。\
*/[new version]/workflow/configs/files.py の self.report_pdf を修正してPDFレポートの出力先を変更する。**（開発サーバーのみ）**\
※ API（レポートシステム）でレポートを作成するとCAPサーバーに出力されるので、上書きしないように任意のファイルパスを指定する。3-2.を参照。
#### 5-5\. 解析の実行
CAPサーバーの場合:
```
cd /data1/data/result/[analysis type]/Validation/[new version]/[current version]/[sample ID] && sh run.sh
```
開発サーバーの場合:
```
cd /data1/data/result/[analysis type]/[new version]/[current version]/[sample ID] && sh run.sh
```
### 5-6\. 解析結果をまとめる
全ての検体で解析完了が確認できたら、解析結果をまとめて1つのExcelファイルに書き出す。\
サンプル毎の解析フォルダにアクセスし、summarized.*.tsv を読み込んで集約するスクリプト post_process.py を利用する。
```
singularity exec --bind /data1 /data1/labTools/labTools.sif python post_process.py -d [analysis dirpath] -o [outputfile.xlsx]
```
開発サーバーの場合:
```
singularity exec --bind /data1 /data1/labTools/labTools.sif python post_process.py -d [analysis dirpath] -o [outputfile.xlsx]
```
**変更したスクリプトファイルは必ず元に戻しておくこと。**
</details>

## 6\. パイプラインのアップデート
TS,LDの承認を得て検証の合格が確定したら、反映日までにパイプラインをアップデートしておく。\
**3-1, 3-2, 5-4 で変更したスクリプトファイルを元に戻したことを確認しておくこと。**
<details>
  <summary> 
    Detail
  </summary>

#### 6-1\. 新バージョンのPipelineスクリプトの確認
パイプラインフォルダの直下にある .pipeline ファイルに記載のバージョンが、アップデート後のバージョンであることを確認する。（この値がパイプラインレポート最終頁のパイプラインバージョンに反映されます）
```
$ cat /data1/GxD_eWES/versions/[new version]/.pipeline
VERSION=[new version]
```
#### 6-2\. シンボリックリンクの差し替え
/data1/GxD_[analysis type]/Pipeline を一度削除してから新たなシンボリックリンクを作成する。
```
rm /data1/GxD_[analysis type]/Pipeline
ln -s /data1/GxD_[analysis type]/versions/[new version] /data1/GxD_[analysis type]/Pipeline
```
#### 6-3\. データベースに登録されているバージョン情報の更新
OncoStationで作成されるPDFファイル(=レポートシステムにuploadされる報告書)の「Additional Information」項目が新Pipelineの情報と一致するよう、データベースに登録されているレポートバージョンの更新をGSからITチームに指示するよう依頼する。(変更がない場合は依頼しなくてよい)
</details>
