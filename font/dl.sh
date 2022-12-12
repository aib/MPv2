#!/bin/sh

wget https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoMusic/NotoMusic-Regular.ttf -O NotoMusic-Regular.ttf
wget https://github.com/notofonts/noto-fonts/raw/main/LICENSE -O NotoMusic-Regular.LICENSE

wget https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansSymbols2/NotoSansSymbols2-Regular.ttf -O NotoSansSymbols2-Regular.ttf
wget https://github.com/notofonts/noto-fonts/raw/main/LICENSE -O NotoSansSymbols2-Regular.LICENSE

wget https://fonts.google.com/download?family=Roboto -O Roboto.zip
unzip Roboto.zip Roboto-Regular.ttf LICENSE.txt
mv LICENSE.txt Roboto-Regular.LICENSE
rm -f Roboto.zip
