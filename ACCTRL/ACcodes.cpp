#include "main.h"

const uint16_t code_ACTimes[] PROGMEM = {
  895, 446,
  61,  52,
  61,  163,
  61,  4079,
  895,  224,
  61,  52
};

/* original
origcodes =  [0, 1, 1,1,2,1,1,1,1,2,1,2,1,2,2,2,2,2,1,1,1,2,1,1,1,1,2,2,2,1,2,2,2,3,4, 3]
print "numCodes", len(origcodes)
def samplesTo10USec(x):
   return (x*1000*100/44100)

def toCodes(l,compression):
    s = ""
    for x in l:
        s += ("{0:0" + str(compression)+ "b}").format(x)
    if len(s)%8 != 0:
        s += "0"*(8 - (len(s)%8))
    numBytes = len(s)/8
    res = []
    for i in range(numBytes):
        num = s[i*8:(i+1)*8]
        num = int(num,2)
        res += [num]
    return res


codes = toCodes(origcodes,3)
print ",\n".join(["0x%02X"%x for x in codes])

*/
const uint8_t code_ACCodes[] PROGMEM = {
0x04,
0x94,
0x49,
0x28,
0xA2,
0x92,
0x48,
0x92,
0x89,
0x25,
0x24,
0x52,
0x4E,
0x30
};
const struct IrCode code_ACCode PROGMEM = {
  freq_to_timerval(38462),
  36,		// # of pairs
  3,		// # of bits per index
  code_ACTimes,
  code_ACCodes
};


const struct IrCode *ACpowerCodes[] PROGMEM = {
&code_ACCode };

uint8_t num_ACcodes = NUM_ELEM(ACpowerCodes);
