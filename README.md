![CI Tests](https://github.com/KyleS22/friendly_ground_truth/workflows/CI%20Tests/badge.svg)

[![codecov](https://codecov.io/gh/KyleS22/friendly_ground_truth/branch/master/graph/badge.svg)](https://codecov.io/gh/KyleS22/friendly_ground_truth)


# friendly_ground_truth
A tool for manually creating ground truth masks from images where a significant amount of detail is required.

# Installation
To install download the (latest release)[https://github.com/KyleS22/friendly_ground_truth/releases/latest], unpack it, and run `make install`.

If you like, here is a bash script that will handle all of that for you

```
newest_version=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tag_name" | sed -E 's/.*"([^"]+)".*/\1/')
tar_path=$(curl https://api.github.com/repos/KyleS22/friendly_ground_truth/releases/latest | grep "tarball_url" | sed -E 's/.*"([^"]+)".*/\1/')
tar_name="friendly_gt-$newest_version.tar"
wget $tar_path -O $tar_name
new_dir_name=$(tar -tf $tar_name | sed -e 's@/.*@@' | uniq)
tar xvfz "$tar_name" -C ./
mv $new_dir_name friendly_ground_truth
cd friendly_ground_truth
make install
```
