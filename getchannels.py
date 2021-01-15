import sys

# Example call:
# python getchannels.py newslave pos-13E.php 4

server = sys.argv[1] # newslave
inputFilename = sys.argv[2] #"pos-13E.php"
outputFilename = sys.argv[2].replace("php", "m3u") #"13E_satip.m3u"
source = sys.argv[3] #"4"



newTransponder = 0
newChannel = 0
newRadioChannel = 0
opidArray = []
channelname = ""
frequency = ""
polarity = ""
delsys = ""
modulation = ""
sysmrate = ""

f = open(inputFilename, "r")
o = open(outputFilename, "w")

for line in f:
	if(newRadioChannel > 0):
		# skip next line
		if(newRadioChannel < 2):		
			newRadioChannel = newRadioChannel + 1
			continue
		elif(newRadioChannel == 2):
			channelname, ignore1 = line.lstrip().split('<', 1)
			newRadioChannel = newRadioChannel + 1
			#print(channelname)
		# skip next 6 lines		
		elif(newRadioChannel < 9):
			newRadioChannel = newRadioChannel + 1
			continue
		elif(newRadioChannel == 9):
			#print(line)
			ignore1, apid = line.split('>', 1)
			apid = apid.split('<', 1)[0]
			apid = apid.split('&', 1)[0]
			apid = apid.split(" ", 1)[0]			
			#print(apid)
			newRadioChannel = newRadioChannel + 1
		else:
			if("pid\">" in line):
				ignore1, opid = line.split('>', 1)
				opid = opid.split('<', 1)[0]
				opid = opid.split('&', 1)[0]
				opid = opid.split(" ", 1)[0]
				#print(opid)
				opidArray.extend([opid])
				newRadioChannel = newRadioChannel + 1
				continue
			else:
				# Build up rtsp:// line here
				# Example m3u from dd SW:
				# #EXTINF:0,SRF 1 HD
				# rtsp://@mmslave/?src=4&freq=10971&pol=h&msys=dvbs2&sr=29700&pids=0,501,502,507,503,504,505,502&x_pmt=501
				description = "#EXTINF:0," + channelname
				url = "rtsp://@" + server + "/?src=" + source + "&freq=" + frequency + "&pol=" + polarity  
				url = url + "&msys=" + delsys + "&mtype=" + modulation + "&sr=" + symrate + "&pids=0," + apid
				for i in opidArray:
					url = url + "," + i
				o.write(description + "\n")
				o.write(url + "\n")
				newRadioChannel = 0
				opidArray = []
				continue
	elif(newChannel > 0):
		# skip next 6 lines
		if(newChannel < 6):
			newChannel = newChannel + 1
			continue
		elif(newChannel == 6):
			ignore1, vpid = line.split('>', 1)
			vpid, ignore1 = vpid.split('<', 1)
			vpid = vpid.split(" ", 1)[0]			
			#print(vpid)
			newChannel = newChannel + 1
			continue
		elif(newChannel == 7):
			ignore1, apid = line.split('>', 1)
			apid = apid.split('<', 1)[0]
			apid = apid.split('&', 1)[0]
			apid = apid.split(" ", 1)[0]			
			#print(apid)
			newChannel = newChannel + 1
			continue
		else:
			if("pid\">" in line):
				ignore1, opid = line.split('>', 1)
				opid = opid.split('<', 1)[0]
				opid = opid.split('&', 1)[0]
				opid = opid.split(" ", 1)[0]
				#print(opid)
				opidArray.extend([opid])
				newChannel = newChannel + 1
				continue
			else:
				# Build up rtsp:// line here
				# Example m3u from dd SW:
				# #EXTINF:0,SRF 1 HD
				# rtsp://@mmslave/?src=4&freq=10971&pol=h&msys=dvbs2&sr=29700&pids=0,501,502,507,503,504,505,502&x_pmt=501
				description = "#EXTINF:0," + channelname
				url = "rtsp://@" + server + "/?src=" + source + "&freq=" + frequency + "&pol=" + polarity  
				url = url + "&msys=" + delsys + "&mtype=" + modulation + "&sr=" + symrate + "&pids=0," + vpid + "," + apid
				for i in opidArray:
					url = url + "," + i
				o.write(description + "\n")
				o.write(url + "\n")
				newChannel = 0
				opidArray = []
				continue
	elif(newTransponder == 0):
		if("<table class=\"frq\">" in line):	
			# new transponder table
			newTransponder = 1;
			continue
		if(" title=\"Id:" in line):
			# new channel
			ignore1, rest = line.split(':', 1)
			channelname, rest = rest.lstrip().split('"', 1)
			#print(channelname)
			newChannel = 1
		if("<img src=\"/radio.gif\"" in line):
			# new radio channel			
			newRadioChannel = 1
	elif(newTransponder == 1):
		if("class=\"bld\">" in line):
			newTransponder = 2
			continue
	elif(newTransponder == 2):
		if("class=\"bld\">" in line):
			ignore1, rest = line.split('>', 1)
			frequency, rest = rest.split('<', 1)
			frequency, ignore1 = frequency.split('.', 1)
			ignore1, ignore2, rest = rest.split('>', 2)
			polarity, rest = rest.split('<', 1)
			ignore1, ignore2, ignore3, ignore4, ignore5, ignore6, ignore7, ignore8, ignore9, rest = rest.split('<', 9)
			ignore1, rest = rest.split('>', 1)
			delsys, rest = rest.split('<', 1)
			delsys = delsys.replace('-', '')
			ignore1, ignore2, rest = rest.split('>', 2)			
			modulation, rest = rest.split('<', 1)
			ignore1, ignore2, ignore3, rest = rest.split('>', 3)
			symrate, rest = rest.split('<', 1)
			#print("Freq: " + frequency + " Pol: " + polarity + " Delsys: " + delsys + " Modulation: " + modulation + " Symbolrate: " + symrate)
			#print(rest)
			newTransponder = 0
	
						
f.close()
o.close()
