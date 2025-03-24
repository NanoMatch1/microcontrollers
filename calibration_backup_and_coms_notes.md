
    # calibration_backup = {"wl_to_triax_steps": [0.10804683994803718, 331.8588098129754, 43950.89354704326], "triax_steps_to_wl": [-5.094413299766325e-08, -0.01590813394008432, 802.7653861488677], "wl_to_l1": [-0.01252753345943214, -42.75470684410267, 42395.08424620002], "l1_to_wl": [-5.094413299758575e-08, -0.015908133940084567, 802.765386148867], "wl_to_l2": [0.004068479941637935, 20.30418040830074, -18891.41344719332], "l2_to_wl": [-2.1134374286916415e-07, 0.03727793396921931, 801.6492620060089], "wl_to_g1_subtractive": [-0.0009343860392719734, 10.7261833692083, 650945.1172672338, 4.655494031296545, 0.08293861801416774, -28.836971874316305, -658973.3758272409], "g1_to_wl_subtractive": [-3.997416525894944e-06, 0.11504349729740472, 40924.95099077628, -3.7657797835191977, 0.0029830668481275646, 6.0959394773331725, -40119.77931396578], "wl_to_g2": [0.023079240005018726, -45.473382574917395, 8566.991143604224], "g2_to_wl": [4.023690443149823e-05, 0.9297669680984147, 6082.062394487625], "wl_to_g1_additive": [0.005183899414806875, 1.448578450504759, 624081.2598467232, 18.066764876201965, 0.08365631420139119, -29.51008752837752, -628605.1425510542], "g1_to_wl_additive": [-9.626148251565028e-06, 0.10420683828922353, -4848.442236579409, -2.272040105929268, 0.0074373346698996335, 6.471415416643864, 5653.535879138745]}

    # standard positions:
    # Current laser wavelength: 802.7494779639835
    # Current grating wavelength: 802.7823897229985


    '''# looking for some kind of response like "b" or "o". Use command "O2000" to enter into command mode.
# Polyfit calibration 24/08/27: [-1.28255101e-02 -4.23233709e+01  4.22414334e+04]
Initial grating is Blaze 500, 1200 g/mm
centre for 532 nm is roughly 241543
centre for sulfur at ~800 nm is 376886 (apd laser at "370686"/371736) (NEW 23/05 375131) (ccd+= 6000) 374414
List of useful commands = {
"Initiate command mode": "02000",
# "Initialise Spectrometer: "A",
"read motor position": "H0",
"read slit position: "j0,0",
"move slit relative: "k0,0,100"
"poll motors after move command sent - necessary because control is given to PC immediately after command is given, but new motor command cannot be issued until motor motion is stopped. Implement a check for this here. Note if the motors are not busy, a timeout is received... could be a delay/timing issue: "E",
"move exit mirror to front exit (out of path): "f0".
"move exit mirror to side exit (in path): "e0",
"entrance mirror to front enterance: "c0",
"entrance mirror to side enterance: "d0"


'''