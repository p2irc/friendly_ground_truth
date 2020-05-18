file="./changelog.txt"
outfile="changes.txt"

start_line_num=`grep -n -m 1 '## \[v[0-9]\+.[0-9]\+.[0-9]\+*' $file | cut -f1 -d:`
end_line_num=`grep -n -m 2 '## \[v[0-9]\+.[0-9]\+.[0-9]\+*' $file | tail -n1 | cut -f1 -d:`
end_line_num=`expr $end_line_num - 1`

lines=`head -n$end_line_num $file`
num=`expr $end_line_num - $start_line_num`
lines=`echo "$lines" | tail -n$num`
echo "$lines" > changes.txt
