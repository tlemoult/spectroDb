from astropy.time import Time

def formatPhase(phase):
    return "{:.2f}".format(round(phase, 2))


def phase_RR_jd(jd):

    ephem = { 
         '1994' : {'jd0': 2449572.4800   , 'per': 0.5668174} ,
         '2013' : {'jd0': 2456539.34275  , 'per': 0.5667975} ,
         '2014' : {'jd0': 2456914.5507   , 'per': 0.56684} ,
         '2015' : {'jd0': 2457286.3558   , 'per': 0.566793} ,
         '2016' : {'jd0': 2457597.5159   , 'per': 0.566793} ,
         '2017' : {'jd0': 2457861.6319   , 'per': 0.566793} ,
         '2018' : {'jd0': 2458349.6240   , 'per': 0.566793} ,
         '2019' : {'jd0': 2458709.5227   , 'per': 0.566793} ,
         '2020' : {'jd0': 2458976.4722   , 'per': 0.566793} ,
         'default' : {'jd0': 2456263.3118055556 , 'per':0.566782}
    }

    year=str(int(Time(jd , scale='tt',format='jd').to_value('jyear')))
    jd0=ephem[year]['jd0']
    per=ephem[year]['per']
    newPhi = (jd-jd0)/per
    newPhiFrac = newPhi - int(newPhi)
    if newPhiFrac<0:
        newPhiFrac=newPhiFrac+1

    return newPhiFrac

def phase_RR_blasko_jd(jd):

    ephem = {
        '1994' : {'jd0b': 2449631.312 , 'perb': 39.06 },
        '2013' : {'jd0b': 2456464.481, 'perb': 39.0},
        '2014' : {'jd0b': 2456881.627, 'perb': 39.0},
        '2015' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2016' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2017' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2018' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2019' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2020' : {'jd0b': 2457354.322, 'perb': 39.0},
        'default' : {'jd0b': 2456846.489, 'perb': 39.0}
    }

    year=str(int(Time(jd , scale='tt',format='jd').to_value('jyear')))
    jd0b=ephem[year]['jd0b']
    perb=ephem[year]['perb']
    newPsi = (jd-jd0b)/perb
    newPsiFrac = newPsi - int(newPsi)
    if newPsiFrac<0:
        newPsiFrac=newPsiFrac+1

    return newPsiFrac
