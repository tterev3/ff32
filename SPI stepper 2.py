import pyff32eb as ff32
from tkinter import *
from tkinter import ttk

def update(*args):
    val = position.get()
    position.set(round(val,0))
    val = speed.get()
    speed.set(round(val,0))
def force_current(*args):
    global real_current
    current.set(real_current)
def update_2(*args):
    global pos_last
    global sp_last
    global run_last
    global dat
    r=run.get()
    sp=speed.get()
    pos=position.get()
    if sp!=sp_last or pos!=pos_last or r!=run_last:
        sp_last=sp
        pos_last=pos
        run_last=r
        if r==True:
            dat=[3, (pos>>8)&0xff, (pos&0xff), (sp&0xff)]
            reply=ff32.readSPI(4, dat)
            current.set(int(reply[0]<<8|reply[1]))
    elif real_current != pos and r==True:
        query()
    window.after(150, update_2)
def query(*args):
    global real_current
    reply=ff32.readSPI(4, dat)
    real_current=int(reply[0]<<8|reply[1])
    current.set(real_current)

pos_last=4096
sp_last=5
run_last=0
real_current=4096
dat=[3, 0, 0, 5]
window=Tk()
window.title("stepper motor control")
window_frame = ttk.Frame(window,padding="3 3 12 12")
window_frame.grid(column=0, row=0, sticky=(N, W, E, S))
window_frame.columnconfigure(0, weight=1)
window_frame.rowconfigure(0, weight=1)
position=IntVar()
position.set(4096)
ttk.Label(window, text="Target:").grid(column=1, row=1, sticky=W)
ttk.Label(window, textvariable=position).grid(column=2, row=1, sticky=W)
slider = ttk.Scale(window, from_=0, to=8192, orient=HORIZONTAL, variable=position, length=400, command=update)
slider.grid(column=1, row=2, columnspan=6)
ttk.Label(window, text="Current:").grid(column=1, row=3, sticky=W)
current=IntVar()
current.set(4096)
ttk.Label(window, textvariable=current).grid(column=2, row=3, sticky=W)
#ttk.Label(window, textvariable=current).grid(column=2, row=3, sticky=W)
current_scale=ttk.Scale(window, from_=0, to=8192, orient=HORIZONTAL, variable=current, length=400, command=force_current)
current_scale.grid(column=1, row=4, columnspan=6)
current.set('disabled')
#current_scale.configure(state='disabled')
ttk.Button(window, text="query", command=query).grid(column=3, row=3, sticky=W)
ttk.Label(window, text="Speed:").grid(column=1, row=5, sticky=W)
speed=IntVar()
ttk.Label(window, textvariable=speed).grid(column=2, row=5, sticky=W)
speed.set(5)
speed_slider = ttk.Scale(window, from_=3, to=250, orient=HORIZONTAL, variable=speed, length=400, command=update)
speed_slider.grid(column=1, row=6, columnspan=6)
run=BooleanVar()
run_check=ttk.Checkbutton(window, text="Run", variable=run, onvalue=True, command=update)
run_check.grid(column=1, row=7, sticky=W)

ff32.initialize()
ff32.setSPIPins(['A',6],['A',5],['B',12],['B',11])


window.after(200, update_2)
window.mainloop()

##ff32.initialize()
##if ff32.acknowledge():
##    print("communication with FF32 established")
##    #cs, clock, mosi, miso
##    ff32.setSPIPins(['A',6],['A',5],['B',12],['B',11])
##    speed=8
##    position=0
##    while True:
##        try:
##            speed = int(input("speed?"))
##        except ValueError:
##            pass #speed=8
##        try:
##            position = int(input("position?"))
##        except ValueError:
##            pass
##        dat=[5, (position>>8)&0xff, (position&0xff), (speed&0xff)]
##        reply=ff32.readSPI(4, dat)
##        print("current position = %g" %int(reply[0]<<8|reply[1]))
##
##else: print("error communicating with FF32")
