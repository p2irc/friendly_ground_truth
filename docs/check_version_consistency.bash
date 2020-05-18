major_num=`grep "VERSION_MAJOR = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`
minor_num=`grep "VERSION_MINOR = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`
patch_num=`grep "VERSION_PATCH = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`

code_str="v$major_num.$minor_num.$patch_num"

changelog_str=`grep -m 1 '## \[v[0-9]\+.[0-9]\+.[0-9]\+*' changelog.txt | cut -f2 -d "[" | cut -f1 -d "]"`

tag_str=$1

if [ $code_str != $changelog_str ]; then
	exit 1
elif [ $changelog_str != $tag_str ]; then
	exit 1
elif [ $tag_str != $code_str ]; then
	exit 1
else
	exit 0
fi
