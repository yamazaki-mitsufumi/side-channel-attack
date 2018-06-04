攻撃対象などはパラメーターから変更できます
ディレクトリ構成：

hoge_cpa.py
hoge_parameter.py
plain_cipher.txt <- "ファイル名,xp,3xq*xp"という列を持つ※
wave/
  000000.csv　<- 一列の電力波形※※
  000001.csv
  ...

※現在ファイル名を使用していないので順番は適宜調整してください
※※整数の前提で作っているので必要であれば適宜調整してください

Damien Jauvart,"Improving Side-Channel Attacks against Pairing-Based Cryptography"
Thomas Unterluggauer,"Practical Attack on Bilinear Pairings to Disclose the Secrets of Embedded Devices"