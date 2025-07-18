import mesa_reader as mr
import matplotlib.pyplot as plt

plt.rc('font', weight='bold')
plt.rc('xtick.major', size=5, pad=10)
plt.rc('ytick.major', size=5, pad=10)
plt.rc('xtick.minor', size=2.5, pad=10)
plt.rc('ytick.minor', size=2.5, pad=10)

fig = plt.figure(figsize=(6,4))

ax1 = fig.add_axes([0.1,0.1,0.87,0.87])
ax1.minorticks_on()
ax1.tick_params(axis='both', which='major', labelsize=8,pad=5,direction='in',bottom=True, top=True, left=True, right=True)
ax1.tick_params(axis='both', which='minor', labelsize=4,pad=5,direction='in',bottom=True, top=True, left=True, right=True)

# load and plot data
h = mr.MesaData('history_1p00.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.00M_{\odot}$')

h = mr.MesaData('history_1p05.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.05M_{\odot}$')

h = mr.MesaData('history_1p10.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.10M_{\odot}$')

h = mr.MesaData('history_1p15.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.15M_{\odot}$')

h = mr.MesaData('history_1p20.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.20M_{\odot}$')

h = mr.MesaData('history_1p25.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.25M_{\odot}$')

h = mr.MesaData('history_1p30.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.30M_{\odot}$')

h = mr.MesaData('history_1p35.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.35M_{\odot}$')

h = mr.MesaData('history_1p40.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.40M_{\odot}$')

h = mr.MesaData('history_1p45.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.45M_{\odot}$')

h = mr.MesaData('history_1p50.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.50M_{\odot}$')

h = mr.MesaData('history_1p55.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.55M_{\odot}$')

h = mr.MesaData('history_1p60.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.60M_{\odot}$')

h = mr.MesaData('history_1p65.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.65M_{\odot}$')

h = mr.MesaData('history_1p70.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.70M_{\odot}$')

h = mr.MesaData('history_1p75.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.75M_{\odot}$')

h = mr.MesaData('history_1p80.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.80M_{\odot}$')

h = mr.MesaData('history_1p85.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.85M_{\odot}$')

h = mr.MesaData('history_1p90.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.90M_{\odot}$')

h = mr.MesaData('history_1p95.data')
plt.plot(h.log_Teff, h.log_L, label=r'$1.95M_{\odot}$')

# set axis labels
plt.xlabel(r'$\log(T_{\rm eff})$')
plt.ylabel(r'$\log(L/L_{\odot})$')

plt.xlim(3.65,3.667)
plt.ylim(1,2)
plt.xticks([3.65,3.655,3.66,3.665])

# invert the x-axis
plt.gca().invert_xaxis()
plt.legend(loc='lower right', ncol=4, fontsize=6)
#plt.show()
plt.savefig("HRD_RGBB.png")
