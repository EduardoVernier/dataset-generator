#!/bin/bash
# Example
# ./batch_extraction.sh repos.txt -m
urls_file=$1
period=$2

echo $urls_file  # file with github urls to be cloned
echo $period  # -a, -d, -m, -y,

# Download all repositories in repo urls file
mkdir repos
cp $urls_file ./repos
cd repos
for repo in $(cat $urls_file)
do
	git clone $repo
done
rm $urls_file
cd ..

# Run the script on all cloned repos
for dir in $(ls repos)
do
	repo=$(pwd)'/repos/'$dir
	python2 cloc_extractor.py -f $repo $period
done
rm files
