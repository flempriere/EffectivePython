#!/usr/bin/env bash

# copies generated markdown files, so that they can still be accessed from inside the repository
# source code based on https://stackoverflow.com/questions/35765470/how-to-move-files-from-x-sub-dir-to-y-sub-dir

# Specify source and target directories (example values)


dirFrom='_site'
dirTo='.'

shopt -s dotglob   # include hidden items when matching `*`
shopt -s nullglob  # expand patterns that don't match anything to the empty string
shopt -s globstar  # search multiple layers of directories

## move index file as the readme
echo "${dirFrom}"/**/index.md "${dirTo}/README.md"


# Use globbing to find all subdirectories - note the trailing '/'
# to ensure that only directories match.
for markdown_file in "$dirFrom"/**/*.md; do

    #strip of from directory and replace with to directory then move
    mv_to="${markdown_file//$dirFrom/$dirTo}"

    mv "${markdown_file}" "${mv_to}"

done
