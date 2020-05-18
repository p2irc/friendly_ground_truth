git diff $1 $2 --quiet -- changelog.txt

if [ $? -eq 0 ]; then
	exit 1
else
	exit 0
fi
