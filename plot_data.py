import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle
import xarray as xr

mpl.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 15
plt.rcParams['xtick.top'] = False
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.right'] = False
plt.rcParams['ytick.direction'] = 'out'
plt.rcParams['grid.linewidth'] = 1.5
plt.rcParams['axes.grid']=True
yd = {'rotation': 0, 'ha': 'right', 'va': 'center'}
plt.rcParams.update({
    'axes.linewidth': 1.5,          # Thickness of the axes (spines)
    'xtick.major.width': 1.5,       # Thickness of major x-ticks
    'ytick.major.width': 1.5,       # Thickness of major y-ticks
    'xtick.major.size': 6,          # Length of major x-ticks
    'ytick.major.size': 6,          # Length of major y-ticks
    'xtick.minor.width': 1,         # Thickness of minor x-ticks
    'ytick.minor.width': 1,         # Thickness of minor y-ticks
    'xtick.minor.size': 4,          # Length of minor x-ticks
    'ytick.minor.size': 4,          # Length of minor y-ticks
})



'''
    Make subplots for article comparing LES and RANS.
    
    Python environment:
        conda create -n blm2025 python spyder numpy scipy xarray matplotlib
'''

###############################################
### Load EARSM data
###############################################
with open('EARSM/cnbl_Gam0.001.pkl', 'rb') as fp:
    c1 = pickle.load(fp)
with open('EARSM/cnbl_Gam0.003.pkl', 'rb') as fp:
    c3 = pickle.load(fp)
with open('EARSM/cnbl_Gam0.009.pkl', 'rb') as fp:
    c9 = pickle.load(fp)
rans = [c1, c3, c9]

###############################################
### Load reference LES data
###############################################
# Nek (Deardorf TKE)
lesT1 = xr.open_dataset("LES/neutral_gamma0001_tke.nc")
lesT3 = xr.open_dataset("LES/neutral_gamma0003_tke.nc")
lesT9 = xr.open_dataset("LES/neutral_gamma0009_tke.nc")
lesTs = [lesT1, lesT3, lesT9]
# Nek (Vreman)
lesV = xr.open_dataset("LES/neutral_gamma0003_vreman.nc")
# NCAR
lesN = xr.open_dataset("LES/neutral_gamma0003_ncar.nc")
# Linestyles
lnsty    = {'color': 'k', 'label': 'NCAR', 'linewidth': 3}
lvsty    = {'color': "#89ce00", 'label': 'Vreman', 'linewidth': 3}
ltsty    = {'color': "#e6308a", 'label': 'Deardorf', 'linewidth': 3}


#########################################################################
############# BL heights ###########################################
#########################################################################
def bl_height_dtdz(T,z):
    # Method 1 (max temperature gradient)
    dTdz = np.gradient(T,z)
    dTdz = np.nan_to_num(dTdz)
    idx_max = np.argmax(dTdz)
    z_BL_top = z[idx_max]
    return z_BL_top

# Find top of BL (point at which dTdz is maximum)
ziRANS = []
ziLES = []

for i in range(len(rans)):
    # RANS
    ransdata = rans[i]
    ranst = ransdata['msol']['T'].squeeze()  # to convert from (257,1) to (257)
    ransz = ransdata['y']['yc']
    ziRANS.append(bl_height_dtdz(ranst, ransz))
    
    #LES
    lesdata = lesTs[i]
    ziLES.append(bl_height_dtdz(lesdata['T'], lesdata['z']))
        
ziRANS = np.array(ziRANS)
ziLES = np.array(ziLES)


#########################################################################
############# Plots ###########################################
#########################################################################
fisty = {'color': 'c', 'linewidth': 3, 'linestyle': 'dashed'}
blrsty = {'color': 'c', 'linewidth': 3, 'linestyle': 'dotted'}
bllsty = {'color': "#e6308a", 'linewidth': 3, 'linestyle': 'dotted'}


# Plot profiles
def mplot(xlabel,xlim='None',varloc='None',sharex=True):
    reduce = 0.9
    fig, ax = plt.subplots(1, 3, sharex=sharex, sharey=True, figsize=(reduce*9, reduce*4))
    ax = ax.flatten()
    ax[1].set_xlabel(xlabel)
    ax[0].set_ylabel(r'$z$ [m]',**yd)
    ax[0].set_ylim(0,850)
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(50))
    if xlim == 'None':
        pass
    else:    
        plt.xlim(xlim[0],xlim[1])
    if varloc == 'None':
        pass
    else:
        plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(varloc))
    # Add labels
    fig.text(0.135,0.92,r"$\bf{(a)}$",ha='center', fontsize=15)
    fig.text(0.41,0.92,r"$\bf{(b)}$",ha='center', fontsize=15)
    fig.text(0.685,0.92,r"$\bf{(c)}$",ha='center', fontsize=15)
    
    return fig
    

# Combine U and V
mplot(xlabel=r'$U$ and $V$ [m s$^{-1}$]',xlim=[-1,11],varloc=1)
plt.gcf().axes[1].plot(lesN['U'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['U'],lesV['z'],**lvsty)
plt.gcf().axes[1].plot(lesN['V'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['V'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['U'],lesT['z'],**ltsty)
    plt.gcf().axes[i].plot(lesT['V'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['U'],c['y']['yc'],**fisty)
    plt.gcf().axes[i].plot(c['msol']['V'],c['y']['yc'],**fisty)
plt.gcf().axes[0].annotate(text=r'$U$',xy=(0.8,0.8),xycoords='axes fraction')
plt.gcf().axes[0].annotate(text=r'$V$',xy=(0.22,0.8),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$U$',xy=(0.79,0.6),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$V$',xy=(0.28,0.6),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$U$',xy=(0.75,0.4),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$V$',xy=(0.4,0.4),xycoords='axes fraction')
plt.gcf().savefig('U_and_V.png',dpi=300,bbox_inches='tight')


# Wind direction
mplot(xlabel=r'$\varphi$ [$^\circ$]',xlim=[-3,40],varloc=5)
plt.gcf().axes[1].plot(lesN['winddir'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['winddir'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['winddir'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(180/np.pi*np.arctan2(c['msol']['V'][1:],c['msol']['U'][1:]),c['y']['yc'][1:],**fisty)


# T
mplot(xlabel=r'$\Theta$ [K]',xlim=[265,269],varloc=0.5)
plt.gcf().axes[1].plot(lesN['T'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['T'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['T'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['T'],c['y']['yc'],**fisty)    


# TKE
mplot(xlabel=r'$K$ [m$^{2}$ s$^{-2}$]',varloc=0.1)
plt.gcf().axes[1].plot(lesN['K'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['K'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['K'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['K'],c['y']['yc'],**fisty)    


# Kt
em2 = 1e-2
mplot(xlabel=r'$K_\theta$ [$10^{-2}\times$ K$^{2}$]',sharex=False)
plt.gcf().axes[1].plot(lesN['Kt']/em2,lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['Kt']/em2,lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    ax = plt.gcf().axes[i]
    plt.gcf().axes[i].plot(lesT['Kt']/em2,lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['Kt']/em2,c['y']['yc'],**fisty)  
    # BL height (based on dTdz)
    ax.set_xlim(ax.get_xlim())
    ax.plot(ax.get_xlim(),[ziLES[i],ziLES[i]],**bllsty)
    ax.plot(ax.get_xlim(),[ziRANS[i],ziRANS[i]],**blrsty)
    
plt.gcf().axes[0].xaxis.set_minor_locator(plt.MultipleLocator(0.02))
plt.gcf().axes[1].xaxis.set_minor_locator(plt.MultipleLocator(0.1))
plt.gcf().axes[2].xaxis.set_minor_locator(plt.MultipleLocator(0.5))


# Shear stresses
mplot(xlabel=r'$\overline{uw}$ and $\overline{vw}$ [m$^{2}$ s$^{-2}$]',xlim=[-0.20,0.05],varloc=0.02)
plt.gcf().axes[1].plot(lesN['uw'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['uw'],lesV['z'],**lvsty)
plt.gcf().axes[1].plot(lesN['vw'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['vw'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['uw'],lesT['z'],**ltsty)
    plt.gcf().axes[i].plot(lesT['vw'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['uw_out'],c['y']['yc'],**fisty)
    plt.gcf().axes[i].plot(c['msol']['vw_out'],c['y']['yc'],**fisty)
plt.gcf().axes[0].annotate(text=r'$\overline{uw}$',xy=(0.25,0.35),xycoords='axes fraction')
plt.gcf().axes[0].annotate(text=r'$\overline{vw}$',xy=(0.7,0.1),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{uw}$',xy=(0.3,0.32),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{vw}$',xy=(0.7,0.1),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{uw}$',xy=(0.4,0.3),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{vw}$',xy=(0.7,0.1),xycoords='axes fraction')

# Horizontal shear stres
mplot(xlabel=r'$\overline{uv}$ [m$^{2}$ s$^{-2}$]',xlim=[-0.05,0.2],varloc=0.02)
plt.gcf().axes[1].plot(lesN['uv'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['uv'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['uv'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['uv_out'],c['y']['yc'],**fisty)


# Normal stresses
mplot(xlabel=r'$\overline{uu}$ and $\overline{ww}$ [m$^{2}$ s$^{-2}$]',xlim=[0,0.9],varloc=0.1)
plt.gcf().axes[1].plot(lesN['uu'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['uu'],lesV['z'],**lvsty)
plt.gcf().axes[1].plot(lesN['ww'],lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['ww'],lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['uu'],lesT['z'],**ltsty)
    plt.gcf().axes[i].plot(lesT['ww'],lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['uu_out'],c['y']['yc'],**fisty)
    plt.gcf().axes[i].plot(c['msol']['ww_out'],c['y']['yc'],**fisty)
plt.gcf().axes[0].annotate(text=r'$\overline{ww}$',xy=(0.02,0.1),xycoords='axes fraction')
plt.gcf().axes[0].annotate(text=r'$\overline{uu}$',xy=(0.5,0.2),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{ww}$',xy=(0.01,0.1),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{uu}$',xy=(0.47,0.2),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{ww}$',xy=(0.01,0.05),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{uu}$',xy=(0.4,0.16),xycoords='axes fraction')



# wt
mplot(xlabel=r'$\overline{w \theta}$ [$10^{-2}\times$ K m s$^{-1}$]',varloc=0.04)
plt.gcf().axes[1].plot(lesN['wt']/em2,lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['wt']/em2,lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['wt']/em2,lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['wt_out']/em2,c['y']['yc'],**fisty)    
plt.gcf().axes[0].set_xticks([-0.4,-0.2,0])



# Both horizontal heatfluxes
mplot(xlabel=r'$\overline{u \theta}$ and $\overline{v \theta}$ [$10^{-2}\times$ K m s$^{-1}$]',sharex=False)
# ut
plt.gcf().axes[1].plot(lesN['ut']/em2,lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['ut']/em2,lesV['z'],**lvsty)
# vt
plt.gcf().axes[1].plot(lesN['vt']/em2,lesN['z'],**lnsty)
plt.gcf().axes[1].plot(lesV['vt']/em2,lesV['z'],**lvsty)
for i in range(len(rans)):
    lesT = lesTs[i]
    plt.gcf().axes[i].plot(lesT['ut']/em2,lesT['z'],**ltsty)
    plt.gcf().axes[i].plot(lesT['vt']/em2,lesT['z'],**ltsty)
    c = rans[i]
    plt.gcf().axes[i].plot(c['msol']['ut_out']/em2,c['y']['yc'],**fisty) 
    plt.gcf().axes[i].plot(c['msol']['vt_out']/em2,c['y']['yc'],**fisty)  
plt.gcf().axes[0].xaxis.set_minor_locator(plt.MultipleLocator(0.1))
plt.gcf().axes[1].xaxis.set_minor_locator(plt.MultipleLocator(0.4))
plt.gcf().axes[2].xaxis.set_minor_locator(plt.MultipleLocator(1))
plt.gcf().axes[2].set_xlim(right=4)
plt.gcf().axes[0].annotate(text=r'$\overline{u \theta}$',xy=(0.82,0.78),xycoords='axes fraction')
plt.gcf().axes[0].annotate(text=r'$\overline{v \theta}$',xy=(0.5,0.5),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{u \theta}$',xy=(0.86,0.61),xycoords='axes fraction')
plt.gcf().axes[1].annotate(text=r'$\overline{v \theta}$',xy=(0.6,0.38),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{u \theta}$',xy=(0.86,0.47),xycoords='axes fraction')
plt.gcf().axes[2].annotate(text=r'$\overline{v \theta}$',xy=(0.6,0.33),xycoords='axes fraction')

