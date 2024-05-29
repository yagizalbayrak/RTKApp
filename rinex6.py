import numpy as np
from datetime import datetime, timedelta

# Constants/Macros
NUMSYS = 6  # Number of systems
MAXOBSTYPE = 64  # Maximum number of observation types
MAXRNXLEN = (16 * MAXOBSTYPE + 4)  # Max RINEX record length
MAXPOSHEAD = 1024  # Max head line position
MINFREQ_GLO = -7  # Min frequency number for GLONASS
MAXFREQ_GLO = 13  # Max frequency number for GLONASS
NINCOBS = 262144  # Incremental number of observation data

# Satellite systems
navsys = ['GPS', 'GLO', 'GAL', 'QZS', 'SBS', 'CMP']
syscodes = 'GREJSC'  # Satellite system codes
obscodes = 'CLDS'  # Observation type codes
frqcodes = '125678'  # Frequency codes

# URA values (reference from IS-GPS-200D)
ura_eph = [
    2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24.0, 48.0, 96.0, 192.0, 384.0, 768.0, 1536.0,
    3072.0, 6144.0, 0.0
]

# Signal Index Type
class SigInd:
    def __init__(self):
        self.n = 0
        self.frq = [0] * MAXOBSTYPE
        self.pos = [-1] * MAXOBSTYPE
        self.pri = [0] * MAXOBSTYPE
        self.type = [0] * MAXOBSTYPE
        self.code = [0] * MAXOBSTYPE
        self.shift = [0.0] * MAXOBSTYPE

# Set string without tail space
def setstr(dst, src, n):
    dst[:n] = src[:n].rstrip()

# Adjust time considering week handover
def adjweek(t, t0):
    tt = (t - t0).total_seconds()
    if tt < -302400.0:
        return t + timedelta(weeks=1)
    if tt > 302400.0:
        return t - timedelta(weeks=1)
    return t

# Adjust time considering day handover
def adjday(t, t0):
    tt = (t - t0).total_seconds()
    if tt < -43200.0:
        return t + timedelta(days=1)
    if tt > 43200.0:
        return t - timedelta(days=1)
    return t

# Time string for ver.3 (yyyymmdd hhmmss UTC)
def timestr_rnx():
    now = datetime.utcnow().replace(microsecond=0)
    return now.strftime("%Y%m%d %H%M%S UTC")

# Satellite to satellite code
def sat2code(sat, prn):
    if sat == 'GPS':
        return f"G{prn:02d}"
    elif sat == 'GLO':
        return f"R{prn:02d}"
    elif sat == 'GAL':
        return f"E{prn:02d}"
    elif sat == 'SBS':
        return f"S{prn:02d}"
    elif sat == 'QZS':
        return f"J{prn:02d}"
    elif sat == 'CMP':
        return f"C{prn:02d}"
    else:
        return None

# Function to convert URA index to URA value (m)
def uravalue(sva):
    return ura_eph[sva] if 0 <= sva < 15 else 32767.0

# Function to convert URA value (m) to URA index
def uraindex(value):
    for i, ura in enumerate(ura_eph):
        if ura >= value:
            return i
    return 15

# Station parameter class
class Sta:
    def __init__(self):
        self.name = ''
        self.marker = ''
        self.antdes = ''
        self.antsno = ''
        self.rectype = ''
        self.recver = ''
        self.recsno = ''
        self.antsetup = 0
        self.itrf = 0
        self.deltype = 0
        self.pos = [0.0, 0.0, 0.0]
        self.del_ = [0.0, 0.0, 0.0]  # 'del' is a reserved keyword in Python
        self.hgt = 0.0

# Initialize station parameter
def init_sta(sta):
    sta.name = ''
    sta.marker = ''
    sta.antdes = ''
    sta.antsno = ''
    sta.rectype = ''
    sta.recver = ''
    sta.recsno = ''
    sta.antsetup = 0
    sta.itrf = 0
    sta.deltype = 0
    sta.pos = [0.0, 0.0, 0.0]
    sta.del_ = [0.0, 0.0, 0.0]  # 'del' is a reserved keyword in Python
    sta.hgt = 0.0

def convcode(ver, sys, str):
    type = "   "
    
    if str == "P1":  # ver.2.11 GPS L1PY,GLO L2P
        if sys == SYS_GPS:
            type = "{}1W".format('C')
        elif sys == SYS_GLO:
            type = "{}1P".format('C')
    elif str == "P2":  # ver.2.11 GPS L2PY,GLO L2P
        if sys == SYS_GPS:
            type = "{}2W".format('C')
        elif sys == SYS_GLO:
            type = "{}2P".format('C')
    elif str == "C1":  # ver.2.11 GPS L1C,GLO L1C/A
        if ver >= 2.12:
            pass  # reject C1 for 2.12
        else:
            if sys == SYS_GPS:
                type = "{}1C".format('C')
            elif sys == SYS_GLO:
                type = "{}1C".format('C')
            elif sys == SYS_GAL:
                type = "{}1X".format('C')  # ver.2.12
            elif sys == SYS_QZS:
                type = "{}1C".format('C')
            elif sys == SYS_SBS:
                type = "{}1C".format('C')
    elif str == "C2":
        if sys == SYS_GPS:
            if ver >= 2.12:
                type = "{}2W".format('C')  # L2P(Y)
            else:
                type = "{}2X".format('C')  # L2C
        elif sys == SYS_GLO:
            type = "{}2C".format('C')
        elif sys == SYS_QZS:
            type = "{}2X".format('C')
        elif sys == SYS_CMP:
            type = "{}1X".format('C')  # ver.2.12 B1
    elif ver >= 2.12 and str[1] == 'A':  # ver.2.12 L1C/A
        if sys == SYS_GPS:
            type = "{}1C".format(str[0])
        elif sys == SYS_GLO:
            type = "{}1C".format(str[0])
        elif sys == SYS_QZS:
            type = "{}1C".format(str[0])
        elif sys == SYS_SBS:
            type = "{}1C".format(str[0])
    elif ver >= 2.12 and str[1] == 'B':  # ver.2.12 GPS L1C
        if sys == SYS_GPS:
            type = "{}1X".format(str[0])
        elif sys == SYS_QZS:
            type = "{}1X".format(str[0])
    elif ver >= 2.12 and str[1] == 'C':  # ver.2.12 GPS L2C
        if sys == SYS_GPS:
            type = "{}2X".format(str[0])
        elif sys == SYS_QZS:
            type = "{}2X".format(str[0])
    elif ver >= 2.12 and str[1] == 'D':  # ver.2.12 GLO L2C/A
        if sys == SYS_GLO:
            type = "{}2C".format(str[0])
    elif ver >= 2.12 and str[1] == '1':  # ver.2.12 GPS L1PY,GLO L1P
        if sys == SYS_GPS:
            type = "{}1W".format(str[0])
        elif sys == SYS_GLO:
            type = "{}1P".format(str[0])
        elif sys == SYS_GAL:
            type = "{}1X".format(str[0])  # tentative
        elif sys == SYS_CMP:
            type = "{}1X".format(str[0])  # extension
    elif ver < 2.12 and str[1] == '1':
        if sys == SYS_GPS:
            type = "{}1C".format(str[0])
        elif sys == SYS_GLO:
            type = "{}1C".format(str[0])
        elif sys == SYS_GAL:
            type = "{}1X".format(str[0])  # tentative
        elif sys == SYS_QZS:
            type = "{}1C".format(str[0])
        elif sys == SYS_SBS:
            type = "{}1C".format(str[0])
    elif str[1] == '2':
        if sys == SYS_GPS:
            type = "{}2W".format(str[0])
        elif sys == SYS_GLO:
            type = "{}2P".format(str[0])
        elif sys == SYS_QZS:
            type = "{}2X".format(str[0])
        elif sys == SYS_CMP:
            type = "{}1X".format(str[0])  # ver.2.12 B1
    elif str[1] == '5':
        if sys == SYS_GPS:
            type = "{}5X".format(str[0])
        elif sys == SYS_GAL:
            type = "{}5X".format(str[0])
        elif sys == SYS_QZS:
            type = "{}5X".format(str[0])
        elif sys == SYS_SBS:
            type = "{}5X".format(str[0])
    elif str[1] == '6':
        if sys == SYS_GAL:
            type = "{}6X".format(str[0])
        elif sys == SYS_QZS:
            type = "{}6X".format(str[0])
        elif sys == SYS_CMP:
            type = "{}6X".format(str[0])  # ver.2.12 B3
    elif str[1] == '7':
        if sys == SYS_GAL:
            type = "{}7X".format(str[0])
        elif sys == SYS_CMP:
            type = "{}7X".format(str[0])  # ver.2.12 B2
    elif str[1] == '8':
        if sys == SYS_GAL:
            type = "{}8X".format(str[0])
    
    print("convcode: ver={:.2f} sys={} type= {} -> {}".format(ver, sys, str, type))
    return type
  
  def decode_obsh(fp, buff, ver, tsys, tobs, nav, sta):
    # default codes for unknown code
    defcodes = [
        "CWX   ",  # GPS: L125___
        "CC    ",  # GLO: L12____
        "X XXXX",  # GAL: L1_5678
        "CXXX  ",  # QZS: L1256__
        "C X   ",  # SBS: L1_5___
        "X  XX "   # BDS: L1__67_
    ]
    deltas = [0.0, 0.0, 0.0]
    label = buff[60:]
    str4 = [""] * 4

    print(f"decode_obsh: ver={ver:.2f}")
    
    if "MARKER NAME" in label:
        if sta:
            sta.name = buff[:60].strip()
    elif "MARKER NUMBER" in label:  # opt
        if sta:
            sta.marker = buff[:20].strip()
    elif "MARKER TYPE" in label:  # ver.3
        pass
    elif "OBSERVER / AGENCY" in label:
        pass
    elif "REC # / TYPE / VERS" in label:
        if sta:
            sta.recsno = buff[:20].strip()
            sta.rectype = buff[20:40].strip()
            sta.recver = buff[40:60].strip()
    elif "ANT # / TYPE" in label:
        if sta:
            sta.antsno = buff[:20].strip()
            sta.antdes = buff[20:40].strip()
    elif "APPROX POSITION XYZ" in label:
        if sta:
            for i in range(3):
                sta.pos[i] = float(buff[i * 14:(i + 1) * 14].strip())
    elif "ANTENNA: DELTA H/E/N" in label:
        if sta:
            for i in range(3):
                deltas[i] = float(buff[i * 14:(i + 1) * 14].strip())
            sta.del[2] = deltas[0]  # h
            sta.del[0] = deltas[1]  # e
            sta.del[1] = deltas[2]  # n
    elif "ANTENNA: DELTA X/Y/Z" in label:  # opt ver.3
        pass
    elif "ANTENNA: PHASECENTER" in label:  # opt ver.3
        pass
    elif "ANTENNA: B.SIGHT XYZ" in label:  # opt ver.3
        pass
    elif "ANTENNA: ZERODIR AZI" in label:  # opt ver.3
        pass
    elif "ANTENNA: ZERODIR XYZ" in label:  # opt ver.3
        pass
    elif "CENTER OF MASS: XYZ" in label:  # opt ver.3
        pass
    elif "SYS / # / OBS TYPES" in label:  # ver.3
        p = syscodes.find(buff[0])
        if p == -1:
            print(f"invalid system code: sys={buff[0]}")
            return
        
        i = p
        n = int(buff[3:6].strip())
        j = nt = 0
        k = 7
        while j < n:
            if k > 58:
                buff = fp.readline()
                k = 7
            if nt < MAXOBSTYPE - 1:
                tobs[i][nt] = buff[k:k + 3]
                nt += 1
            j += 1
            k += 4
        tobs[i][nt] = ''
        
        # change beidou B1 code: 3.02 draft -> 3.02
        if i == 5:
            for j in range(nt):
                if tobs[i][j][1] == '2':
                    tobs[i][j] = tobs[i][j][:1] + '1' + tobs[i][j][2:]
        
        # if unknown code in ver.3, set default code
        for j in range(nt):
            if len(tobs[i][j]) > 2:
                continue
            p = frqcodes.find(tobs[i][j][1])
            if p == -1:
                continue
            tobs[i][j] = tobs[i][j] + defcodes[i][p]
            print(f"set default for unknown code: sys={buff[0]} code={tobs[i][j]}")
    elif "WAVELENGTH FACT L1/2" in label:  # opt ver.2
        pass
    elif "# / TYPES OF OBSERV" in label:  # ver.2
        n = int(buff[:6].strip())
        j = nt = 0
        while j < n:
            if j > 58:
                buff = fp.readline()
                j = 10
            if nt >= MAXOBSTYPE - 1:
                continue
            if ver <= 2.99:
                str_ = buff[j:j + 2]
                tobs[0][nt] = convcode(ver, SYS_GPS, str_)
                tobs[1][nt] = convcode(ver, SYS_GLO, str_)
                tobs[2][nt] = convcode(ver, SYS_GAL, str_)
                tobs[3][nt] = convcode(ver, SYS_QZS, str_)
                tobs[4][nt] = convcode(ver, SYS_SBS, str_)
                tobs[5][nt] = convcode(ver, SYS_CMP, str_)
            nt += 1
            j += 6
        tobs[0][nt] = ''
    elif "SIGNAL STRENGTH UNIT" in label:  # opt ver.3
        pass
    elif "INTERVAL" in label:  # opt
        pass
    elif "TIME OF FIRST OBS" in label:
        if buff[48:51] == "GPS":
            tsys = TSYS_GPS
        elif buff[48:51] == "GLO":
            tsys = TSYS_UTC
        elif buff[48:51] == "GAL":
            tsys = TSYS_GAL
        elif buff[48:51] == "QZS":  # ver.3.02
            tsys = TSYS_QZS
        elif buff[48:51] == "BDT":  # ver.3.02
            tsys = TSYS_CMP
    elif "TIME OF LAST OBS" in label:  # opt
        pass
    elif "RCV CLOCK OFFS APPL" in label:  # opt
        pass
    elif "SYS / DCBS APPLIED" in label:  # opt ver.3
        pass
    elif "SYS / PCVS APPLIED" in label:  # opt ver.3
        pass
    elif "SYS / SCALE FACTOR" in label:  # opt ver.3
        pass
    elif "SYS / PHASE SHIFTS" in label:  # ver.3.01
        pass
    elif "GLONASS SLOT / FRQ #" in label:  # ver.3.02
        if nav:
            p = buff[4:]
            for i in range(8):
                prn, fcn = int(p[:2].strip()), int(p[2:4].strip())
                if 1 <= prn <= MAXPRNGLO:
                    nav.glo_fcn[prn - 1] = fcn + 8
                p = p[8:]
    elif "GLONASS COD/PHS/BIS" in label:  # ver.3.02
        if nav:
            p = buff
            for i in range(4):
                if p[1:4] == "C1C":
                    nav.glo_cpbias[0] = float(p[5:13].strip())
                elif p[1:4] == "C1P":
                    nav.glo_cpbias[1] = float(p[5:13].strip())
                elif p[1:4] == "C2C":
                    nav.glo_cpbias[2] = float(p[5:13].strip())
                elif p[1:4] == "C2P":
                    nav.glo_cpbias[3] = float(p[5:13].strip())
                p = p[13:]
    elif "LEAP SECONDS" in label:  # opt
        if nav:
            nav.leaps = int(buff[:6].strip())
    elif "# OF SATELLITES" in label:  # opt
        pass
    elif "PRN / # OF OBS" in label:  # opt
        pass


