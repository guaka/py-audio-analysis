from __future__ import division
from scipy import signal, arange, sin, pi
from RandomArray import normal
from scipy.signal import buttord, butter, lfilter
import Interactive


dt = 0.001
t = arange(0.0, 10.0, dt)
nse = normal(0, 1.4, t.shape)
#s = sin(2*pi*t) + nse
s = nse

lpcf = 3
lpsf = 5
Nyq = 1/(2*dt)
Rp = 1
Rs = 500
Wp = lpcf/Nyq
Ws = lpsf/Nyq
d = 0.5
e = 0.0000000001
[n,Wn] = buttord([d - e, d], [d - e - e, d + e], Rp, Rs)
[b,a] = butter(n,Wn)
xlp = lfilter(b,a,s)

Interactive.show(xlp)
