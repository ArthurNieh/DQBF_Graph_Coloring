#!/bin/bash

for (( i=2; i<=5; i=i+1 )); do
# Create an array of sorted benchmarks by numeric instance number
    mapfile -t sorted_benches < <(
        for f in iscas89/benchmarks/s*.bench; do
            num=$(basename "$f" .bench | sed 's/^s//')
            echo "$num $f"
        done | sort -n | awk '{print $2}'
    )

    for bench in "${sorted_benches[@]}"; do	
		echo "##############################"
		# echo ""
		# echo "##############################"
        	echo $bench;

		prefix="iscas89/benchmarks/"
		suffix=".bench"
		ins=${bench#"$prefix"}
		ins=${ins%"$suffix"}

        	echo $bench &> "iscas89/result/${ins}_${i}"  ;
		echo "${ins}" &>> "iscas89/result/${ins}_${i}" 
    		echo "color=${i}" &>> "iscas89/result/${ins}_${i}"
		
		echo "${ins}"
    		echo "color=${i}"

		if [[ "$ins" == "s1423" || "$ins" == "s5378" || "$ins" == "s9234" ]]; then
			echo "$ins skip"
			continue
		fi

		if [[ "$ins" == "s13207" ]]; then
			echo "${ins} skip"
			break
		fi

		./my_iscas.sh "$ins" "$i" &> tmp.out
	done
done
