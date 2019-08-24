while IFS='' read -r line || [[ -n "$line" ]];do
	for word in $line
	do
		echo $word
		if [ "$word" == "sudo" ]
		then
			x="echo $4 | $line"
			eval $x
			break
		else
			eval $line
			break
		fi
	done
done < "requirements.txt"
python3 dbHelperService.py $1 $2 $3 $4