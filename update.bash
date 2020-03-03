#!/bin/bash
newest_version=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tag_name" | sed -E 's/.*"([^"]+)".*/\1/')

python src/version_info.py $newest_version

if [ "$?" -eq "0" ]; then
	tar_path=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tarball_url" | sed -E 's/.*"([^"]+)".*/\1/')
	wget $tar_path -O "friendly_gt-$newest_version.tar"
	tar xvfz "friendly_gt-$newest_version.tar" ./
fi
