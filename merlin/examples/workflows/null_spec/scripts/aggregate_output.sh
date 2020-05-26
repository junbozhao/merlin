
runs=( 37 )
concurrencies=(1 2 4 8 16 32 64)
samples=(1 10 100 1000 10000)

for run in "${runs[@]}"
    do
    read_path="/p/lustre2/bay1/null_results/run_${run}"
    DATA=my_data${run}.yaml
    touch ${DATA}

    for c in "${concurrencies[@]}"
        do
        for s in "${samples[@]}"
            do
            echo "c${c}_s${s} : " >> ${DATA}
            wf_path="${read_path}/c_$c/s_$s"
            python3 read_output.py ${wf_path}/ $c $s >> ${DATA}
            done
        done
    perl -pi -e 's/ : \n/ : /g' ${DATA}
    done

