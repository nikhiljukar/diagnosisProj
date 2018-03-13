import psycopg2 as db
from buoyappconfig import *
import heapq

#input from user
users_symptom = "sore throat"


#Initialize Database connection and cursor
con = db.connect("dbname={} user={} host={} port = {}".format(my_db, my_user,my_host,my_port))
cur = con.cursor()
cur.execute("select * from symptomdiagnosistable where symptom = '{}'  ".format(users_symptom))
symptoms_arr = cur.fetchall()
symptoms=symptoms_arr[0]
#print(symptoms)
colnames = [desc[0] for desc in cur.description]
#print (colnames)

#maintain a Maxheap based on frequency of the diagnosis
heap_list = []

#loop thru each of the above output and push them in a maxheap . Each elem is an obj ( <freq> : <Diagnosis>) compare by freq
for i in range(0,len(colnames)):
    if(symptoms[i] and colnames[i]!='id' and colnames[i]!='symptom'):
        heapq.heappush(heap_list,(symptoms[i],colnames[i]))

heapq.heapify(heap_list)
print(heap_list)
print(len(heap_list))
#Default user_input
user_input = "invalid"
second_diagnosis_input = "invalid"

#Now pop max element of max heap and display <Diagnosis> to user
most_likely_dignosis = heapq.nlargest(1,heap_list)[0]
heap_list.remove(most_likely_dignosis)
most_likely_dignosis_name = most_likely_dignosis[1]
most_likely_dignosis_freq = most_likely_dignosis[0]

print(heap_list)
print(len(heap_list))
print("Is this the right Diagnosis - "+ most_likely_dignosis_name)
user_input = input("yes or no ?")
while (user_input != "yes" and user_input != "no"):
    user_input = input("Invalid input .please enter yes or no ?")

#if user says yes,
    #update its freq++ in symptomdiagnosistable


if (user_input == "yes"):
    most_likely_dignosis_freq = most_likely_dignosis_freq + 1
    cur.execute("update symptomdiagnosistable set {} = {}  where symptom = '{}'".format(most_likely_dignosis_name,most_likely_dignosis_freq,users_symptom))
    print("updated "+most_likely_dignosis_name +" to "+str(most_likely_dignosis_freq)+ ". result- "+ str(cur.rowcount))
    con.commit()

#else let user choose a diagnosis and loop to make a report
else:
    report = "\n\nReport - \nDiagnosis    :   Frequency \n"
    report_dict = dict()
    print("\nList of Diagnosis - ")
    for diagnosis in heap_list:
        most_likely_dignosis = heapq.nlargest(1,heap_list)[0]
        most_likely_dignosis_name = most_likely_dignosis[1]
        most_likely_dignosis_freq = most_likely_dignosis[0]
        report = report + "{}:{} \n".format(most_likely_dignosis_name,most_likely_dignosis_freq)
        report_dict[most_likely_dignosis_name]=most_likely_dignosis_freq
        print(most_likely_dignosis_name)
        heap_list.remove(most_likely_dignosis)

    while (second_diagnosis_input not in  report):
        second_diagnosis_input = input("\nChoose one of the above Diagnosis ")

    most_likely_dignosis_freq = report_dict[second_diagnosis_input]+1
    cur.execute("update symptomdiagnosistable set {} = {} where symptom = '{}'  ".format(second_diagnosis_input,most_likely_dignosis_freq,users_symptom))
    print("updated "+second_diagnosis_input +" to "+str(most_likely_dignosis_freq)+ ". result- "+ str(cur.rowcount))
    con.commit()
    print(report)

print ("Diagnosis Completed.Thank you for using this service")
cur.close()
con.close()
