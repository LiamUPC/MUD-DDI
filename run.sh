#! /bin/bash

BASEDIR=../../lab_resources/DDI/
#BASEDIR=../lab1/DDI/

./corenlp-server.sh -quiet true -port 9000 -timeout 15000  &
sleep 1

exit

# extract features
echo "Extracting features"
python3 -i extract-features.py $BASEDIR/data/devel/ > devel.cod &
#python3 extract-features.py $BASEDIR/data/train/ | tee train.cod | cut -f4- > train.cod.cl

kill `cat /tmp/corenlp-server.running`

# train model
echo "Training model"
python3 train-sklearn.py model.joblib vectorizer.joblib < train.cod.cl
# run model
echo "Running model..."
python3 predict-sklearn.py model.joblib vectorizer.joblib < devel.cod > devel.out
# evaluate results
echo "Evaluating results..."
python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel.stats

SAVEFILE=experiments.txt
i=`grep "#### EXPERIMENT" $SAVEFILE | wc -l`
echo "#### EXPERIMENT $i ####" >> $SAVEFILE
cat devel.stats >> $SAVEFILE
echo "#######################" >> $SAVEFILE
