from flask import Flask, render_template, request
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="xxxxxx",
    database="crms"
)

app = Flask(__name__)

cursor = db.cursor()


@app.route("/", methods=["GET", "POST"])
def index():
    query = "SELECT cases.Number, judge.Name, registry_officer.Name, cases.Court, cases.Outcome FROM cases INNER JOIN judge ON judge.ID = cases.Judge INNER JOIN registry_officer ON registry_officer.ID = cases.RegistryOfficer"
    ro_query = "SELECT ID AS id, Name AS name FROM registry_officer"
    cursor.execute(ro_query)
    registry_officers = cursor.fetchall()
    if request.method == 'POST':
        if request.form["registry_officer"] != "all":
            query += " WHERE RegistryOfficer = " + \
                str(request.form["registry_officer"])
    query += " ORDER BY cases.Number"
    cursor.execute(query)
    case_list = cursor.fetchall()

    return render_template('index.html', registry_officers=registry_officers, cases=case_list)


@app.route("/create/<entity>/<int:case>", methods=["GET", "POST"])
def create(entity, case):
    base_entities = ("Case", "Judge", "Law Clerk",
                     "Location", "Registry Officer")
    entities = ("Affidavit", "Appellant", "Case", "Factum", "Hearing", "Judge", "Law Clerk", "Location",
                "Registry Officer", "Respondent", "Witness")
    if request.method == "POST":
        if entity == "choose":
            if request.form["entity"] == base_entities[0]:
                ro_query = "SELECT ID, Name FROM registry_officer"
                cursor.execute(ro_query)
                registry_officers = cursor.fetchall()
                judge_query = "SELECT ID, Name FROM judge"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                return render_template("createCase.html", registry_officers=registry_officers, judges=judges)
            elif request.form["entity"] == base_entities[1]:
                return render_template("createJudge.html")
            elif request.form["entity"] == base_entities[2]:
                judge_query = "SELECT ID, Name FROM judge"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                return render_template("createLawClerk.html", judges=judges)
            elif request.form["entity"] == base_entities[3]:
                return render_template("createLocation.html")
            elif request.form["entity"] == base_entities[4]:
                return render_template("createRegistryOfficer.html")
        elif entity == entities[0]:
            email = request.form["email"]
            phone = request.form["phone"]
            date_given = request.form["dateGiven"]
            affiant_name = request.form["affiantName"]
            deadline = request.form["deadline"]
            date_submitted = request.form["dateSubmitted"]
            submitter = request.form["submitterName"]
            link = request.form["linkToDoc"]
            doc_insert = "INSERT into documents (caseNumber, Deadline, Submitter, linkToDoc, dateOfSubmission) VALUES ({}, '{}', '{}', '{}', '{}')"
            doc_insert = doc_insert.format(
                case, deadline, submitter, link, date_submitted)
            cursor.execute(doc_insert)
            doc_query = "SELECT docNumber FROM documents WHERE caseNumber = {} and Deadline = '{}' and Submitter = '{}' and linkToDoc = '{}' and dateOfSubmission = '{}'"
            doc_query = doc_query.format(
                case, deadline, submitter, link, date_submitted)
            new_doc = cursor.execute(doc_query).fetchone()
            doc_num = new_doc[0]
            aff_insert = "INSERT into affidavit (docNumber, email, phoneNumber, dateGiven, affiantName) VALUES ({}, '{}', '{}', '{}', '{}')"
            aff_insert = aff_insert.format(
                doc_num, email, phone, date_given, affiant_name)
            cursor.execute(aff_insert)
        elif entity == entities[1]:
            sin = request.form["sin"]
            name = request.form["name"]
            phoneNumber = request.form["phone"]
            address = request.form["address"]
            email = request.form["email"]
            barristerName = request.form["barristerName"]
            barristerEmail = request.form["barristerEmail"]
            participant_query = "SELECT * FROM participants WHERE SIN = {}"
            participant_query = participant_query.format(sin)
            cursor.execute(participant_query)
            participant_check = cursor.fetchone()
            if participant_check == None:
                partcipant_insert = "INSERT into participants (SIN, name, phoneNumber, address, email) VALUES ({}, '{}', '{}', '{}', '{}')"
                partcipant_insert = partcipant_insert.format(
                    sin, name, phoneNumber, address, email)
                cursor.execute(partcipant_insert)
            appellant_insert = "INSERT into appellant (caseNumber, SIN, barristerName, barristerEmail) VALUES ({}, {}, '{}', '{}')"
            appellant_insert = appellant_insert.format(
                case, sin, barristerName, barristerEmail)
            cursor.execute(appellant_insert)
        elif entity == entities[2]:
            judge = int(request.form["judge"])
            ro = int(request.form["registry_officer"])
            court = request.form["court"]
            case_insert = "INSERT into Cases (Judge, RegistryOfficer, Court, Outcome) VALUES ({}, {}, '{}', 'No Outcome')"
            case_insert = case_insert.format(judge, ro, court)
            cursor.execute(case_insert)
        elif entity == entities[3]:
            releventMotion = request.form["releventMotion"]
            deadline = request.form["deadline"]
            date_submitted = request.form["dateSubmitted"]
            submitter = request.form["submitterName"]
            link = request.form["linkToDoc"]
            doc_insert = "INSERT into documents (caseNumber, Deadline, Submitter, linkToDoc, dateOfSubmission) VALUES ({}, '{}', '{}', '{}', '{}')"
            doc_insert = doc_insert.format(
                case, deadline, submitter, link, date_submitted)
            cursor.execute(doc_insert)
            doc_query = "SELECT documents.docNumber FROM documents WHERE caseNumber = {} AND Deadline = '{}' AND Submitter = '{}' AND linkToDoc = '{}' AND dateOfSubmission = '{}'"
            doc_query = doc_query.format(
                case, deadline, submitter, link, date_submitted)
            cursor.execute(doc_query)
            new_doc = cursor.fetchone()
            doc_num = new_doc[0]
            factum_insert = "INSERT into factum (docNumber, releventMotion) VALUES ({}, '{}')"
            factum_insert = factum_insert.format(doc_num, releventMotion)
            cursor.execute(factum_insert)
        elif entity == entities[4]:
            hearingDate = request.form["hearingDate"]
            loc_string = request.form["id"]
            loc_string = loc_string.replace("'", "")
            loc_string = loc_string.replace("\\", "")
            loc_string = loc_string.replace("(", "")
            loc_string = loc_string.replace(")", "")
            loc_string = loc_string.split(", ")
            building = loc_string[0]
            room = loc_string[1]
            hearing_insert = "INSERT into hearing (caseNumber, Date, locationRoom, locationBuilding) VALUES ({}, '{}', '{}', '{}')"
            hearing_insert = hearing_insert.format(
                case, hearingDate, room, building)
            cursor.execute(hearing_insert)
        elif entity == entities[5]:
            name = request.form["name"]
            email = request.form["email"]
            judge_insert = "INSERT into judge (Name, Email) VALUES ('{}', '{}')"
            judge_insert = judge_insert.format(name, email)
            cursor.execute(judge_insert)
        elif entity == entities[6].replace(" ", ""):
            name = request.form["name"]
            email = request.form["email"]
            judge = int(request.form["judge"])
            clerk_insert = "INSERT into lawclerk (Name, Email, clerksFor) VALUES ('{}', '{}', {})"
            clerk_insert = clerk_insert.format(name, email, judge)
            cursor.execute(clerk_insert)
        elif entity == entities[7]:
            building = request.form["building"]
            room = int(request.form["roomNum"])
            city = request.form["city"]
            seating_cap = int(request.form["seatingCap"])
            loc_insert = "INSERT into location (Building, roomNum, City, seatingCap) VALUES ('{}', {}, '{}', {})"
            loc_insert = loc_insert.format(building, room, city, seating_cap)
            cursor.execute(loc_insert)
        elif entity == entities[8].replace(" ", ""):
            name = request.form["name"]
            email = request.form["email"]
            ro_insert = "INSERT into registry_officer (Name, Email) VALUES ('{}', '{}')"
            ro_insert = ro_insert.format(name, email)
            cursor.execute(ro_insert)
        elif entity == entities[9]:
            sin = request.form["sin"]
            name = request.form["name"]
            phoneNumber = request.form["phone"]
            address = request.form["address"]
            email = request.form["email"]
            barristerName = request.form["barristerName"]
            barristerEmail = request.form["barristerEmail"]
            participant_query = "SELECT * FROM participants WHERE SIN = {}"
            participant_query = participant_query.format(sin)
            cursor.execute(participant_query)
            participant_check = cursor.fetchone()
            if participant_check == None:
                partcipant_insert = "INSERT into participants (SIN, name, phoneNumber, address, email) VALUES ({}, '{}', '{}', '{}', '{}')"
                partcipant_insert = partcipant_insert.format(
                    sin, name, phoneNumber, address, email)
                cursor.execute(partcipant_insert)
            respondent_insert = "INSERT into respondent (caseNumber, SIN, barristerName, barristerEmail) VALUES ({}, {}, '{}', '{}')"
            respondent_insert = respondent_insert.format(
                case, sin, barristerName, barristerEmail)
            cursor.execute(respondent_insert)
        elif entity == entities[10]:
            sin = request.form["sin"]
            name = request.form["name"]
            phoneNumber = request.form["phone"]
            address = request.form["address"]
            email = request.form["email"]
            participant_query = "SELECT * FROM participants WHERE SIN = {}"
            participant_query = participant_query.format(sin)
            cursor.execute(participant_query)
            participant_check = cursor.fetchone()
            if participant_check == None:
                partcipant_insert = "INSERT into participants (SIN, name, phoneNumber, address, email) VALUES ({}, '{}', '{}', '{}', '{}')"
                partcipant_insert = partcipant_insert.format(
                    sin, name, phoneNumber, address, email)
                cursor.execute(partcipant_insert)
            witness_insert = "INSERT into witness (caseNumber, SIN) VALUES ({}, {})"
            witness_insert = witness_insert.format(case, sin)
            cursor.execute(witness_insert)
        try:
            db.commit()
            return render_template("success.html")
        except Exception as e:
            print(e)
            return render_template("error.html")
    else:
        if entity == "choose":
            return render_template("create.html", entities=base_entities)
        elif entity == "Hearing":
            loc_query = "SELECT Building, roomNum, City FROM location"
            cursor.execute(loc_query)
            locations = cursor.fetchall()
            return render_template("createHearing.html", case=case, locations=locations)
        else:
            create_string = entity.replace(" ", "")
            return render_template("create" + create_string + ".html", case=case)


@app.route("/delete/<entity>/<case_num>/<id>", methods=["GET", "POST"])
def delete(entity, case_num, id):
    base_entities = ("Judge", "Law Clerk", "Location", "Registry Officer")
    entities = ("Affidavit", "Appellant", "Case", "Factum", "Hearing", "Judge", "Law Clerk", "Location",
                "Registry Officer", "Respondent", "Witness")

    if request.method == "POST":
        if entity == "choose":
            if request.form["entity"] == base_entities[0]:
                judge_query = "SELECT ID, Name FROM judge ORDER by ID"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                return render_template("deleteJudge.html", judges=judges)
            elif request.form["entity"] == base_entities[1]:
                clerk_query = "SELECT ID, Name FROM lawclerk"
                cursor.execute(clerk_query)
                clerks = cursor.fetchall()
                return render_template("deleteLawClerk.html", clerks=clerks)
            elif request.form["entity"] == base_entities[2]:
                loc_query = "SELECT Building, roomNum, City FROM location"
                cursor.execute(loc_query)
                locations = cursor.fetchall()
                return render_template("deleteLocation.html", locations=locations)
            elif request.form["entity"] == base_entities[3]:
                ro_query = "SELECT ID, Name FROM registry_officer ORDER by ID"
                cursor.execute(ro_query)
                registry_officers = cursor.fetchall()
                return render_template("deleteRegistryOfficer.html", registry_officers=registry_officers)
        elif entity == entities[5]:
            judge_id = request.form["id"]
            judge_delete = "DELETE FROM judge WHERE ID = {}"
            judge_delete = judge_delete.format(judge_id)
            cursor.execute(judge_delete)
        elif entity == entities[6].replace(" ", ""):
            lc_id = request.form["id"]
            lc_delete = "DELETE FROM lawclerk WHERE ID = {}"
            lc_delete = lc_delete.format(lc_id)
            cursor.execute(lc_delete)
        elif entity == entities[7]:
            loc_string = request.form["id"]
            loc_string = loc_string.replace("'", "")
            loc_string = loc_string.replace("\\", "")
            loc_string = loc_string.replace("(", "")
            loc_string = loc_string.replace(")", "")
            loc_string = loc_string.split(", ")
            building = loc_string[0]
            room = loc_string[1]
            loc_delete = "DELETE FROM location WHERE Building = '{}' AND roomNum = {}"
            loc_delete = loc_delete.format(building, room)
            cursor.execute(loc_delete)
        elif entity == entities[8].replace(" ", ""):
            ro_id = request.form["id"]
            ro_delete = "DELETE FROM registry_officer WHERE ID = {}"
            ro_delete = ro_delete.format(ro_id)
            cursor.execute(ro_delete)
        try:
            db.commit()
            return render_template("success.html")
        except Exception as e:
            print(e)
            return render_template("error.html")
    else:
        if entity == "choose":
            return render_template("delete.html", entities=base_entities)
        elif entity == entities[0] or entity == entities[3]:
            doc_delete = "DELETE FROM documents WHERE docNumber = {}"
            doc_delete = doc_delete.format(id)
            cursor.execute(doc_delete)
        elif entity == entities[1]:
            appellant_delete = "DELETE FROM appellant WHERE SIN = {} and caseNumber = {}"
            appellant_delete = appellant_delete.format(id, case_num)
            cursor.execute(appellant_delete)
        elif entity == entities[2]:
            case_delete = "DELETE FROM cases WHERE Number = {}"
            case_delete = case_delete.format(id)
            cursor.execute(case_delete)
        elif entity == entities[4]:
            hearing_delete = "DELETE FROM hearing WHERE caseNumber = {} and Date = {}"
            hearing_delete = hearing_delete.format(case_num, id)
            cursor.execute(hearing_delete)
        elif entity == entities[9]:
            respondent_delete = "DELETE FROM respondent WHERE SIN = {} and caseNumber = {}"
            respondent_delete = respondent_delete.format(id, case_num)
            cursor.execute(respondent_delete)
        elif entity == entities[10]:
            witness_delete = "DELETE FROM witness WHERE SIN = {} and caseNumber = {}"
            witness_delete = witness_delete.format(id, case_num)
            cursor.execute(witness_delete)
        try:
            db.commit()
            return render_template("success.html")
        except Exception as e:
            print(e)
            return render_template("error.html")


@app.route("/update/<entity>/<case_num>/<id>", methods=["GET", "POST"])
def update(entity, case_num, id):
    courts = ("FC", "FCA", "TCC", "CMAC")
    base_entities = ("Judge", "Law Clerk", "Location", "Registry Officer")
    entities = ("Affidavit", "Appellant", "Case", "Factum", "Hearing", "Judge", "Law Clerk", "Location",
                "Registry Officer", "Respondent", "Witness")
    if request.method == 'POST':
        if entity == "choose":
            if request.form["entity"] == base_entities[0]:
                judge_query = "SELECT * FROM judge ORDER by ID"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                return render_template("updateJudge.html", judges=judges)
            elif request.form["entity"] == base_entities[1]:
                judge_query = "SELECT ID, Name FROM judge"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                clerk_query = "SELECT ID, Name FROM lawclerk"
                cursor.execute(clerk_query)
                clerks = cursor.fetchall()
                return render_template("updateLawClerk.html", judges=judges, clerks=clerks)
            elif request.form["entity"] == base_entities[2]:
                loc_query = "SELECT Building, roomNum, City FROM location"
                cursor.execute(loc_query)
                locations = cursor.fetchall()
                return render_template("updateLocation.html", locations=locations)
            elif request.form["entity"] == base_entities[3]:
                ro_query = "SELECT * FROM registry_officer ORDER by ID"
                cursor.execute(ro_query)
                registry_officers = cursor.fetchall()
                return render_template("updateRegistryOfficer.html", registry_officers=registry_officers)
        elif entity == entities[0]:
            submitter = request.form["submitterName"]
            date_submitted = request.form["dateSubmitted"]
            link = request.form["linkToDoc"]
            date_given = request.form["dateGiven"]
            affiant_name = request.form["affiantName"]
            phone = request.form["phone"]
            email = request.form["email"]
            deadline = request.form["deadline"]
            affidavit_update = "UPDATE affidavit SET dateGiven = '{}', affiantName = '{}', phoneNumber = '{}', email = '{}' WHERE docNumber = {}"
            affidavit_update = affidavit_update.format(
                date_given, affiant_name, phone, email, id)
            doc_update = "UPDATE documents SET Submitter = '{}', dateOfSubmission = '{}', linkToDoc = '{}', Deadline = '{}' WHERE docNumber = {}"
            doc_update = doc_update.format(
                submitter, date_submitted, link, deadline, case_num, id)
            cursor.execute(affidavit_update)
            cursor.execute(doc_update)
        elif entity == entities[1]:
            appellant_update = "Update appellant SET WHERE "
            appellant_update = appellant_update.format()
            cursor.execute(appellant_update)
        elif entity == entities[2]:
            judge = int(request.form["judge"])
            ro = int(request.form["registry_officer"])
            court = request.form["court"]
            outcome = request.form["outcome"]
            case_update = "UPDATE cases SET Judge = {}, RegistryOfficer = {}, Court = '{}', Outcome = '{}' WHERE cases.Number = {}"
            case_update = case_update.format(
                judge, ro, court, outcome, case_num)
            cursor.execute(case_update)
        elif entity == entities[3]:
            factum_update = "UPDATE factum SET WHERE"
            factum_update = factum_update.format()
            cursor.execute(factum_update)
        elif entity == entities[4]:
            hearing_update = "UPDATE hearing SET WHERE"
            hearing_update = hearing_update.format()
            cursor.execute(hearing_update)
        elif entity == entities[5]:
            judge_id = int(request.form["id"])
            name = request.form["name"]
            email = request.form["email"]
            judge_update = "UPDATE judge SET Name = '{}', Email = '{}' WHERE ID = {}"
            judge_update = judge_update.format(name, email, judge_id)
            cursor.execute(judge_update)
        elif entity == entities[6].replace(" ", ""):
            lc_id = int(request.form["id"])
            name = request.form["name"]
            email = request.form["email"]
            judge = int(request.form["judge"])
            lc_update = "UPDATE lawclerk SET Name = '{}', Email = '{}', clerksFor = {} WHERE ID = {}"
            lc_update = lc_update.format(name, email, judge, lc_id)
            cursor.execute(lc_update)
        elif entity == entities[7]:
            loc_string = request.form["id"]
            loc_string = loc_string.replace("'", "")
            loc_string = loc_string.replace("\\", "")
            loc_string = loc_string.replace("(", "")
            loc_string = loc_string.replace(")", "")
            loc_string = loc_string.split(", ")
            building = loc_string[0]
            room = loc_string[1]
            seating_cap = int(request.form["seatingCap"])
            lc_update = "UPDATE location SET seatingCap = {} WHERE Building = '{}' AND roomNum = {}"
            lc_update = lc_update.format(seating_cap, building, room)
            cursor.execute(lc_update)
        elif entity == entities[8].replace(" ", ""):
            ro_id = request.form["id"]
            name = request.form["name"]
            email = request.form["email"]
            ro_update = "UPDATE registry_officer SET Name = '{}', Email = '{}' WHERE ID = {}"
            ro_update = ro_update.format(name, email, ro_id)
            cursor.execute(ro_update)
        elif entity == entities[9]:
            respondent_update = "UPDATE respondent SET WHERE"
            respondent_update = respondent_update.format()
            cursor.execute(respondent_update)
        elif entity == entities[10]:
            witness_update = "UPDATE witness SET WHERE"
            witness_update = witness_update.format()
            cursor.execute(witness_update)
        try:
            db.commit()
            return render_template("success.html")
        except Exception as e:
            print(e)
            return render_template("error.html")
    else:
        if entity == "choose":
            return render_template("update.html", entities=base_entities)
        elif entity == "Affidavit":
            affidavit_query = "SELECT Submitter, dateOfSubmission, linkToDoc, dateGiven, affiantName, phoneNumber, email, Deadline FROM documents INNER JOIN affidavit ON documents.docNumber = affidavit.docNumber WHERE documents.caseNumber = {} AND affidavit.docNumber = {}"
            affidavit_query = affidavit_query.format(case_num, id)
            cursor.execute(affidavit_query)
            affidavit = cursor.fetchone()
            return render_template("updateAffidavit.html", affidavit=affidavit, case=case_num, id=id)
        elif entity == "Appellant":
            return render_template("updateAppellant.html", case=case_num, id=id)
        elif entity == "Case":
            case_query = "SELECT * FROM cases WHERE cases.number = {}"
            case_query = case_query.format(case_num)
            cursor.execute(case_query)
            case = cursor.fetchone()
            ro_query = "SELECT ID, Name FROM registry_officer"
            cursor.execute(ro_query)
            registry_officers = cursor.fetchall()
            judge_query = "SELECT ID, Name FROM judge"
            cursor.execute(judge_query)
            judges = cursor.fetchall()
            hearing_query = "SELECT Date, Building, roomNum, City FROM hearing inner join location WHERE locationRoom = roomNum AND locationBuilding = Building AND caseNumber = {}"
            hearing_query = hearing_query.format(case_num)
            cursor.execute(hearing_query)
            hearings = cursor.fetchall()
            appellants_query = "SELECT appellant.SIN, name, phoneNumber, address, barristerName, barristerEmail FROM participants JOIN appellant ON appellant.SIN = participants.SIN WHERE caseNumber = {}"
            appellants_query = appellants_query.format(case_num)
            cursor.execute(appellants_query)
            appellants = cursor.fetchall()
            respondents_query = "SELECT respondent.SIN, name, phoneNumber, address, barristerName, barristerEmail FROM participants JOIN respondent ON respondent.SIN = participants.SIN WHERE caseNumber = {}"
            respondents_query = respondents_query.format(case_num)
            cursor.execute(respondents_query)
            respondents = cursor.fetchall()
            witness_query = "SELECT witness.SIN, name, phoneNumber, email, address FROM participants JOIN witness ON witness.SIN = participants.SIN WHERE caseNumber = {}"
            witness_query = witness_query.format(case_num)
            cursor.execute(witness_query)
            witnesses = cursor.fetchall()
            factum_query = "SELECT documents.docNumber, Submitter, dateOfSubmission, linkToDoc, releventMotion, Deadline FROM documents JOIN factum ON factum.docNumber = documents.docNumber WHERE documents.caseNumber = {}"
            factum_query = factum_query.format(case_num)
            cursor.execute(factum_query)
            factums = cursor.fetchall()
            affidavit_query = "SELECT documents.docNumber, Submitter, dateOfSubmission, linkToDoc, dateGiven, affiantName, phoneNumber, email, Deadline FROM documents JOIN affidavit ON documents.docNumber = affidavit.docNumber WHERE documents.caseNumber = {}"
            affidavit_query = affidavit_query.format(case_num)
            cursor.execute(affidavit_query)
            affidavits = cursor.fetchall()
            return render_template('updateCase.html', case=case, registry_officers=registry_officers, judges=judges,
                                   hearings=hearings, appellants=appellants, respondents=respondents, id=case_num,
                                   witnesses=witnesses, factums=factums, affidavits=affidavits, courts=courts)
        elif entity == "Factum":
            return render_template("updateFactum.html", case=case_num, id=id)
        elif entity == "Hearing":
            return render_template("updateHearing.html", case=case_num, id=id)
        elif entity == "Respondent":
            return render_template("updateRespondent.html", case=case_num, id=id)
        elif entity == "Witness":
            return render_template("updateWitness.html", case=case_num, id=id)


@app.route("/view/<entity>/", methods=["GET", "POST"])
def view(entity):
    base_entities = ("Judges", "Law Clerks", "Locations", "Registry Officers")

    if request.method == 'POST':
        if entity == "choose":
            if request.form["entity"] == base_entities[0]:
                judge_query = "SELECT Name, Email FROM judge ORDER by ID"
                cursor.execute(judge_query)
                judges = cursor.fetchall()
                return render_template("viewJudge.html", judges=judges)
            elif request.form["entity"] == base_entities[1]:
                clerk_query = "SELECT lawclerk.Name, lawclerk.Email, judge.Name FROM lawclerk JOIN judge ON judge.ID = clerksFor"
                cursor.execute(clerk_query)
                clerks = cursor.fetchall()
                return render_template("viewLawClerk.html", clerks=clerks)
            elif request.form["entity"] == base_entities[2]:
                loc_query = "SELECT * FROM location"
                cursor.execute(loc_query)
                locations = cursor.fetchall()
                return render_template("viewLocation.html", locations=locations)
            elif request.form["entity"] == base_entities[3]:
                ro_query = "SELECT Name, Email FROM registry_officer ORDER by ID"
                cursor.execute(ro_query)
                registry_officers = cursor.fetchall()
                return render_template("viewRegistryOfficer.html", registry_officers=registry_officers)
    else:
        if entity == "choose":
            return render_template("view.html", entities=base_entities)


if __name__ == "__main__":
    app.run(debug=True)
