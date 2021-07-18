
echo genere programme observation nouvelle Be

expTime=3600
priority=2
project=NewBe

for star in 'BD+28 4177' 'BD+54 2775' 'BD+57 2581' 'BD+58 310' 'BD+59 2675' 'BD+60 133' 'BD+60 2523' 'BD+60 2645' 'BD+63 1964' 'HD12243' 'HD16485' 'HD179793' 'HD191494' 'HD225859' 'HD237126' 'HD253928' 'HD44783' 'BD+64 106' 'HD151067' 'BD+03 3861' 'HD34906' 'HD40724' 'HD181751' 'HD6676' 'HD189847' 'HD223924' 'HD184061' 'HD9878' 'HD1873'
do
    echo $star
    python3 in-request.py $project "$star" $priority $expTime
    
done


#python3 in-request.py NewBe 'BD+28 4177' 1 3600
