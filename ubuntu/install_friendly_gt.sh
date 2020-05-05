#!/bin/bash

mkdir -p ~/bin
mkdir -p ~/.icons

chmod u+x ./friendly_gt_ubuntu-latest
mv ./friendly_gt_ubuntu-latest ~/bin/friendly_gt
mv ./friendly_gt.desktop ~/.local/share/applications
mv ./friendly_gt.png ~/.icons

if [[ :$PATH: == *:"$~/bin":* ]] ; then
    echo ""
else
    read -p "Add ~/bin to your path? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 
    read -p "Specify bash profile file (blank uses ~/.bashrc): " response

    if [ "$response" == "" ]; then
	    file=~/.bashrc
    else
	    file=$response
    fi
    
    file="${file/#~/$HOME}"

    if [ -f "$file" ]; then
    	grep -qxF 'export PATH=~/bin:${PATH}' "$file" || echo 'export PATH=~/bin:${PATH}' >> "$file"
    else 
	echo "Sorry, the given file does not exist"
    fi
fi
