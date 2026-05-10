from datetime import datetime, date, timedelta
import sqlite3
from flask import Flask, session, render_template, request, g
ver = ">>> PyFlaskDb 20.03.2026 - 19.04.2026 1324 - PC 08.05.2026"
app = Flask(__name__)
app.secret_key = "sadfaweqr345tcvbbf"
app.config["SESSION_COOKIE_NAME"] = "myCOOKIE_monSTER528"
#theDatabase = "D:/2026/tutorialtid20260327.db"     # Windows
theDatabase = "/home/jsh/2026/tutorialtid20260327.db"     # Linux

devidstart = 104

sensorbeskrivelse = "Sensorbeskrivelse kommer xxx"

# OK
def adapt_date_iso(val: datetime) -> str:
    return val.isoformat()
def convert_date(val: bytes) -> datetime:
   return datetime.fromisoformat(val.decode())
def dbSQLite3Init():
    #print(">>> dbSQLite3Init")
    # OK
    sqlite3.register_adapter(datetime, adapt_date_iso)
    sqlite3.register_converter("date", convert_date)

@app.template_filter("datetimeformat")
def datetimeformat(value, format2="%Y-%m-%d %H:%M:%S"):
    #print(f">>>value: {value}")
    #print(f"Event: {value}, Date: {value} (Type: {type(value)})")
    #return value.strftime(format)
    #dt = datetime.strptime(value, format2)
    dt = value.strftime(format2)
    #print(f">>>dt: {dt}")
    return dt

@app.template_filter("closedgreen")
def closedgreen(value):
    if value == "CLOSED":
        thevalue = "<P><span style='background-color: green;'>" + value + "</span></P>"
        #thevalue = value + " OK"
    elif value == "OPEN":
        thevalue = "<P><span style='background-color: red;'>" + value + "</span></P>"        
    else:
        thevalue = value
    return thevalue


@app.template_filter("zeroseconds")
def zeroseconds(value):
    if value == 0:
        #thevalue = "<P><span style='background-color: green;'>" + value + "</span></P>"
        thevalue = ""
    else:
        thevalue = value
    return thevalue


@app.route("/", methods=["POST", "GET"])
def index():
    print(">>> index")

    devidselected = request.form.get("devidselected")
    if devidselected is None:
        devidselected = devidstart
    else:
        devidselected = int(devidselected)

    now = datetime.now()
    idag = now.strftime("%A %d.%m.%Y")
    data = get_db(0,devidselected)
    #return str(data)
    return render_template("index.html", all_data=data, tempdag=idag, dateadjust="0", sensorbeskrivelse=sensorbeskrivelse, devidselected=devidselected)



def get_db(dateadjust: int,devidselected: int):
    print(">>> get_db")
    dbSQLite3Init()
    start = datetime.now().date()
    start_date = start + timedelta(days=dateadjust)
    #print(f"start_date: {start_date}")
    end_date =  start_date + timedelta(1)
    #print(f"end_date: {end_date}")

    if isinstance(start_date, date):
        start_date = start_date.isoformat()
    if isinstance(end_date, date):
        end_date = end_date.isoformat()

    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(theDatabase, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = db.cursor()
        cursor.execute("SELECT datotid, dev, tem, hum, bar, alt, bootcount, softwareid, restartreason, "
                            " voltbattery, percentagebat, analogvalue "
                            " FROM tempdata"        # Columns 0-6
                            " WHERE DATE(datotid) = DATE(?) "
                            " AND dev = ? "
                            " ORDER BY datotid",(start_date, devidselected))
        all_data = cursor.fetchall()

        #print("****************************************************")
        #for row in all_data:
        #    print(row)
        #    #datotid2 = row[2].strftime("%d/%m/%Y %H:%M:%S")
        #    print(f"Event: {row[0]}, Date: {row[0]} (Type: {type(row[0])})")
        #print("****************************************************")

    return all_data


# 08.05.2026 *******************************************************
def get_dbbatmonitor(dateadjust: int,devidselected: int):
    print(">>> get_batmonitor")
    dbSQLite3Init()

    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(theDatabase, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = db.cursor()
        cursor.execute("SELECT "
         " datotid, dev, "
         " voltdivider, voltbattery, percentagebat, analogvalue "
         " FROM battmonitor"
         " ORDER BY datotid DESC LIMIT 100")
        all_databat = cursor.fetchall()

    return all_databat



# 19.04.2026 *******************************************************
def get_dbport(dateadjust: int,devidselected: int):
    print(">>> get_dbport")
    dbSQLite3Init()

    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(theDatabase, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = db.cursor()
        cursor.execute("SELECT datotid, dev, cmd, cmdtext, portseconds, bootcount, softwareid, restartreason from garageportdata "        # Columns 0-6
                            " ORDER BY datotid DESC LIMIT 10")
        all_dataport = cursor.fetchall()

    return all_dataport

@app.route("/port-clicked", methods=["POST"])
def port_clicked():
    print(">>> portbutton_clicked")
    # Call your Python function here
    #result_message = my_python_function()

    idag = datetime.now().strftime("%A %d.%m.%Y")

    devid2 = request.form.get("garagename")
    devid = int(devid2)
    #print(f"devid: {devid}")

    # Redirect back to home with a message
    data = get_dbport(0, devid)
    return render_template("index.html", all_dataport=data, tempdag=idag, dateadjust=0, sensorbeskrivelse=sensorbeskrivelse, devidselected=devid)

@app.route("/garageport-clicked", methods=["POST"])
def garageport_clicked():
    print(">>> garageport_clicked")
    # Call your Python function here
    #result_message = my_python_function()

    idag = datetime.now().strftime("%A %d.%m.%Y")

    #devid2 = request.form.get("garagename")
    devid = 201
    #print(f"devid: {devid}")

    # Redirect back to home with a message
    data = get_dbport(0, devid)
    return render_template("garageport.html", all_dataport=data, tempdag=idag, dateadjust=0, sensorbeskrivelse=sensorbeskrivelse, devidselected=devid)





@app.route("/batmonitor-clicked", methods=["POST"])
def batmonitor_clicked():
    print(">>> batmonitor_clicked")
    # Call your Python function here
    #result_message = my_python_function()

    idag = datetime.now().strftime("%A %d.%m.%Y")

    #devid2 = request.form.get("garagename")
    devid = 301
    #print(f"devid: {devid}")

    # Redirect back to home with a message
    data = get_dbbatmonitor(0, devid)
    return render_template("batmonitor.html", all_databat=data, tempdag=idag, dateadjust=0, sensorbeskrivelse=sensorbeskrivelse, devidselected=devid)





@app.teardown_appcontext
def close_connection(exception):
    print(">>> close_connection")
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        print(">>> close_connection 2")


# Python function to be executed
def my_python_function():
    print("Python function executed!")
    return "Function executed successfully!"

# Python function to be executed
def my_python_function_date():
    print("my_python_function_date Python function executed!")
    return "Function executed successfully!"


@app.route("/button-clicked", methods=["POST"])
def button_clicked():
    print(">>> button_clicked")
    # Call your Python function here
    #result_message = my_python_function()

    idag = datetime.now().strftime("%A %d.%m.%Y")

    devid2 = request.form.get("devid")
    devid = int(devid2)
    #print(f"devid: {devid}")

    # Redirect back to home with a message
    data = get_db(0, devid)
    return render_template("index.html", all_data=data, tempdag=idag, dateadjust=0, sensorbeskrivelse=sensorbeskrivelse, devidselected=devid)


@app.route("/date_select", methods=["POST"])
def date_select():
    print(">>> date_select")
    # Call your Python function here
    #result_message = my_python_function_date()

    devidselected = request.form.get("devid22")
    if devidselected is None:
        devidselected = devidstart
    else:
        devidselected = int(devidselected)

    dateadjust33 = 0
    dateadjust2 = 0
    #dateadjust33 = session["dateadjustnumber"]
    #print(f"dateadjust33: {dateadjust33}")

    dateselect = request.form.get("dateselect")
    #print(f"dateselect: {dateselect}")

    dateadjust33 = 0
    dateadjust44 = request.form.get("dd2")
    #print(f">>> dateadjust44: >{dateadjust44}<")
    if dateadjust44 is None:
        dateadjust33 = 0
    else:
        dateadjust33 = int(dateadjust44)

    now = datetime.now()
    dagendato = datetime.now()
    dagen = dagendato.date()

    if dateselect == "20":      # Today
        dateadjust2 = 0

    if dateselect == "10":      # En dag tilbake
        dateadjust2 = -1 + dateadjust33
        start = datetime.now().date()        # date(2026, 3, 24)
        dagen = start + timedelta(days=dateadjust2)

    if dateselect == "30":      # En dag frem
        dateadjust2 = 1 + dateadjust33
        start = datetime.now().date()              # date(2026, 3, 24)
        dagen = start + timedelta(days=dateadjust2)

    idag = dagen.strftime("%A %d.%m.%Y")

    # Redirect back to home with a message
    data = get_db(dateadjust2, devidselected)
    return render_template("index.html", all_data=data, tempdag=idag, dateadjust=dateadjust2, sensorbeskrivelse=sensorbeskrivelse, devidselected=devidselected)


if __name__ == '__main__':
    print(ver)
    #app.run()
    #app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
