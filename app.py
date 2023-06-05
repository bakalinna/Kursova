import psycopg2 
import psycopg2.extras 
from flask import Flask, request, render_template, g, current_app 
from flask.cli import with_appcontext 

app = Flask(__name__) 
 
# Routes 
 
@app.route("/") 
def homepage(): 
    return render_template("home.html") 
 
@app.route("/dump") 
def dump_realties(): 
    conn = get_db() 
    cursor = conn.cursor() 
    cursor.execute('select id, type, mark, price, name, surname, number, reservation_date from realties') 
    rows = cursor.fetchall() 
    output = "" 
    for r in rows: 
        debug(str(dict(r))) 
        output += str(dict(r)) 
        output += "\n" 
    return "<pre>" + output + "</pre>" 
 
@app.route("/browse") 
def browse(): 
    conn = get_db() 
    cursor = conn.cursor() 
    cursor.execute('select id, type, mark, price, name, surname, number, reservation_date from realties') 
    rowlist = cursor.fetchall() 
    return render_template('browse.html', realties=rowlist) 
 
@app.route("/write", methods=['get', 'post']) 
def write(): 
    if "step" not in request.form:      
        return render_template('write.html', step="compose_realty") 
     
    elif request.form["step"] == "add_realty": 
        conn = get_db() 
        cursor = conn.cursor() 
        cursor.execute("insert into realties (type, mark, price, name, surname, number, reservation_date) values (%s, %s, %s, %s, %s, %s, %s)", 
                   [request.form['type'], request.form['mark'], request.form['price'], request.form['name'], 
                        request.form['surname'], request.form['number'], request.form['reservation_date']]) 
        conn.commit() 
        return render_template("write.html", step="add_realty") 
 
@app.route("/delete", methods=['get', 'post']) 
def delete(): 
    debug("form data=" + str(request.form)) 
     
    if "step" not in request.form: 
        conn = get_db() 
        cursor = conn.cursor()
        cursor.execute('select id, type, mark, price, name, surname, number, reservation_date from realties') 
        rowlist = cursor.fetchall() 
        return render_template('delete.html', step="display_realties", realties=rowlist) 
         
    elif request.form["step"] == "delete_realty": 
        conn = get_db() 
        cursor = conn.cursor() 
         
        postid = int(request.form["postid"]) 
         
        cursor.execute("delete from realties where id=%s", [postid]) 
        conn.commit() 
        return render_template("delete.html", step="delete_realty") 
 
def dump_entries(): 
    conn = get_db() 
    cur = conn.cursor() 
    cur.execute("select * from realties") 
    rows = cur.fetchall() 
    print("Here are the realties:") 
    print(rows) 
      
   
def connect_db(): 
    """Connects to the database.""" 
    debug("Connecting to DB.") 
    conn = psycopg2.connect(host="localhost", user="postgres", 
                            password="admin", dbname="my_realties", cursor_factory=psycopg2.extras.DictCursor) 
    return conn 
     
def get_db(): 
    """Retrieve the database connection or initialize it. The connection 
    is unique for each request and will be reused if this is called again. 
    """ 
    if "db" not in g: 
        g.db = connect_db() 
 
    return g.db 
     
@app.teardown_appcontext 
def close_db(e=None): 
    """If this request connected to the database, close the 
    connection. 
    """ 
    db = g.pop("db", None) 
 
    if db is not None: 
        db.close() 
        debug("Closing DB") 
 
@app.route("/initdb") 
def init_db(): 
    """Clear existing data and create new tables.""" 
    conn = get_db() 
    cur = conn.cursor() 
    with current_app.open_resource("table.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit() 
    print("Initialized the database.") 
 
@app.route('/populate') 
def populate_db(): 
    conn = get_db() 
    cur = conn.cursor() 
    with current_app.open_resource("populate.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit() 
    print("Populated DB with sample data.") 
    dump_realties() 
 
def debug(s): 
    """Prints a message to the screen (not web browser)  
    if FLASK_DEBUG is set.""" 
    if app.config['DEBUG']: 
        print(s) 
 
 
if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=50100, debug=True)