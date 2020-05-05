file="./changelog.txt"
outfile="changes/txt"

start_line_num=`grep -n -m 1 '## v*' $file | cut -f1 -d:`
end_line_num=`grep -n -m 2 '## v*' $file | tail -n1 | cut -f1 -d:`
end_line_num=`expr $end_line_num - 1`

lines=`head -n$end_line_num $file` 
echo "$lines" > changes.txt
