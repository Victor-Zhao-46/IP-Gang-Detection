def compare(ip):                   #this program first cleans up the specific gang file by
    tmp=ip.strip("::ffff:")         #retaining only the rather frequent attackers
    a,b,c,d=tmp.split('.')          #and then does the hashing required for visualization.
    if(len(d)>=3):
        if(d[len(d)-3]=='r'):       #this compare function is for sorting
            d=d.strip('r'+d[len(d)-2]+d[len(d)-3])    #very unrefined! changes likely needed
    if(len(a)==2):
        a='0'+a
    elif(len(a)==1):
        a="00"+a
    if(len(b)==2):
        b='0'+b
    elif(len(b)==1):
        b="00"+b
    if(len(c)==2):
        c='0'+c
    elif(len(c)==1):
        c="00"+c
    if(len(d)==2):
        d='0'+d
    elif(len(d)==1):
        d="00"+d
    return int(a+b+c+d)

#is it possible that Neo4j is not using the node based connections for the ip addresses,
#and is instead going over all the groups to find those affiliated to

def hash(directory):
    uri = "bolt://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "nsfocus2016"))
    with driver.session() as session:
        f=open(directory+"specific_gang_cleaned.txt")
        outfile=open(directory+"ip_hash.txt",'w')
        outfiletime=open(directory+"ip_hash_time.txt",'w')
        for line in f: #each line is a gang(botnet)
            if(line=='\n'):
                print("stray new line")
                break
            #temp=line.strip('\n')
            #if(temp!=line):
            #    print("stray \\n at line end")
            #line=temp
            print("Hey!") #to track progress
            line=line.strip('\n')  #stripping the new line that is always present at the end
            line,gangid=line.split('\\')  #gangid is the id of the current gang
            line=line.strip(' ')  #there is always another stray space at the end
            line=line.split(' ')
            for ip in line:  #here each ip is an ip in the gang(botnet)
                response=session.run("match (current_ip:ips),(current_ip)-[:BELONGS_TO]->(OAVS:groups)"
                                     "where (current_ip.ip=\""+ip+"\") return OAVS")
                tmp=[]
                for item in response:    #respones appears to be a pointer that points to a data
                    tmp.append(item["OAVS"].properties)    #in the memory that self-destructs
                #for item in response:                      after being accessed once, yet we need to
                #    outfile.write(item["OAVS"].properties["id"]+' ')      access it twice, so we
                for item in tmp:                                  #extract the data from the memory
                    outfile.write(item["id"]+' ')               #and then refer to the data directly.
                outfile.write('\n')    #in the finished output file each line represents
                #for item in response:  #the activity of an ip address.
                #    outfiletime.write(item["OAVS"].properties["time"]+' ')
                for item in tmp:
                    outfiletime.write(item["time"]+' ')
                outfiletime.write('\n')
            outfile.write("gang_end\\"+gangid+'\n')
            outfiletime.write("gang_end\\"+gangid+'\n')
        f.close()
        outfile.close()
        outfiletime.close()

#description:this program differs from previous clean_up programs in that this one does not use the zz txt files for data, instead using the neo4j database,
#and the output has some format changes as well, namely: only the gangs with pa6 ip addresses or more will be outputted, and in the output file each line represents a gang of ip addresses.
#the pa4=0 part is not entirely functional for now because I did not specify how many gangs to go through if pa4=0. For now, I am experimenting with pa4 values of below 0.1 to simulate
#a pa4=0 effect.
from random import randint
from neo4j.v1 import GraphDatabase,basic_auth
#directory=input("Please enter the directory in which the files are stored\n")
directory="//home//victor//Neo4j_version//2_months_benchmark//Pa3_0.6//"
f=open(directory+"specific_gang.txt")
outfile=open(directory+"specific_gang_cleaned.txt",'w')
report=open(directory+"clean_up_report.txt","a")
#outfile_raw=open(directory+"gang_raw.txt",'w')
#simple_gang=open("simple_gang.txt",'w')
#configuration here
pa4=0.1    #the screening threshold
pa5=500    #the amount of ip addresses to be randomly chosen in case pa4 is 0
pa6=10    #minimum size of gang that counts as a big gang. This size is the number of organized attack events attributed to the gang!
gang_count=-1    #counts the number of gangs to mark the id of each.
twice_count=0 #counts the times  an IP address appears at least twice in a single OAV
group_count=0
totip=0

report.write("This clean up has parameters: pa4="+str(pa4)+",pa5="+str(pa5)+",pa6="+str(pa6)+'\n')
report.write("The number of IP addresses in the gangs are as follows:\n")
for line in f: #each line is a OAV cluster
    count={}
    tmp=line.split(',')    #tmp becomes a list of OAVs
    total=0 #counts the number of OAVs in each gang, is cleared to 0 for each gang/
    gang_count+=1
    if(len(tmp)<pa6):    #this skips all the gangs that don't have enough organized attack events.
        continue
    for item in tmp:  #each item is an OAV
        if(item=='\n'):
            print("Hey!")
            break
        item=item.strip('\n')
        uri="bolt://127.0.0.1:7687"
        driver=GraphDatabase.driver(uri,auth=basic_auth("neo4j","nsfocus2016"))
        with driver.session() as session: #how does this work, and why does the line below not work?
            #response=driver.session.run("match current_group:groups,current_group-[:CONTAINS]->sources:ips where (current_group.id=\""+str(item)+"\") return sources.ip")
            response=session.run("match (current_group:groups),(current_group)-[:CONTAINS]->(sources:ips) where (current_group.id=\""+str(item)+"\") return sources.ip")
        check={}
        for ip in response:
            e=ip["sources.ip"]
            if(e in count):
                if(e not in check):
                    count[e]+=1    #this counts the number of times an ip address appears in an
                else:               #OAV cluster
                    #print("Hey!\n")
                    twice_count+=1
                    #print(e)
                    #print(item)
            else:
                count[e]=1
                check[e]=1
        total+=1
    group_count+=total
    sortip=[]
    for item in count.items():
        #outfile_raw.write(str(item[1]))
        if(item[1]>total*pa4):    #we do this no matter pa4 is 0 or not
            sortip.append(item[0])
            #tmp=item[0]
            #outfile.write(item[0])
            #outfile.write(' ')
    #outfile.write('\n')
    #print('\n')
    if(pa4==0):    #special treatment for pa4=0: randomly select some IP addresses
        temp=[]
        tmp=len(sortip)-1
        for i in range(0,pa5+1):
            temp.append(sortip[randint(0,tmp)])
        sortip=temp
        temp=[]
    #for item in sort.items():
        #print(item)
    #    outfile_raw.write(str(item))
    #    outfile_raw.write('\n')

    #step:sorting ip addresses that are known to be in the gang to make the
    #output file look better
    sortip.sort(key=compare)
    report.write(str(len(sortip))+'\n')
    totip+=len(sortip)
    for item in sortip:    #each item here is a valid ip address member of the current gang.
        outfile.write(item+' ')
    outfile.write('\\'+str(gang_count)+'\n')

report.write("In total, "+str(totip)+" ip addresses were classified.\n")
report.write("There were "+str(twice_count)+" duplicate source IPs in the same group\n")
report.write("There were "+str(group_count)+" groups in total\n\n")
print(twice_count)
print(group_count)
#outfile.write(str(gang_count))
f.close()
outfile.close()
report.close()
#outfile_raw.close()
hash(directory) #finally, hash the ip addresses to ready them for visualization
