#!/bin/sh

mkdir -vp deps
pushd deps
for url in $( cat ../deps.txt ); do wget $url; done
popd
