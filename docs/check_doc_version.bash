major_num=`grep "VERSION_MAJOR = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`
minor_num=`grep "VERSION_MINOR = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`
patch_num=`grep "VERSION_PATCH = " ../friendly_ground_truth/version_info.py | cut -f2 -d "=" | tr -d "[:space:]"`

doc_major_num=`grep -m 1 "VERSION_MAJOR = " ./html/friendly_ground_truth/version_info.html | cut -f2 -d "=" | tr -d "[:space:]"`
doc_minor_num=`grep -m 1 "VERSION_MINOR = " ./html/friendly_ground_truth/version_info.html  | cut -f2 -d "=" | tr -d "[:space:]"`
doc_patch_num=`grep -m 1 "VERSION_PATCH = " ./html/friendly_ground_truth/version_info.html | cut -f2 -d "=" | tr -d "[:space:]"`

if [ $major_num -ne $doc_major_num ]; then
	exit 1
fi

if [ $minor_num -ne $doc_minor_num ]; then
	exit 1
fi

if [ $patch_num -ne $doc_patch_num ]; then
	exit 1
fi

exit 0
