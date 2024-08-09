#!/usr/bin/env bash
set -e

test -d out && rm -rf out

mkdir -v out

cp -Rv datasheets lessons/{*.html,res} out/

wget "https://github.com/hakimel/reveal.js/archive/refs/tags/5.1.0.tar.gz"
tar -xvf 5.1.0.tar.gz
rm 5.1.0.tar.gz
mv -v reveal.js-5.1.0 out/reveal.js

cat datasheets/_index.html | tr '\n' ' ' |
    python -c "print(input().replace('%TEMPLATE%', '$(ls -1 out/datasheets/*.pdf | xargs -n1 basename | awk '{print "<li><a href=\""$1"\">"$1"</a></li>"}' | tr '\n' ' ')'))" \
    > out/datasheets/index.html
rm -v out/datasheets/_index.html
