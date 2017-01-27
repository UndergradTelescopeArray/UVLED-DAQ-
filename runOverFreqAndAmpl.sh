#!/bin/bash
trap "exit" INT
i=0
for j in {5000..75000..2500}
do
	array[$i]=$j
	i=$i+1
	echo ${array[$j]}
	done

frequencies=()
function checkArray #function to be used in randomizing the frequency array
{
	for item in ${frequencies[@]}
		do
		[[ $item == $1 ]] && return 0
		done
 	return 1
}

while [ "${#frequencies[@]}" -ne "${#array[@]}" ]
do
	rand=$[ $RANDOM % ${#array[@]} ]
	checkArray "${array[$rand]}" || frequencies=(${frequencies[@]} "${array[$rand]}")
	done

echo Frequency order will be
echo ${frequencies[@]}
for freq in ${frequencies[@]}
do
	echo Beginning frequency loop at $freq Hz
	python measure_test.py background -a 0 -f $freq -di $1 -r 2E-9 -m 1 -p 150
	for ampl in {60..160..10}
		do python measure_test.py experiment -a $ampl -f $freq -di $1 -r 2E-9 -m 1 -p 150
	done
done

