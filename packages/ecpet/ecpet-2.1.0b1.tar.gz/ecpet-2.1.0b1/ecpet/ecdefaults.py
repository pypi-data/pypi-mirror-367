########################################
#
# ec-frame default configuration
#
########################################
#
defaults = {
    'ConfName': {
        'type': 'str',
        'value': "current.conf",
        'short': "Config Name",
        'comment': "configuration file name"},
    #
    # input data file names
    'RawDir': {
        'type': 'str',
        'value': "in",
        'short': "Raw Data Dir",
        'comment': "directory where to find data files"},
    'RawFormat': {
        'type': 'str',
        'value': "toa5",
        'short': "Raw Data Format",
        'comment': "format of input data files"},
    'RawFastData': {
        'type': 'str',
        'value': "*ts*",
        'short': "Fast Data Files",
        'comment': "space-separated list of files in RawDir (or glob patterns)"},
    'RawSlowData': {
        'type': 'str',
        'value': "*rpv*",
        'short': "Slow Data Files",
        'comment': "space-separated list of files in RawDir (or glob patterns)"},
    #
    # averaging intervals
    'AvgInterval': {
        'type': 'int',
        'value': "1800",
        'short': "Avg Interval (s)",
        'comment': "averaging interval in seconds"},
    'PlfitInterval': {
        'type': 'int',
        'value': "7",
        'short': "Plfit Interval (d)",
        'comment': "planar-fit interval in days"},
    #
    # time period to process (empty string = automatic)
    'DateBegin': {
        'type': 'str',
        'value': "",
        'short': "Start Date/Time",
        'comment': "Beginning time of the period to process, format: yyyy/mm/dd-hh:mm:ss.ss"},
    'DateEnd': {
        'type': 'str',
        'value': "",
        'short': "End Date/Time",
        'comment': "End time of the period to process, format: yyyy/mm/dd-hh:mm:ss.ss"},
    #
    # output files
    'OutDir': {
        'type': 'str',
        'value': "out",
        'short': "Output Dir",
        'comment': "Directory for output files (flux files, intermediate result file, flags files)"},
    'FluxName': {
        'type': 'str',
        'value': "ec-flux.dat",
        'short': "Flux Output File",
        'comment': "Name of ECPACK flux output file"},
    'QCOutName': {
        'type': 'str',
        'value': "qc-flux.dat",
        'short': "QC Output File",
        'comment': "quality-controlled flux data output file"},
    #
    # ---------------------------------------
    #  format of input files
    #  (order of columns)
    # ---------------------------------------
    #
    'fastfmt.U_col': {
        'type': 'int',
        'value': "3",
        'short': "U Component",
        'comment': "Wind along device x axis in m/s"},
    'fastfmt.V_col': {
        'type': 'int',
        'value': "4",
        'short': "V Component",
        'comment': "Wind along device y axis in m/s"},
    'fastfmt.W_col': {
        'type': 'int',
        'value': "5",
        'short': "W Component",
        'comment': "Wind along device z axis in m/s"},
    'fastfmt.Tsonic_col': {
        'type': 'int',
        'value': "8",
        'short': "Sonic Temperature",
        'comment': "Sonic temperature in °C"},
    'fastfmt.Tcouple_col': {
        'type': 'int',
        'value': "0",
        'short': "Thermocouple",
        'comment': "Thermocouple temperature column"},
    'fastfmt.Humidity_col': {
        'type': 'int',
        'value': "7",
        'short': "Humidity",
        'comment': "Water vapor density in g/m³"},
    'fastfmt.CO2_col': {
        'type': 'int',
        'value': "6",
        'short': "CO₂",
        'comment': "CO₂ concentration column"},
    'fastfmt.Press_col': {
        'type': 'int',
        'value': "9",
        'short': "Pressure",
        'comment': "Air pressure in kPa"},
    'fastfmt.diag_col': {
        'type': 'int',
        'value': "10",
        'short': "CSAT Diagnostic",
        'comment': "CSAT3 diagnostic word"},
    'fastfmt.agc_col': {
        'type': 'int',
        'value': "11",
        'short': "IRGA Diagnostic",
        'comment': "LiCor diagnostic word"},
    #
    'fastfmt.U_nam': {
        'type': 'str',
        'value': "",
        'short': "U Component",
        'comment': "Name of u-velocity variable in TOA5 column definition"},
    'fastfmt.V_nam': {
        'type': 'str',
        'value': "",
        'short': "V Component",
        'comment': "Name of v-velocity variable in TOA5 column definition"},
    'fastfmt.W_nam': {
        'type': 'str',
        'value': "",
        'short': "W Component",
        'comment': "Name of w-velocity variable in TOA5 column definition"},
    'fastfmt.Tsonic_nam': {
        'type': 'str',
        'value': "",
        'short': "Sonic Temperature",
        'comment': "Name of sonic temperature variable in TOA5 column definition"},
    'fastfmt.Tcouple_nam': {
        'type': 'str',
        'value': "",
        'short': "Thermocouple",
        'comment': "Thermocouple column name in input files"},
    'fastfmt.Humidity_nam': {
        'type': 'str',
        'value': "",
        'short': "Humidity",
        'comment': "Name of humidity variable in TOA5 column definition"},
    'fastfmt.CO2_nam': {
        'type': 'str',
        'value': "",
        'short': "CO₂",
        'comment': "Name of CO₂ variables in TOA5 column definition"},
    'fastfmt.Press_nam': {
        'type': 'str',
        'value': "",
        'short': "Pressure",
        'comment': "Pressure column name in input files"},
    'fastfmt.diag_nam': {
        'type': 'str',
        'value': "",
        'short': "CSAT Diagnostic",
        'comment': "Name of diagnostic variable TOA5 column definition"},
    'fastfmt.agc_nam': {
        'type': 'str',
        'value': "",
        'short': "IRGA Diagnostic",
        'comment': "LiCor diagnostic column name in input files"},
    #
    'slowfmt.Tref_col': {
        'type': 'int',
        'value': "3",
        'short': "Ref Temperature",
        'comment': "Air temperature in °C"},
    'slowfmt.RelHum_col': {
        'type': 'int',
        'value': "4",
        'short': "Rel Humidity",
        'comment': "Relative humidity in percent"},
    'slowfmt.Pref_col': {
        'type': 'int',
        'value': "6",
        'short': "Ref Pressure",
        'comment': "Air pressure in hPa"},
    #
    'slowfmt.Tref_nam': {
        'type': 'str',
        'value': "",
        'short': "Ref Temperature",
        'comment': "Air temperature column name in input files"},
    'slowfmt.RelHum_nam': {
        'type': 'str',
        'value': "",
        'short': "Rel Humidity",
        'comment': "Relative humidity column name in input files"},
    'slowfmt.Pref_nam': {
        'type': 'str',
        'value': "",
        'short': "Ref Pressure",
        'comment': "Air pressure column name in input files"},
    #
    # ---------------------------------------
    #  internal settings
    # ---------------------------------------
    #
    'nproc': {
        'type': 'int',
        'value': "0",
        'short': "Processes",
        'comment': "parallel processes (0=auto)"},
    #
    # directories
    'ExeDir': {
        'type': 'str',
        'value': "",
        'short': "Executable Dir",
        'comment': "executables directory"},
    'DatDir': {
        'type': 'str',
        'value': "work",
        'short': "Working Dir",
        'comment': "Directory for data files"},
    'Parmdir': {
        'type': 'str',
        'value': ".",
        'short': "Parameters Dir",
        'comment': "Directory for parameter file (processing parameters, calibration files, interval files)"},
    #
    # file names
    'ec_pre': {
        'type': 'str',
        'value': "ec_pre",
        'short': "Pre-processor",
        'comment': "default file name"},
    'ec_fit': {
        'type': 'str',
        'value': "planang",
        'short': "Planar Fit",
        'comment': "default file name"},
    'ec_calc': {
        'type': 'str',
        'value': "ec_ncdf",
        'short': "Calculator",
        'comment': "default file name"},
    'ec_post': {
        'type': 'str',
        'value': "ec_post",
        'short': "Post-processor",
        'comment': "default file name"},
    'PlfIntName': {
        'type': 'str',
        'value': "inter-plfit.dat",
        'short': "Plfit Intermediate",
        'comment': "default file name"},
    'InterName': {
        'type': 'str',
        'value': "inter-ec.dat",
        'short': "Intermediate File",
        'comment': "Name of interval file"},
    'PlfName': {
        'type': 'str',
        'value': "planang.dat",
        'short': "Planar Angles",
        'comment': "default file name"},
    #
    # netcdf variable names
    'U_var': {
        'type': 'str',
        'value': "Ux",
        'short': "U Variable",
        'comment': "Name of u-velocity variable in TOA5 column definition, will be used also for the NetCDF file"},
    'V_var': {
        'type': 'str',
        'value': "Uy",
        'short': "V Variable",
        'comment': "Name of v-velocity variable in TOA5 column definition, will be used also for the NetCDF file"},
    'W_var': {
        'type': 'str',
        'value': "Uz",
        'short': "W Variable",
        'comment': "Name of w-velocity variable in TOA5 column definition, will be used also for the NetCDF file"},
    'Tsonic_var': {
        'type': 'str',
        'value': "Ts",
        'short': "Ts Variable",
        'comment': "Name of sonic temperature variable in TOA5 column definition, will be used also for the NetCDF file"},
    'Tcouple_var': {
        'type': 'str',
        'value': "Tcoup",
        'short': "Tcoup Variable",
        'comment': "intermediate file variable name"},
    'Humidity_var': {
        'type': 'str',
        'value': "h2o",
        'short': "H2O Variable",
        'comment': "Name of humidity variable in TOA5 column definition, will be used also for the NetCDF file"},
    'CO2_var': {
        'type': 'str',
        'value': "co2",
        'short': "CO2 Variable",
        'comment': "Name of CO₂ variables in TOA5 column definition, will be used also for the NetCDF file"},
    'Press_var': {
        'type': 'str',
        'value': "Press",
        'short': "Press Variable",
        'comment': "intermediate file variable name"},
    'Hourmin_var': {
        'type': 'str',
        'value': "hour_min",
        'short': "Hour/Min Variable",
        'comment': "Name of hour/minute variable in NetCDF file"},
    'Doy_var': {
        'type': 'str',
        'value': "doy",
        'short': "DOY Variable",
        'comment': "Name of day of year variable in NetCDF file"},
    'sec_var': {
        'type': 'str',
        'value': "sec",
        'short': "Seconds Variable",
        'comment': "Name of seconds variable in NetCDF"},
    'year_var': {
        'type': 'str',
        'value': "year",
        'short': "Year Variable",
        'comment': "intermediate file variable name"},
    'diag_var': {
        'type': 'str',
        'value': "diag_csat",
        'short': "Diag Variable",
        'comment': "Name of diagnostic variable TOA5 column definition, will be used also for the NetCDF file"},
    'agc_var': {
        'type': 'str',
        'value': "diag_irga",
        'short': "AGC Variable",
        'comment': "intermediate file variable name"},
    #
    #
    'QCdisable': {
        'type': 'str',
        'value': "fkm",
        'short': "QC Disable",
        'comment': "Space-separated list of quality control tests to disable for faster processing"},
    'PreOutFormat': {
        'type': 'str',
        'value': "",
        'short': "Output Format",
        'comment': "intermediate file format: possible values: NetCDF TOA5"},
    'Despiking': {'type': 'str',
                  'value': "mad",
                  'short': "Despiking Method",
                  'comment': "Select despiking method: spk=Vickers&Mahrt, chr=change rate, mad=median absolute deviation"},
    'Qflags': {
        'type': 'str',
        'value': "",
        'short': "Quality Flags",
        'comment': "Select special ways to treat diagnostic words: noirga, Campbell"},
    'InstLatLon': {
        'type': 'str',
        'value': "",
        'short': "Latitude, Longitude",
        'comment': "Position of the Instrument: space-separated list of latitude and longitude in degrees"},
    'SourceArea': {
        'type': 'str',
        'value': "",
        'short': "Source Area File",
        'comment': "Name (including path) of area-of-interest file containing the definition of the targeted source area"},
    'Displacement': {
        'type': 'float',
        'value': "",
        'short': "Displacement (m)",
        'comment': "Aerodynamic displacement height at the instrument site"},
    'ExcludeSector': {
        'type': 'str',
        'value': "",
        'short': "Exclude Sectors",
        'comment': "Definition of excluded sectors (space-separated start and end in degrees from north)"},
    #
    # ---------------------------------------
    # preprocessor setting
    # ---------------------------------------
    #
    # slow reference consitency limits
    'qcconf.limrrfl': {
        'type': 'float',
        'value': '0.',
        'short': "RH Lower Limit"},
    'qcconf.limrrfh': {
        'type': 'float',
        'value': '100.',
        'short': "RH Upper Limit"},
    'qcconf.limrtcl': {
        'type': 'float',
        'value': '-30.',
        'short': "Temp Lower Limit"},
    'qcconf.limrtch': {
        'type': 'float',
        'value': '50.',
        'short': "Temp Upper Limit"},
    'qcconf.limrppl': {
        'type': 'float',
        'value': '750.',
        'short': "Press Lower Lim"},
    'qcconf.limrpph': {
        'type': 'float',
        'value': '1100.',
        'short': "Press Upper Lim"},
    # instrument flags
    'qcconf.csatmask': {
        'type': 'int',
        'value': "61440",
        'short': "CSAT Mask",
        'comment': "Hi bits must be lo in CSAT diagnostic word"},
    'qcconf.irgamask': {
        'type': 'int',
        'value': "240",
        'short': "IRGA Mask",
        'comment': "Hi bits must be hi in LiCor diagnostic word"},
    'qcconf.agclimit': {
        'type': 'float',
        'value': "70.",
        'short': "AGC Limit",
        'comment': "Max. accepted value for LiCor auto gain control"},
    # 1 spikes  (using window width L1)
    'qcconf.L1': {
        'type': 'float',
        'value': "300.",
        'short': "Window Length (s)",
        'comment': "Averaging subrecord width in s"},
    'qcconf.spth': {
        'type': 'float',
        'value': "3.5",
        'short': "Threshold (σ)",
        'comment': "Threshold in standard deviations for first pass"},
    'qcconf.spin': {
        'type': 'float',
        'value': "0.2",
        'short': "Threshold Incr",
        'comment': "Threshold increment per pass in standard deviations"},
    'qcconf.spco': {
        'type': 'int',
        'value': "3",
        'short': "Max Consecutive",
        'comment': "Max. number of consecutive values regarded as spike"},
    'qcconf.spcr': {
        'type': 'float',
        'value': "0.01",
        'short': "Max Spike Frac",
        'comment': "Max. acceptable fraction of values removed as spikes"},
    # 2 amplitude resolution
    'qcconf.widampres': {
        'type': 'int',
        'value': "1000",
        'short': "Amp Res Width",
        'comment': "Averaging subrecord width in data points"},
    'qcconf.mxem': {
        'type': 'float',
        'value': "0.5",
        'short': "Max Empty Bins",
        'comment': "Max. acceptable fraction of empty cells in histogram"},
    # 3 dropouts
    'qcconf.widdropout': {
        'type': 'int',
        'value': "1000",
        'short': "Dropout Width",
        'comment': "Averaging subrecord width in data points"},
    'qcconf.maxcon1': {
        'type': 'float',
        'value': "0.10",
        'short': "Max Consec 10-90",
        'comment': "Max. acceptable fraction of consecutive values per subrecord within 10%-90% of value range"},
    'qcconf.maxcon2': {
        'type': 'float',
        'value': "0.06",
        'short': "Max Consec Outer",
        'comment': "Max. acceptable fraction of consecutive values per subrecord outside 10%-90% of value range"},
    # 4 absolute limits
    'qcconf.limu': {
        'type': 'float',
        'value': "50.",
        'short': "H Wind (m/s)",
        'comment': "Mean wind limit in m/s"},
    'qcconf.limw': {
        'type': 'float',
        'value': "5.",
        'short': "V Wind (m/s)",
        'comment': "Vertical wind limit in m/s"},
    'qcconf.limtl': {
        'type': 'float',
        'value': "-30.",
        'short': "Temp Min (°C)",
        'comment': "Lower temperature limit in °C"},
    'qcconf.limth': {
        'type': 'float',
        'value': "50.",
        'short': "Temp Max (°C)",
        'comment': "Upper temperature limit in °C"},
    'qcconf.limql': {
        'type': 'float',
        'value': "0.",
        'short': "Humid Min (g/kg)",
        'comment': "Lower specific humidity limit in g/kg"},
    'qcconf.limqh': {
        'type': 'float',
        'value': "30.",
        'short': "Humid Max (g/kg)",
        'comment': "Upper specific humidity limit in g/kg"},
    'qcconf.limcl': {
        'type': 'float',
        'value': "30.",
        'short': "CO₂ Min (ppm)",
        'comment': "Lower CO₂ concentration in ppm"},
    'qcconf.limch': {
        'type': 'float',
        'value': "1000.",
        'short': "CO₂ Max (ppm)",
        'comment': "Upper CO₂ concentration in ppm"},
    # 5 higher moments
    'qcconf.maxskew_1': {
        'type': 'float',
        'value': "1.",
        'short': "Skew Soft Limit",
        'comment': "Skewness threshold for soft flag"},
    'qcconf.maxskew_2': {
        'type': 'float',
        'value': "2.",
        'short': "Skew Hard Limit",
        'comment': "Skewness threshold for hard flag"},
    'qcconf.minkurt_1': {
        'type': 'float',
        'value': "2.",
        'short': "Kurt Min Soft",
        'comment': "Lower kurtosis threshold for soft flag"},
    'qcconf.maxkurt_1': {
        'type': 'float',
        'value': "5.",
        'short': "Kurt Max Soft",
        'comment': "Upper kurtosis threshold for soft flag"},
    'qcconf.minkurt_2': {
        'type': 'float',
        'value': "1.",
        'short': "Kurt Min Hard",
        'comment': "Lower kurtosis threshold for hard flag"},
    'qcconf.maxkurt_2': {
        'type': 'float',
        'value': "8.",
        'short': "Kurt Max Hard",
        'comment': "Upper kurtosis threshold for hard flag"},
    # 7 nonstationarity
    'qcconf.minred': {
        'type': 'float',
        'value': "0.9",
        'short': "Min Reduction",
        'comment': "Min. acceptable reduction of mean wind vector amount compared to mean wind speed"},
    'qcconf.maxrn': {
        'type': 'float',
        'value': "0.5",
        'short': "Max Nonstation",
        'comment': "Max. acceptable mean, cross, and vector wind relative nonstationarity"},
    # 8 lag correlation
    'qcconf.L2': {
        'type': 'float',
        'value': "2.",
        'short': "Lag Window (s)",
        'comment': "Lag search window in s"},
    # 9 change rate spikes
    'qcconf.chr_u': {
        'type': 'float',
        'value': "5.",
        'short': "H Wind (m/s)",
        'comment': "Max. horizontal wind change in m/s"},
    'qcconf.chr_w': {
        'type': 'float',
        'value': "5.",
        'short': "V Wind (m/s)",
        'comment': "Max. vertical wind change in m/s"},
    'qcconf.chr_t': {
        'type': 'float',
        'value': "5.",
        'short': "Temperature (K)",
        'comment': "Max. temperature change in K"},
    'qcconf.chrh2o': {
        'type': 'float',
        'value': "3.6",
        'short': "H₂O (g/m³)",
        'comment': "Max. specific humidity change in g/m³"},
    'qcconf.chrco2': {
        'type': 'float',
        'value': "20.",
        'short': "CO₂ (mg/m³)",
        'comment': "Max. CO₂ concentration change in mg/m³"},
    'qcconf.chrcr': {
        'type': 'float',
        'value': "0.01",
        'short': "Max Change Frac",
        'comment': "Max. acceptable fraction of values removed as spikes"},
    # 10 mad spikes
    'qcconf.mader': {
        'type': 'int',
        'value': "0",
        'short': "MAD Derivative",
        'comment': "0th derivative = use data values"},
    'qcconf.madth': {
        'type': 'float',
        'value': "6.5",
        'short': "MAD Threshold",
        'comment': "Threshold for spike detection in median absolute deviations"},
    'qcconf.madcr': {
        'type': 'float',
        'value': "0.01",
        'short': "Max Spike Frac",
        'comment': "Max. acceptable fraction of values removed as spikes"},
    # 11 stationariry after Foken & Wichura
    'qcconf.fwsub': {
        'type': 'int',
        'value': "6",
        'short': "F&W Subrecords",
        'comment': "Number of subrecords"},
    'qcconf.fwlim1': {
        'type': 'float',
        'value': "0.30",
        'short': "F&W Soft Limit",
        'comment': "Max. acceptable relative difference between subrecord and full record variances"},
    'qcconf.fwlim2': {
        'type': 'float',
        'value': "0.75",
        'short': "F&W Hard Limit",
        'comment': "Max. acceptable relative difference between subrecord and full record variances"},
    # 12 stationarity from flux by linear trend
    'qcconf.cotlimit': {
        'type': 'float',
        'value': "0.30",
        'short': "Covar Trend Lim",
        'comment': "Max. acceptable relative difference between covariances with and without detrending"},
    # 13 Higher moments compared to beta distribution
    'qcconf.bettol': {
        'type': 'float',
        'value': "1.",
        'short': "Beta Tolerance",
        'comment': "Max. tolerated deviation from borderline beta / gamma distribution"},
    'qcconf.betdet': {
        'type': 'float',
        'value': "1.",
        'short': "Beta Detrend",
        'comment': "Apply detrending, 0 = no, 1 = yes"},
    # 14 Stationarity of variance
    'qcconf.vstlim': {
        'type': 'float',
        'value': "3.",
        'short': "Var Change Lim",
        'comment': "Max. variance change between left and right side of a subrecord"},
    # 15 Turbulent fraction
    'qcconf.Lf': {
        'type': 'int',
        'value': "75",
        'short': "Subwindow Len (s)",
        'comment': "Subwindow length in seconds"},
    'qcconf.ftmin1': {
        'type': 'float',
        'value': "0.7",
        'short': "Soft Threshold",
        'comment': "Min. acceptable fraction before raising a soft flag"},
    'qcconf.ftmin2': {
        'type': 'float',
        'value': "0.5",
        'short': "Hard Threshold",
        'comment': "Min. acceptable fraction before raising a hard flag"},
    # 16 Surving values
    'qcconf.msurv1': {
        'type': 'float',
        'value': "0.99",
        'short': "Soft Survival",
        'comment': "Minimum acceptable fraction of surviving values before raising a soft flag"},
    'qcconf.msurv2': {
        'type': 'float',
        'value': "0.90",
        'short': "Hard Survival",
        'comment': "Minimum acceptable fraction of surviving values before raising a hard flag"},
    # value representing nans in despiked output
    'qcconf.spfill': {
        'type': 'int',
        'value': "1",
        'short': "Spike Fill",
        'comment': "1=interpolate spikes; 0=set spikes nan"},
    'qcconf.outnan': {
        'type': 'float',
        'value': "-9999.",
        'short': "Output NaN",
        'comment': "produces Nan in TOA5 and missing value in NetCDF"},
    #
    # ---------------------------------------
    # turbulence processor settings
    # ---------------------------------------
    #
    #
    'Par.DoIterate': {
        'type': 'bool',
        'value': 'T',
        'short': "Iterate Corr",
        'comment': "Iterate the Schotanus correction, the oxygen correction and the frequency correction"},
    'Par.MaxIter': {
        'type': 'int',
        'value': '10',
        'short': "Max Iterations",
        'comment': "The maximum number of iterations to be performed"},
    #
    'Par.FREQ': {
        'type': 'float',
        'value': "20.",
        'short': "Sample Freq (Hz)",
        'comment': "Sampling frequency of the fast data in Hz"},
    #
    'Par.PitchLim': {
        'type': 'float',
        'value': "30.",
        'short': "Pitch Limit (°)",
        'comment': "Limit when Mean(W) is turned to zero in degree"},
    'Par.RollLim': {
        'type': 'float',
        'value': "30.",
        'short': "Roll Limit (°)",
        'comment': "Limit when Cov(V,W) is turned to zero in degree"},
    #
    'Par.PreYaw': {
        'type': 'float',
        'value': "0.",
        'short': "Fixed Yaw",
        'comment': "Fixed yaw angle for known-tilt correction"},
    'Par.PrePitch': {
        'type': 'float',
        'value': "0.",
        'short': "Fixed Pitch",
        'comment': "Fixed pitch angle for known-tilt correction"},
    'Par.PreRoll': {
        'type': 'float',
        'value': "0.",
        'short': "Fixed Roll",
        'comment': "Fixed roll angle for known-tilt correction"},
    #
    'Par.LLimit': {
        'type': 'float',
        'value': "0.85",
        'short': "Freq Resp Low",
        'comment': "Smallest acceptable freq-response corr. factor"},
    'Par.ULimit': {
        'type': 'float',
        'value': "1.15",
        'short': "Freq Resp High",
        'comment': "Largest acceptable freq-response corr. factor"},
    #
    'Par.DoCrMean': {
        'type': 'bool',
        'value': 'T',
        'short': "Replace Means",
        'comment': "Replace mean quantities by better estimates"},
    'Par.DoDetrend': {
        'type': 'bool',
        'value': 'F',
        'short': "Detrend Data",
        'comment': "Correct data for linear trend"},
    'Par.DoSonic': {
        'type': 'bool',
        'value': 'T',
        'short': "Humidity Corr",
        'comment': "Correct sonic temperature for humidity"},
    'Par.DoTilt': {
        'type': 'bool',
        'value': 'F',
        'short': "Tilt Correction",
        'comment': "Perform true known-tilt correction with fixed angles"},
    'Par.DoYaw': {
        'type': 'bool',
        'value': 'T',
        'short': "Yaw Rotation",
        'comment': "Turn system such that Mean(V) is minimized"},
    'Par.DoPitch': {
        'type': 'bool',
        'value': 'F',
        'short': "Pitch Rotation",
        'comment': "Turn system such that Mean(W) is minimized"},
    'Par.DoRoll': {
        'type': 'bool',
        'value': 'F',
        'short': "Roll Rotation",
        'comment': "Turn System such that Cov(W,V) is minimized"},
    'Par.DoFreq': {
        'type': 'bool',
        'value': 'T',
        'short': "Freq Response",
        'comment': "Correct for limited frequency response of the instruments"},
    'Par.DoO2': {
        'type': 'bool',
        'value': 'T',
        'short': "O2 Sensitivity",
        'comment': "Correct hygrometer for oxygen-sensitivity"},
    'Par.DoWebb': {
        'type': 'bool',
        'value': 'T',
        'short': "Webb Correction",
        'comment': "Calculate mean velocity according to Webb"},
    'Par.DoStruct': {
        'type': 'bool',
        'value': 'T',
        'short': "Structure Coeff",
        'comment': "Calculate structure coefficients"},
    'Par.StructSep': {
        'type': 'float',
        'value': "0.15",
        'short': "Structure Sep",
        'comment': "separation used for calculation of structure parameters in m"},
    'Par.DoPF': {
        'type': 'bool',
        'value': 'T',
        'short': "Planar Fit",
        'comment': "Apply untilting by the planar-fit method"},
    'Par.PFValid': {
        'type': 'float',
        'value': "0.99",
        'short': "PF Validity",
        'comment': "Fraction of valid samples required to include interval in planar fit"},
    #
    'Par.DoErrFiSi': {
        'type': 'bool',
        'value': 'T',
        'short': "FiSi Error",
        'comment': "Calculate alternate random error of covariances after Finkelstein&Sims"},
    #
    'Par.DoPrint': {
        'type': 'bool',
        'value': 'F',
        'short': "Print Results",
        'comment': "Skip printing intermediate results or not?"},
    #
    # ---------------------------------------
    # postprocessor settings
    # ---------------------------------------
    #
    # i. mean vertical wind
    'qcconf.wlimit1': {
        'type': 'float',
        'value': '0.1',
        'short': "Soft Limit (m/s)",
        'comment': "Max. acceptable magnitude of mean vertical wind for soft flag"},
    'qcconf.wlimit2': {
        'type': 'float',
        'value': '0.15',
        'short': "Hard Limit (m/s)",
        'comment': "Max. acceptable magnitude of mean vertical wind for hard flag"},
    # ii. integr. turb. characteristics after Foken & Wichura
    'qcconf.itclim1': {
        'type': 'float',
        'value': '0.3',
        'short': "Soft Limit",
        'comment': "Max. acceptable relative difference between measured and modeled integr. turb. characteristics for soft flag"},
    'qcconf.itclim2': {
        'type': 'float',
        'value': '1.0',
        'short': "Hard Limit",
        'comment': "Max. acceptable relative difference between measured and modeled integr. turb. characteristics for hard flag"},
    'qcconf.itchmin': {
        'type': 'float',
        'value': '10.',
        'short': "Min Height (m)",
        'comment': "Minimum height for ITC calculation"},
    # iii. excluded sector wind direction
    #          set in main configuration if needed
    # iv. footprint model after Kormann & Meixner
    'qcconf.minfoot': {
        'type': 'float',
        'value': '0.70',
        'short': "Min Footprint",
        'comment': "Min. acceptable fraction of footprint in the area of interest"},
    # iv. exessive error
    'qcconf.Herrmin': {
        'type': 'float',
        'value': '15.',
        'short': "H Min (W/m²)",
        'comment': "Max. acceptable absolute error in sensible heat flux in W/m²"},
    'qcconf.Herrfac': {
        'type': 'float',
        'value': '0.3',
        'short': "H Factor",
        'comment': "Max. acceptable relative error in sensible heat flux"},
    'qcconf.Eerrmin': {
        'type': 'float',
        'value': '15.',
        'short': "LE Min (W/m²)",
        'comment': "Max. acceptable absolute error in latent heat flux in W/m²"},
    'qcconf.Eerrfac': {
        'type': 'float',
        'value': '0.3',
        'short': "LE Factor",
        'comment': "Max. acceptable relative error in latent heat flux"},
    'qcconf.Cerrmin': {
        'type': 'float',
        'value': '6.5E-8',
        'short': "CO₂ Min",
        'comment': "Max. acceptable absolute error in CO₂ flux in kg/m²/s"},
    'qcconf.Cerrfac': {
        'type': 'float',
        'value': '0.3',
        'short': "CO₂ Factor",
        'comment': "Max. acceptable relative error in CO₂ flux"},
    'qcconf.terrmin': {
        'type': 'float',
        'value': '0.05',
        'short': "τ Min (N/m²)",
        'comment': "Max. acceptable absolute error in momentum flux in N/m²"},
    'qcconf.terrfac': {
        'type': 'float',
        'value': '0.12',
        'short': "τ Factor",
        'comment': "Max. acceptable relative error in momentum flux"},
    #
    # flux-flag dependecies
    'qcconf.flag_tau': {
        'type': 'str',
        'value': "ux__lim uy__lim uz__lim ux__srvh2 uy__srvh2 uz__srvh2 ux__fws uy__fws uz__mnwi1 uz__mnwh2 ux__exs ux__itc uz__itc",
        'short': "τ Flag Rules",
        'comment': "Flag rules for momentum flux"},
    'qcconf.flag_h_0': {
        'type': 'str',
        'value': "ts__lim uz__lim ts__srvh2 uz__srvh2 ts__fws uz__mnwi1 uz__mnwh2 ux__exs uz__itc",
        'short': "H Flag Rules",
        'comment': "Flag rules for sensible heat flux"},
    'qcconf.flag_e_0': {
        'type': 'str',
        'value': "h2o_lim uz__lim h2o_srvh2 uz__srvh2 h2o_fws uz__mnwi1 uz__mnwh2 ux__exs uz__itc",
        'short': "LE Flag Rules",
        'comment': "Flag rules for latent heat flux"},
    'qcconf.flag_fc2': {
        'type': 'str',
        'value': "co2_lim uz__lim co2_srvh2 uz__srvh2 co2_fws uz__mnwi1 uz__mnwh2 ux__exs uz__itc",
        'short': "FC Flag Rules",
        'comment': "Flag rules for CO₂ flux"},
    #
    'qcconf.interrule': {
        'type': 'str',
        'value': "h_0ie_0 fc2ie_0",
        'short': "Inter Rules",
        'comment': "Inter-flag dependency rules"},
    #
    'qcconf.kill': {
        'type': 'int',
        'value': '2',
        'short': "Kill Level",
        'comment': "Flag level for killing data"},
    #
    # ---------------------------------------
    # Calibrations
    # ---------------------------------------
    #
    # external calibration files
    # SonName="calib-sonic.conf"
    # Coupname="calib-thermo.conf"
    # HygName="calib-hygro-h2o.conf"
    # CO2Name="calib-hygro-co2.conf"
    #
    #
    'SonCal.QQType': {
        'type': 'int',
        'value': "1",
        'short': "Device Type",
        'comment': "Device type code (see device types table)"},
    'SonCal.QQIdent': {
        'type': 'int',
        'value': "0",
        'short': "Serial Number",
        'comment': "True series-number of the apparatus"},
    'SonCal.QQGain': {
        'type': 'int',
        'value': "1",
        'short': "Gain",
        'comment': "Calibration gain factor"},
    'SonCal.QQOffset': {
        'type': 'int',
        'value': "0",
        'short': "Offset",
        'comment': "Calibration offset"},
    'SonCal.QQX': {
        'type': 'int',
        'value': "0",
        'short': "X Position",
        'comment': "Position coordinates (m) x-position of the focal point"},
    'SonCal.QQY': {
        'type': 'int',
        'value': "0",
        'short': "Y Position",
        'comment': "Position coordinates (m) y-position of the focal point"},
    'SonCal.QQZ': {
        'type': 'float',
        'value': "2.0",
        'short': "Z Position",
        'comment': "Position coordinates (m) and height above ground"},
    'SonCal.QQC0': {
        'type': 'int',
        'value': "0",
        'short': "Calib C0",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC1': {
        'type': 'int',
        'value': "0",
        'short': "Calib C1",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC2': {
        'type': 'int',
        'value': "0",
        'short': "Calib C2",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC3': {
        'type': 'int',
        'value': "0",
        'short': "Calib C3",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC4': {
        'type': 'int',
        'value': "0",
        'short': "Calib C4",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC5': {
        'type': 'int',
        'value': "0",
        'short': "Calib C5",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQC6': {
        'type': 'int',
        'value': "0",
        'short': "Calib C6",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQYaw': {
        'type': 'int',
        'value': "0",
        'short': "Yaw Angle",
        'comment': "[degree] Yaw angle of apparatus relative to north"},
    'SonCal.QQPitch': {
        'type': 'int',
        'value': "0",
        'short': "Pitch Angle",
        'comment': "Pitch angle"},
    'SonCal.QQRoll': {
        'type': 'int',
        'value': "0",
        'short': "Roll Angle",
        'comment': "Roll angle"},
    'SonCal.QQOrder': {
        'type': 'int',
        'value': "0",
        'short': "Order",
        'comment': "Calibration curve coefficients"},
    'SonCal.QQFunc': {
        'type': 'int',
        'value': "0",
        'short': "Function",
        'comment': "Calibration function type (1=polynomial, 2=logarithmic polynomial)"},
    'SonCal.QQPath': {
        'type': 'float',
        'value': "0.1",
        'short': "Path Length",
        'comment': "[m] Path length over which sensor integrates"},
    'SonCal.QQTime': {
        'type': 'int',
        'value': "0",
        'short': "Time Constant",
        'comment': "unused"},
    'SonCal.QQDelay': {
        'type': 'int',
        'value': "0",
        'short': "Delay",
        'comment': "[ms] Delay of this apparatus"},
    'SonCal.QQExt1': {
        'type': 'int',
        'value': "0",
        'short': "Ext1",
        'comment': "unused ? Factor for conversion of sonic temperature signal"},
    'SonCal.QQExt2': {
        'type': 'int',
        'value': "1",
        'short': "Ext2",
        'comment': "unused ? Multiplication factor for sonic temperature due to path length"},
    'SonCal.QQExt3': {
        'type': 'float',
        'value': "0.0",
        'short': "Ext3",
        'comment': "[m] distance w-u"},
    'SonCal.QQExt4': {
        'type': 'float',
        'value': "0.1",
        'short': "Ext4",
        'comment': "[m] path length sonic T"},
    'SonCal.QQExt5': {
        'type': 'int',
        'value': "0",
        'short': "Ext5",
        'comment': "Additional calibration coefficient"},
    'SonCal.QQExt6': {
        'type': 'int',
        'value': "0",
        'short': "Ext6",
        'comment': "Additional calibration coefficient"},
    'SonCal.QQExt7': {
        'type': 'int',
        'value': "0",
        'short': "Ext7",
        'comment': "Additional calibration coefficient"},
    'SonCal.QQExt8': {
        'type': 'int',
        'value': "0",
        'short': "Ext8",
        'comment': "Additional calibration coefficient"},
    'SonCal.QQExt9': {
        'type': 'int',
        'value': "0",
        'short': "Ext9",
        'comment': "Additional calibration coefficient"},
    'SonCal.QQExt10': {
        'type': 'int',
        'value': "0",
        'short': "Ext10",
        'comment': "Additional calibration coefficient (Only QQType=6)"},
    'SonCal.QQExt11': {
        'type': 'int',
        'value': "0",
        'short': "Ext11",
        'comment': "Additional calibration coefficient (Only QQType=6)"},
    #
    'CoupCal.QQType': {
        'type': 'int',
        'value': "2",
        'short': "Device Type",
        'comment': "Either of the ApXXXXXX numbers"},
    'CoupCal.QQIdent': {
        'type': 'int',
        'value': "0",
        'short': "Serial Number",
        'comment': "True series-number of the apparatus"},
    'CoupCal.QQGain': {
        'type': 'int',
        'value': "1",
        'short': "Gain",
        'comment': "Gain in this experiment"},
    'CoupCal.QQOffset': {
        'type': 'int',
        'value': "0",
        'short': "Offset",
        'comment': "Offset in this experiment"},
    'CoupCal.QQX': {
        'type': 'int',
        'value': "0",
        'short': "X Position",
        'comment': "Absolute x-position of the focal point"},
    'CoupCal.QQY': {
        'type': 'int',
        'value': "0",
        'short': "Y Position",
        'comment': "Absolute y-position of the focal point"},
    'CoupCal.QQZ': {
        'type': 'float',
        'value': "2.0",
        'short': "Z Position",
        'comment': "[m] Absolute z-position of the focal point"},
    'CoupCal.QQC0': {
        'type': 'int',
        'value': "0",
        'short': "Calib C0",
        'comment': "Zeroth order coefficient of calibration"},
    'CoupCal.QQC1': {
        'type': 'int',
        'value': "1",
        'short': "Calib C1",
        'comment': "First order coefficient of calibration"},
    'CoupCal.QQC2': {
        'type': 'int',
        'value': "0",
        'short': "Calib C2",
        'comment': "Second order coefficient of calibration"},
    'CoupCal.QQC3': {
        'type': 'int',
        'value': "0",
        'short': "Calib C3",
        'comment': "Third order coefficient of calibration"},
    'CoupCal.QQC4': {
        'type': 'int',
        'value': "0",
        'short': "Calib C4",
        'comment': "Fourth order coefficient of calibration"},
    'CoupCal.QQC5': {
        'type': 'int',
        'value': "0",
        'short': "Calib C5",
        'comment': "Fifth order coefficient of calibration"},
    'CoupCal.QQC6': {
        'type': 'int',
        'value': "0",
        'short': "Calib C6",
        'comment': "Sixth order coefficient of calibration"},
    'CoupCal.QQYaw': {
        'type': 'int',
        'value': "0",
        'short': "Yaw Angle",
        'comment': "unused"},
    'CoupCal.QQPitch': {
        'type': 'int',
        'value': "0",
        'short': "Pitch Angle",
        'comment': "unused"},
    'CoupCal.QQRoll': {
        'type': 'int',
        'value': "0",
        'short': "Roll Angle",
        'comment': "unused"},
    'CoupCal.QQOrder': {
        'type': 'int',
        'value': "1",
        'short': "Order",
        'comment': "Order of the calibration model"},
    'CoupCal.QQFunc': {
        'type': 'int',
        'value': "1",
        'short': "Function",
        'comment': "Type of fitfunction"},
    'CoupCal.QQPath': {
        'type': 'int',
        'value': "0",
        'short': "Path Length",
        'comment': "unused"},
    'CoupCal.QQTime': {
        'type': 'int',
        'value': "0",
        'short': "Time Constant",
        'comment': "Time constant"},
    'CoupCal.QQDelay': {
        'type': 'int',
        'value': "0",
        'short': "Delay",
        'comment': "[ms] Delay of this apparatus"},
    'CoupCal.QQExt1': {
        'type': 'int',
        'value': "0",
        'short': "Ext1",
        'comment': "unused"},
    'CoupCal.QQExt2': {
        'type': 'int',
        'value': "0",
        'short': "Ext2",
        'comment': "unused"},
    'CoupCal.QQExt3': {
        'type': 'int',
        'value': "0",
        'short': "Ext3",
        'comment': "unused"},
    'CoupCal.QQExt4': {
        'type': 'int',
        'value': "0",
        'short': "Ext4",
        'comment': "unused"},
    'CoupCal.QQExt5': {
        'type': 'int',
        'value': "0",
        'short': "Ext5",
        'comment': "unused"},
    #
    'HygCal.QQType': {
        'type': 'int',
        'value': "8",
        'short': "Device Type",
        'comment': "Either of the ApXXXXXX numbers"},
    'HygCal.QQIdent': {
        'type': 'int',
        'value': "0",
        'short': "Serial Number",
        'comment': "True series-number of the apparatus"},
    'HygCal.QQGain': {
        'type': 'int',
        'value': "1000",
        'short': "Gain",
        'comment': "Gain in this experiment"},
    'HygCal.QQOffset': {
        'type': 'int',
        'value': "0",
        'short': "Offset",
        'comment': "Offset in this experiment"},
    'HygCal.QQX': {
        'type': 'int',
        'value': "0",
        'short': "X Position",
        'comment': "Absolute x-position of the focal point"},
    'HygCal.QQY': {
        'type': 'int',
        'value': "0",
        'short': "Y Position",
        'comment': "Absolute y-position of the focal point"},
    'HygCal.QQZ': {
        'type': 'float',
        'value': "2.0",
        'short': "Z Position",
        'comment': "[m] Absolute z-position of the focal point"},
    'HygCal.QQC0': {
        'type': 'int',
        'value': "0",
        'short': "Calib C0",
        'comment': "Zeroth order coefficient of calibration"},
    'HygCal.QQC1': {
        'type': 'int',
        'value': "1",
        'short': "Calib C1",
        'comment': "First order coefficient of calibration"},
    'HygCal.QQC2': {
        'type': 'int',
        'value': "0",
        'short': "Calib C2",
        'comment': "Second order coefficient of calibration"},
    'HygCal.QQC3': {
        'type': 'int',
        'value': "0",
        'short': "Calib C3",
        'comment': "Third order coefficient of calibration"},
    'HygCal.QQC4': {
        'type': 'int',
        'value': "0",
        'short': "Calib C4",
        'comment': "Fourth order coefficient of calibration"},
    'HygCal.QQC5': {
        'type': 'int',
        'value': "0",
        'short': "Calib C5",
        'comment': "Fifth order coefficient of calibration"},
    'HygCal.QQC6': {
        'type': 'int',
        'value': "0",
        'short': "Calib C6",
        'comment': "Sixth order coefficient of calibration"},
    'HygCal.QQYaw': {
        'type': 'int',
        'value': "0",
        'short': "Yaw Angle",
        'comment': "unused"},
    'HygCal.QQPitch': {
        'type': 'int',
        'value': "0",
        'short': "Pitch Angle",
        'comment': "unused"},
    'HygCal.QQRoll': {
        'type': 'int',
        'value': "0",
        'short': "Roll Angle",
        'comment': "unused"},
    'HygCal.QQOrder': {
        'type': 'int',
        'value': "1",
        'short': "Order",
        'comment': "Order of the calibration model"},
    'HygCal.QQFunc': {
        'type': 'int',
        'value': "1",
        'short': "Function",
        'comment': "Type of fitfunction"},
    'HygCal.QQPath': {
        'type': 'float',
        'value': "0.1",
        'short': "Path Length",
        'comment': "[m] Path length over which sensor integrates"},
    'HygCal.QQTime': {
        'type': 'int',
        'value': "0",
        'short': "Time Constant",
        'comment': "unused"},
    'HygCal.QQDelay': {
        'type': 'int',
        'value': "0",
        'short': "Delay",
        'comment': "[ms] Delay of this apparatus"},
    'HygCal.QQExt1': {
        'type': 'int',
        'value': "0",
        'short': "Ext1",
        'comment': "unused"},
    'HygCal.QQExt2': {
        'type': 'int',
        'value': "0",
        'short': "Ext2",
        'comment': "unused"},
    'HygCal.QQExt3': {
        'type': 'int',
        'value': "0",
        'short': "Ext3",
        'comment': "unused"},
    'HygCal.QQExt4': {
        'type': 'int',
        'value': "0",
        'short': "Ext4",
        'comment': "unused"},
    'HygCal.QQExt5': {
        'type': 'int',
        'value': "0",
        'short': "Ext5",
        'comment': "unused"},
    #
    'Co2Cal.QQType': {
        'type': 'int',
        'value': "8",
        'short': "Device Type",
        'comment': "Either of the ApXXXXXX numbers"},
    'Co2Cal.QQIdent': {
        'type': 'int',
        'value': "0",
        'short': "Serial Number",
        'comment': "True series-number of the apparatus"},
    'Co2Cal.QQGain': {
        'type': 'int',
        'value': "1000000",
        'short': "Gain",
        'comment': "Gain in this experiment"},
    'Co2Cal.QQOffset': {
        'type': 'int',
        'value': "0",
        'short': "Offset",
        'comment': "Offset in this experiment"},
    'Co2Cal.QQX': {
        'type': 'int',
        'value': "0",
        'short': "X Position",
        'comment': "Absolute x-position of the focal point"},
    'Co2Cal.QQY': {
        'type': 'int',
        'value': "0",
        'short': "Y Position",
        'comment': "Absolute y-position of the focal point"},
    'Co2Cal.QQZ': {
        'type': 'float',
        'value': "2.0",
        'short': "Z Position",
        'comment': "[m] Absolute z-position of the focal point"},
    'Co2Cal.QQC0': {
        'type': 'int',
        'value': "0",
        'short': "Calib C0",
        'comment': "Zeroth order coefficient of calibration"},
    'Co2Cal.QQC1': {
        'type': 'int',
        'value': "1",
        'short': "Calib C1",
        'comment': "First order coefficient of calibration"},
    'Co2Cal.QQC2': {
        'type': 'int',
        'value': "0",
        'short': "Calib C2",
        'comment': "Second order coefficient of calibration"},
    'Co2Cal.QQC3': {
        'type': 'int',
        'value': "0",
        'short': "Calib C3",
        'comment': "Third order coefficient of calibration"},
    'Co2Cal.QQC4': {
        'type': 'int',
        'value': "0",
        'short': "Calib C4",
        'comment': "Fourth order coefficient of calibration"},
    'Co2Cal.QQC5': {
        'type': 'int',
        'value': "0",
        'short': "Calib C5",
        'comment': "Fifth order coefficient of calibration"},
    'Co2Cal.QQC6': {
        'type': 'int',
        'value': "0",
        'short': "Calib C6",
        'comment': "Sixth order coefficient of calibration"},
    'Co2Cal.QQYaw': {
        'type': 'int',
        'value': "0",
        'short': "Yaw Angle",
        'comment': "unused"},
    'Co2Cal.QQPitch': {
        'type': 'int',
        'value': "0",
        'short': "Pitch Angle",
        'comment': "unused"},
    'Co2Cal.QQRoll': {
        'type': 'int',
        'value': "0",
        'short': "Roll Angle",
        'comment': "unused"},
    'Co2Cal.QQOrder': {
        'type': 'int',
        'value': "1",
        'short': "Order",
        'comment': "Order of the calibration model"},
    'Co2Cal.QQFunc': {
        'type': 'int',
        'value': "1",
        'short': "Function",
        'comment': "Type of fitfunction"},
    'Co2Cal.QQPath': {
        'type': 'float',
        'value': "0.1",
        'short': "Path Length",
        'comment': "[m] Path length over which sensor integrates"},
    'Co2Cal.QQTime': {
        'type': 'int',
        'value': "0",
        'short': "Time Constant",
        'comment': "unused"},
    'Co2Cal.QQDelay': {
        'type': 'int',
        'value': "0",
        'short': "Delay",
        'comment': "[ms] Delay of this apparatus"},
    'Co2Cal.QQExt1': {
        'type': 'int',
        'value': "0",
        'short': "Ext1",
        'comment': "unused"},
    'Co2Cal.QQExt2': {
        'type': 'int',
        'value': "0",
        'short': "Ext2",
        'comment': "unused"},
    'Co2Cal.QQExt3': {
        'type': 'int',
        'value': "0",
        'short': "Ext3",
        'comment': "unused"},
    'Co2Cal.QQExt4': {
        'type': 'int',
        'value': "0",
        'short': "Ext4",
        'comment': "unused"},
    'Co2Cal.QQExt5': {
        'type': 'int',
        'value': "0",
        'short': "Ext5",
        'comment': "unused"},
    #
}