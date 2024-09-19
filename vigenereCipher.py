import math

def encode(text, key):
    result = ""
    y = 0
    x = 0
    for i in range(len(text)):
        c = text[i].lower() 
        if(y<len(key)):
            x = key[y].lower()
        else:
            y = 0
            x = key[y].lower()
        result += chr((ord(c) - 97 + ord(x) - 97) % 26 + 97)
        y += 1
    return result
def decode(text, key):
    result = ""
    y = 0
    x = 0
    for i in range(len(text)):
        c = text[i].lower()
        if(y<len(key)):
            x = key[y].lower()
        else:
            y = 0
            x = key[y].lower()
        result += chr((ord(c) - 97 - (ord(x) - 97)) % 26 + 97)
        y += 1
    return result
def subtract(text, num):
    result = ""
    result1 = ""
    for i in range(num,len(text)):
        result += text[i]
    for x in range(len(text)-num):
        result1 += chr((ord(text[x]) - 97 - (ord(result[x]) - 97)) % 26 + 97)
    return result1
def simpleSubtract(text,result):
    result1 = ""
    for x in range(len(text)):
        result1 += chr((ord(text[x]) - 97 - (ord(result[x]) - 97)) % 26 + 97)
    return result1
def crackCode(msg,num,known):
    sub0 = subtract(msg,num)
    sub = subtract(known,num)
    index = sub0.find(sub)
    final = simpleSubtract(msg[index:index+num], known[0:num])
    i = index%num
    return final[len(final)-i:len(final)]+final[0:len(final)-i]
def findLong(msg):
    temp = list()
    temp1 = list()
    for j in range(len(msg)):
        for i in range(j+2,len(msg)):
            s1 = msg[j:i]
            s2 = msg[i:-1]
            if s1 in s2:
                temp.append(s1)
    long = max(temp,key = len)
    r = temp.count(long)
    for i in range(r):
        temp.remove(long)
    long1 = max(temp,key = len)
    r1 = temp.count(long1)
    for i in range(r1):
        temp.remove(long1)
    long2 = max(temp,key = len)
    temp1.append(long)
    temp1.append(long1)
    temp1.append(long2)
    return temp1
def findGap(msg,sub):
    x = msg.find(sub)
    new = msg[x + len(sub):]
    y = new.find(sub)
    return y+len(sub)
def findFactors(x):
    temp = list()
    for i in range(1, x + 1):
        if(x % i == 0):
           temp.append(i)
    return temp
def findCode(encodedMsg, seg):
    first = findLong(encodedMsg)
    key = math.gcd(math.gcd(findGap(encodedMsg, first[0]),
    findGap(encodedMsg, first[1])),findGap(encodedMsg, first[2]))
    factors = findFactors(key)
    for i in range(len(factors)):
        if(crackCode(encodedMsg, factors[i], seg) != ""):
            code = crackCode(encodedMsg, factors[i], seg)
            break
    return code

testmsg = "weholdthesetruthstobeselfevidentthatallmenarecreatedequalthattheyareendowedbytheircreatorwithcertainunalienablerightsthatamongthesearelifelibertyandthepursuitofhappinessThattosecuretheserightsGovernmentsareinstitutedamongMenderivingtheirjustpowersfromtheconsentofthegovernedThatwheneveranyFormofGovernmentbecomesdestructiveoftheseendsitistheRightofthePeopletoalterortoabolishitandtoinstitutenewGovernmentlayingitsfoundationonsuchprinciplesandorganizingitspowersinsuchformastothemshallseemmostlikelytoeffecttheirSafetyandHappinessPrudenceindeedwilldictatethatGovernmentslongestablishedshouldnotbechangedforlightandtransientcausesandaccordinglyallexperiencehathshewnthatmankindaremoredisposedtosufferwhileevilsaresufferablethantorightthemselvesbyabolishingtheformstowhichtheyareaccustomedButwhenalongtrainofabusesandusurpationspursuinginvariablythesameObjectevincesadesigntoreducethemunderabsoluteDespotismitistheirrightitistheirdutytothrowoffsuchGovernmentandtoprovidenewGuardsfortheirfuturesecuritySuchhasbeenthepatientsufferanceoftheseColoniesandsuchisnowthenecessitywhichconstrainsthemtoaltertheirformerSystemsofGovernmentThehistoryofthepresentKingofGreatBritainisahistoryofrepeatedinjuriesandusurpationsallhavingindirectobjecttheestablishmentofanabsoluteTyrannyovertheseStatesToprovethisletFactsbesubmittedtoacandidworld"
testmsg1 = "theunanimousdeclarationofthethirteenunitedstatesofamericawheninthecourseofhumaneventsitbecomesnecessaryforonepeopletodissolvethepoliticalbandswhichhaveconnectedthemwithanotherandtoassumeamongthepowersoftheearththeseparateandequalstationtowhichthelawsofnatureandofnaturesgodentitlethemadecentrespecttotheopinionsofmankindrequiresthattheyshoulddeclarethecauseswhichimpelthemtotheseparationweholdthesetruthstobeselfevidentthatallmenarecreatedequalthattheyareendowedbytheircreatorwithcertainunalienablerightsthatamongthesearelifelibertyandthepursuitofhappinessthattosecuretheserightsgovernmentsareinstitutedamongmenderivingtheirjustpowersfromtheconsentofthegovernedthatwheneveranyformofgovernmentbecomesdestructiveoftheseendsitistherightofthepeopletoalterortoabolishitandtoinstitutenewgovernmentlayingitsfoundationonsuchprinciplesandorganizingitspowersinsuchformastothemshallseemmostlikelytoeffecttheirsafetyandhappinessprudenceindeedwilldictatethatgovernmentslongestablishedshouldnotbechangedforlightandtransientcausesandaccordinglyallexperiencehathshewnthatmankindaremoredisposedtosufferwhileevilsaresufferablethantorightthemselvesbyabolishingtheformstowhichtheyareaccustomedbutwhenalongtrainofabusesandusurpationspursuinginvariablythesameobjectevincesadesigntoreducethemunderabsolutedespotismitistheirrightitistheirdutytothrow"

testencodedmsg = "wfjrlevketgwrvvksuqeetgoffxldfpwticwamnpeocuedthauggerwdlujdtujhybtheofrwffeyujhiseuebvrrxkwhdgutbkquocoifpdbmguihjwsujdtbornhvketgdrfnlffnlbftwybpgtigsusuxiuqihbrsiogvsujdtuqvedwueujhsftlgivvgpxhroohnuudrfkqsukwuugganqqgngqdftlvjpjtiglrkwvtqqzesuirpowhferntgqtphwhfirvftqeevkauykeogyescqygqumphjowgunngqtcgfongvdfuwrvewiwgrfujhsfgqdtkwitvkeskjhuqitigseproeuqdluguosvracqoitjltbpgtpkqsukwuugqexirvftqmfpwlbalnhkwsgqxnecwipprntwfhqtlndkslfudnequgbplzjpjiuusoxgusjpvudjiosodsuqwhfovhbnosfgpmpuwljmhlzvreghhcuvkejtvaggwybpghbrsiogvsqtxdfpfejpgeffzimngidvdtfvkauirvftqmfpwsmqqgfuwacnlsiggsiqxleprtcgfhbpjeehrrmkjhucqdutdntkhnuedutgvaofdcdqudjpjlzcolfzseskhndgkaujvhfyqticwmbpniofdrforrfflsqqveevrsvhiesykimghvjnvasgvughhrbdoeujdnuquihjwtigpsfnyetdbacqoitjlnhvkegqumtvrwikfhujhybthadexsuqpeedxtxjhnbnrnhvuajprfbdxsfudnewvusrdtjqqsqwusvkqgjpyaskdbmawhfudmfqejfewewkqcfuddfulgovrrffxcfvkenwqdftdbtqouuggetrrtjupiukvtiglrskjhukwitvkejtguuawoujuoxqiftwfhhqyesppeovdnevrpsqyiegqexixasfvfptwhfkufvvxrfuhcvtltzuxcijdscghnujhpbvleovvughhrbpfephwhfuhcpnrnjgvaofvudjlsoqztigqedgvsjvbwikfhdqqsutdiouwhfowobnwesvkejtiosohrtavtfovogirvftqmfpwtigkitvrrzqitigsrfuhnumlnhqigsgdtctltbkqitckitvrrzqirfrhauggiolxrjgvaofxsvtsaukrntcolicyioilnekuedvrbkgftujhetvdbmkvhngqtphdnbdvomwweuauaopbowgutigvetvdtfuwoqtrvfvkitnhtgcfttdhsvdpiuvhduqdcbpgieyrrmf"
testencodedmsg2 = "tigxnbplmpwvdfeoascwipprfujhtikutfgquokweeuwaugvogcpeskfaxjhnjpwhferusuhogjxmbphvfpwsjveedqpetphcfuvasaiosqqeqgrpmgwoekvspnyeujhppnltjedlccqdtykidjkawgfoophcuggtigpwjvkaoqwhftdnevratuxmfcpooiwhfrrwftvogvkefcutivketgsascwebpgerwdltvdtjqqtpykidjwhfndwtqinbvxrfcqdphqauwuetirdfpwiunhtigpaegfeovuetrhcuvrtigrpjploourfncqkjpgrfsxisgvticwtigbsiqxlefhcmcueujhcbwvetykidjlmqgotigptpvketgsascwippzeiqodujhsfvuuujvtpdhsfniewkgeovwhbvdlmohnbthcsgdtffhqvcoticwtigbasghneqzeedbtiglrdthauquwjvkcftwajpxnbnleocelftlgivvticwanqqgujhsfcuemkiemkeesvbaofwhfrxrtwltphkaqrlnfuvticwtpuhcvthtigveskjhuujowgunngqttcuejpvtjvxtffdmppjmfpgeskyioiwhfkujvuwppyhrthuonvkedqqsfpwogvkehqyesphdujdtxjhnfxhrbpbfptpogirvftqmfpwbfermfugetvuudvlvfqitigvefpgsjvlsujhrjiktphwhfrhoqnhtpcotftrruqdbpnlsikwaofwojpvtjvxtfphwhqyesppeovoazkqgjvvfpwqdbvlooqqsvekpskqcjroetcqdptjaokcioilttrrwftviouxcihrrncvtpvkenukamnvefopotvoilgoyuqhfggftujhisudffvbaofkaqrlnfuvpswgeoehiofheeyllmflcucweujdthqyesppeovvlppjetvdbmkvhffvhpwodoqwbfekaoihdgquljiktbpgtscqsjgqtdcxsfudnecfcptgioioybnoeyrhrjgqcfjdtiukexpwhbvpaomlnecuenqueekvppuhduqvughhrxjllfgyimudrfuxfgguacnhticqtptlgivwhfovemxhscadbpnlsikqgujhfptpsuqzhjektigbasgdcdwvtpohdcwwwigqamqqgutdioqiacwvetcqdvuxrqcwippvpvtvujpjioxdrjcelzvketcpepdmedvhvjpfetcgetkjnuqueewfeujhmvpgescespnxtffhsqqwitoltjuwhfkurjiktjvlsujhisfxtzvrtitrwphisvekg"

i = input("Input encrypted text here:")
ii = input("Input known segment here:")
print(decode(i, findCode(i, ii)))