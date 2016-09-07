#!/bin/sh

pacmd list-sink-inputs | grep index | while read line
do
echo "Moving input: ";
echo $line | cut -f2 -d' ';
echo "to sink: $1";
pacmd move-sink-input `echo $line | cut -f2 -d' '` $1
done
