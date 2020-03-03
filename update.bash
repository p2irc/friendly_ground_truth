#!/bin/bash
newest_version=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tag_name" | sed -E 's/.*"([^"]+)".*/\1/')

python src/version_info.py $newest_version

if [ "$?" -eq "0" ]; then
	tar_path=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tarball_url" | sed -E 's/.*"([^"]+)".*/\1/')
	tar_name="friendly_gt-$newest_version.tar"
	wget $tar_path -O $tar_name
	new_dir_name=$(tar -tf $tar_name | sed -e 's@/.*@@' | uniq)
	tar xvfz "friendly_gt-$newest_version.tar" -C ./
	cp -r $new_dir_name/* .
	rm -rf $new_dir_name
	rm $tar_name
	make install
fi
