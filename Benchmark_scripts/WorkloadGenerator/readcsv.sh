while IFS=, read -r col1 col2 col3
do
    echo $col1
    echo $col2
    echo $col3
done < workload.csv