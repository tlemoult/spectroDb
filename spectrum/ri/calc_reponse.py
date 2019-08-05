import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
import scipy.ndimage.filters as scipy_filter
import scipy.signal
import sys,json

def load_spc(file):
    """
    Load a spectrum fits file.
    return two nArray for wavelenth in Angstrum and Intensity
    """
    I=fits.getdata(file)
    if I.ndim == 2:
        I=I[0]
    H=fits.getheader(file)

    lam_min=H['CRVAL1']
    lam_delta=H['CDELT1']
    lam_max=lam_min+lam_delta*H['NAXIS1']
    lam=np.arange(lam_min, lam_max, lam_delta)
    lam=lam[0:I.size]   # That, suppoe todo nothing, but, in some file, we need to fix the lenght !
    return (lam,I)

def display_value_spc(lam,flux):
    print(f'  lamba: size={lam.size} val={lam}')
    print(f'  flux : size={flux.size} val={flux}')
    print(f'------')

def describe_spc_multiplan(file):
    hdulist=fits.open(file)
    print(f'This file {file} contains {len(hdulist)} fits plan.')
    for hdu in hdulist:
        print(f'hdu.name={hdu.name}')
        for k,v in hdu.header.items():
            print(f'  {k}={v}  ({hdu.header.comments[k]})')
        print(f'data type {type(hdu.data)}')
        print("----------------")


def load_spc_multi(file,debug=False):
    """
    Load a spectrum fits file.
    return a list of couple nArray for wavelenth in Angstrum and Intensity
    """
    hdulist=fits.open(file)
    print(f'This file {file} contains {len(hdulist)} fits plan.')

    return_value=[]
    for hdu in hdulist:
        
        level='P_1B_'
        if hdu.name.startswith(level):
            #if hdu.name=='P_1B_FULL':
            #    continue
            #if hdu.name=='P_1B_32':
            #    continue
            print(f'  Read hdu name="{hdu.name}"',end='')
            I=hdu.data
            H=hdu.header
            print(f' NAXIS={H["NAXIS1"]} CRVAL1={H["CRVAL1"]}  CDELT1={H["CDELT1"]}')
            lam_min=H['CRVAL1']
            lam_delta=H['CDELT1']
            lam_max=lam_min+lam_delta*(H['NAXIS1']-1)
            lam=np.arange(lam_min, lam_max, lam_delta)
            lam=lam[0:I.size]   # That, suppoe todo nothing, but, in some file, we need to fix the lenght !
            if debug:
                display_value_spc(lam,I)
            return_value.append((lam,I,hdu.name))
    return return_value

def save_spc_multi(file,ldat):
    """
    save the response file for audela pipeline, Merged order and separate order.
    """
    def add_keys_spc(header,lam):
        cdelt=round((lam[10]-lam[0])/10,8)
        header.update({     'CRVAL1' : lam[0],
                            'CDELT1' : cdelt,
                            'NAXIS1' : lam.size, 
                            'NAXIS'  : 1,
                            'CTYPE1' :'Wavelength', 
                            'CUNIT1' :'angstrom',
                            'CRPIX1' : 1,
                            })
        return header
    
    hdu_list= fits.HDUList()
    key_merged_spectrum='P_1B_FULL'
    if key_merged_spectrum in ldat:
        print(f'write PRIMARY hdu')
        lam,flux = ldat[key_merged_spectrum]      
        hdu=fits.PrimaryHDU(flux)
        #hdu.name= 'PRIMARY'
        hdu.header=add_keys_spc(hdu.header,lam)
        hdu.header.update({ 'SIMPLE': True, 'IMAGETYP' : 'RESPONSE' })
        hdu_list.append(hdu)
        del ldat[key_merged_spectrum]   # exclude these data from next

    print(f'write Response in: {file}')
    for name in ldat:
#        print(f'{name},',end='')
        lam,flux = ldat[name]
        hdu=fits.PrimaryHDU(flux)
        hdu.name=name.replace('1B','RESPONSE')
        hdu.header=add_keys_spc(hdu.header,lam)
        hdu.header.update({ 'PCOUNT' : 0,
                                'GCOUNT' : 1,
                                'HDUVERS': 1,
                                'XTENSION': 'IMAGE' })
        hdu_list.append(hdu)

    hdu_list.writeto(file,overwrite=True)

def calc_RI(lam_obs,flux_obs,name,lam_std,flux_std,enable_plot=False,enable_save_plot=False,debug=False):
    """
    Calculate Instrumental response with the observed spectrum and the reference spectrum
    return a tuple:  (lambda,coef_response)
    """
    def lin(lam,lam_min,lam_max,S, delta): 
        """
        linearize the spectrum and the wavalength vectors:
        takes in input the wavelength vector, the lower limit to choose, the upper limit to choose, the flux vector and the new element resolution
        """
        #print(f'linearize delta={delta}')
        i=np.arange(0,len(lam),1.) #we create the pixels vector
        f1=scipy.interpolate.interp1d(i,S) #interpolate pixels against flux
        f2=scipy.interpolate.interp1d(lam,i) #interpolate wavelength against pixels
        lamp=np.arange(lam_min, lam_max, delta) #create an evenly spaced wavelength vector with the new resolution element
        ip=f2(lamp) #find the new pixels solution
        Sp=f1(ip) #apply that to the spectrum
        return lamp,Sp #return the new wavelength vector and the new spectrum, now linearized

    def low_res_gaus(lam,F,new_reso_element):
        "low pass Filter gaussian"
        lam_step=lam[1]-lam[0] # we assert the lam is constant step vector
        new_res=new_reso_element/lam_step #this will be the new pixel axis resolution, must be odd for defining the filter (see next)
        if new_reso_element<lam_step:
            return lam,F
        F=scipy_filter.gaussian_filter1d(F,new_res)
        return lam,F

    def low_res_median(lam,F,new_reso_element):
        "low pass Filter median"
        lam_step=lam[1]-lam[0] # we assert the lam is constant step vector
        new_res=new_reso_element/lam_step #this will be the new pixel axis resolution, must be odd for defining the filter (see next)
        if new_reso_element<lam_step:
            return lam,F
        new_res=int(new_res)
        new_res=new_res+(1-new_res%2)
        F=scipy.signal.medfilt(F,new_res)
        return lam,F

    def cut_spectrum(lam,flux,lam_ex):
        for inf,sup in lam_ex:
            if (inf<lam[0]) |(sup>lam[-1])  :  # we keep data if interval begin before the data sample  or the 
                continue
            
            flux1 = flux[(lam<=inf)|(lam>=sup)]
            lam1 = lam[(lam<=inf)|(lam>=sup)]
            lam=lam1
            flux=flux1
        return lam,flux   

    def fix_zero(flux):
        last_i=flux.nonzero()[0].max()
        first_i=flux.nonzero()[0].min()
        flux[0:first_i]=flux[first_i]
        flux[last_i+1:]=flux[last_i]
        return flux

    def fix_zero_border(lam,flux):
        beg=flux.nonzero()[0][0]     #index inculded
        end=flux.nonzero()[0][-1]+1  #index not included
        #print(f'fix zero border on {len(flux)-(end-beg)} points.')
        return lam[beg:end],flux[beg:end]


    print(f'{name},',end='',flush=True)

    reso_element_low, reso_element_high, reso_final = 6., 0.05, 28
    lam_excluded=[(4318,4370),(4820,4900),(5266,5273),(5271,5278),(6345,6350),
                   (6368,6374),(6525,6600),(6864,6925.5)]
    #lam_excluded=[]

    lam_obs,flux_obs = fix_zero_border(lam_obs,flux_obs)
    if debug:
        display_value_spc(lam_obs,flux_obs)

    # For final :: linearize the standard and the object to have same resolution & # get same limit..
    lam_std_lin,flux_std_lin=lin(lam_std,lam_obs.min(),lam_obs.max(),flux_std, reso_element_high) 
    lam_obs_lin,flux_obs_lin=lin(lam_obs,lam_obs.min(),lam_obs.max(),flux_obs, reso_element_high)
    if debug:
        display_value_spc(lam_obs_lin,flux_obs_lin)

    #cut line in spectrum
    lam_std_cut,flux_std_cut = cut_spectrum(lam_std,flux_std,lam_excluded)
    lam_obs_cut,flux_obs_cut = cut_spectrum(lam_obs,flux_obs,lam_excluded)
    if debug:
        display_value_spc(lam_obs_cut,flux_obs_cut)

    #linearize the standard and the object to have same resolution & # get same limit..
    lam_std1,flux_std1=lin(lam_std_cut,lam_obs.min(),lam_obs.max(),flux_std_cut, reso_element_high) 
    lam_obs1,flux_obs1=lin(lam_obs_cut,lam_obs.min(),lam_obs.max(),flux_obs_cut, reso_element_high)

    #reduce the resolution to get rid of the absorption lines
    lam_std2,flux_std2 = low_res_median(lam_std1,flux_std1,reso_element_low)
    lam_obs2,flux_obs2 = low_res_median(lam_obs1,flux_obs1,reso_element_low)


    #calculating the sensitivity curve
    coef_response=flux_obs2/flux_std2
    lam_filter,coef_reponse_filt= low_res_gaus(lam_obs2,coef_response,reso_final)

    flux_restore = flux_obs_lin/coef_reponse_filt

    #plot all
    if enable_plot or enable_save_plot:
        (fig1,[[ax_obs,ax_std],[ax_resp,ax_restore]]) = plt.subplots(2,2)
        fig1.set_size_inches(16, 10)
        fig1.suptitle('RI for '+name)
        ax_obs.set_title('observation without RI')
        ax_obs.plot(lam_obs,flux_obs,'r-',lam_obs1,flux_obs1,'k-',lam_obs2,flux_obs2,'b-')
        ax_obs.set_ylim(bottom=0)

        ax_std.set_title('reference spectrum')
        ax_std.plot(lam_std_lin,flux_std_lin,'r-',lam_std_lin,flux_std1,'k-',lam_std_lin,flux_std2,'b-')
        ax_std.set_ylim(bottom=0)

        ax_resp.set_title('RI')
        ax_resp.plot(lam_obs2,coef_response,'r-',lam_obs2,coef_reponse_filt,'k')
        ax_resp.set_ylim(bottom=0)

        ax_restore.set_title('observation+RI vs reference')
        ax_restore.plot(lam_obs_lin,flux_restore,'k-',lam_obs_lin,flux_std_lin,'b-')
        ax_restore.set_ylim(bottom=0)
        if enable_plot and not enable_save_plot:
            plt.show()
        elif enable_save_plot:
            plt.savefig('fig/'+name+'.png')
        plt.close(fig1)

    return { name: [lam_obs2,coef_reponse_filt] }

# main code here 
if len(sys.argv)!=2:
    print("syntax:\n    python3 calc_reponse.py resp.json")
    exit()
config = json.loads(open(sys.argv[1]).read())
print(config)

#describe_spc_multiplan(r'./org/reponse.fit')

lam_std,flux_std = load_spc(config['refFileName'])
#lam_std,flux_std = load_spc(r'./org/HD39283.fits')

obsFilename=config['obsFilename']
print(f"Load observation {obsFilename}")
observationLst=load_spc_multi(obsFilename)

print("\nCalc Response")
ri=dict([])
for lam_obs,flux_obs,name in observationLst:
    ri.update( calc_RI(lam_obs,flux_obs,name,lam_std,flux_std,enable_plot=False,enable_save_plot=True))

#TODO, renormer... pour un maximum de RI global et par ordre a environ 1.
print("\nRescale value")
mean_ri_order=np.array([ ri[name][1].mean() for name in ri if not name.endswith('_FULL') ]).mean()
print(f'moys={mean_ri_order}')
for name in ri:
    if not name.endswith('_FULL'):
        ri[name][1]=10.*ri[name][1]/mean_ri_order

save_spc_multi(config['responseOutFileName'],ri)
#describe_spc_multiplan('Newreponse.fits')