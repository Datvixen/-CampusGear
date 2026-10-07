from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
app=Flask(__name__); app.secret_key="campusgear-dev"; DB=Path(__file__).with_name("campusgear.db")
CATEGORIES=["Laptop","Tablet","Camera","Projector","Charger","Lab Equipment","Other"]
CONDITIONS=["New","Good","Fair","Needs Repair","Out of Service"]
LOCATIONS=["Library","IT Department","Media Lab","Science Building","Student Center","Other"]
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 c=db(); c.execute("""CREATE TABLE IF NOT EXISTS equipment(id INTEGER PRIMARY KEY AUTOINCREMENT,asset_tag TEXT UNIQUE NOT NULL,name TEXT NOT NULL,category TEXT NOT NULL,serial_number TEXT,quantity INTEGER NOT NULL,condition TEXT NOT NULL,location TEXT NOT NULL,notes TEXT)""")
 c.execute("""CREATE TABLE IF NOT EXISTS checkouts(id INTEGER PRIMARY KEY AUTOINCREMENT,equipment_id INTEGER NOT NULL,borrower_name TEXT NOT NULL,borrower_email TEXT NOT NULL,quantity INTEGER NOT NULL,checkout_date TEXT NOT NULL,due_date TEXT NOT NULL,return_date TEXT,status TEXT NOT NULL)""")
 if c.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]==0:
  c.executemany("INSERT INTO equipment(asset_tag,name,category,serial_number,quantity,condition,location,notes) VALUES(?,?,?,?,?,?,?,?)",[("CG-1001","Dell Latitude 5440","Laptop","DL5440-01",8,"Good","IT Department","Student loaner laptops"),("CG-1002","Apple iPad","Tablet","IPAD-22",6,"Good","Library","General checkout"),("CG-1003","Canon EOS Camera","Camera","CAN-401",4,"Fair","Media Lab","Media production"),("CG-1004","Epson Projector","Projector","EP-900",3,"Good","Student Center","Presentation equipment"),("CG-1005","USB-C Charger","Charger","CHG-120",12,"Needs Repair","IT Department","Two units need inspection")])
 c.commit(); c.close()
@app.route("/")
def dashboard():
 c=db(); stats={"types":c.execute("SELECT COUNT(*) FROM equipment").fetchone()[0],"units":c.execute("SELECT COALESCE(SUM(quantity),0) FROM equipment").fetchone()[0],"repair":c.execute("SELECT COUNT(*) FROM equipment WHERE condition='Needs Repair'").fetchone()[0],"locations":c.execute("SELECT COUNT(DISTINCT location) FROM equipment").fetchone()[0]}; recent=c.execute("SELECT * FROM equipment ORDER BY id DESC LIMIT 5").fetchall(); c.close(); return render_template("dashboard.html",stats=stats,recent=recent)
@app.route("/equipment")
def equipment():
 s=request.args.get("search","").strip(); cat=request.args.get("category",""); cond=request.args.get("condition",""); loc=request.args.get("location",""); sql="SELECT * FROM equipment WHERE 1=1"; p=[]
 if s: sql+=" AND (name LIKE ? OR asset_tag LIKE ? OR serial_number LIKE ?)"; q=f"%{s}%"; p += [q,q,q]
 if cat: sql+=" AND category=?"; p.append(cat)
 if cond: sql+=" AND condition=?"; p.append(cond)
 if loc: sql+=" AND location=?"; p.append(loc)
 c=db(); items=c.execute(sql+" ORDER BY name",p).fetchall(); c.close(); return render_template("equipment.html",items=items,categories=CATEGORIES,conditions=CONDITIONS,locations=LOCATIONS,search=s,category=cat,condition=cond,location=loc)
@app.route("/equipment/add",methods=["GET","POST"])
def add_equipment():
 if request.method=="POST": return save()
 return render_template("form.html",item=None,categories=CATEGORIES,conditions=CONDITIONS,locations=LOCATIONS)
def save(item_id=None):
 vals=(request.form["asset_tag"].strip(),request.form["name"].strip(),request.form["category"],request.form.get("serial_number","").strip(),int(request.form["quantity"]),request.form["condition"],request.form["location"],request.form.get("notes","").strip()); c=db()
 try:
  if item_id: c.execute("UPDATE equipment SET asset_tag=?,name=?,category=?,serial_number=?,quantity=?,condition=?,location=?,notes=? WHERE id=?",vals+(item_id,))
  else: c.execute("INSERT INTO equipment(asset_tag,name,category,serial_number,quantity,condition,location,notes) VALUES(?,?,?,?,?,?,?,?)",vals)
  c.commit()
 except sqlite3.IntegrityError: c.close(); flash("Asset tag already exists.","danger"); return redirect(request.url)
 c.close(); flash("Equipment saved.","success"); return redirect(url_for("equipment"))
@app.route("/equipment/<int:i>/edit",methods=["GET","POST"])
def edit(i):
 c=db(); item=c.execute("SELECT * FROM equipment WHERE id=?",(i,)).fetchone(); c.close()
 if request.method=="POST": return save(i)
 return render_template("form.html",item=item,categories=CATEGORIES,conditions=CONDITIONS,locations=LOCATIONS)
@app.route("/equipment/<int:i>/delete",methods=["POST"])
def delete(i):
 c=db(); c.execute("DELETE FROM equipment WHERE id=?",(i,)); c.commit(); c.close(); return redirect(url_for("equipment"))
@app.route("/checkout")
def checkout(): return render_template("todo.html",title="Checkout & Returns",owner="Team Member 2",tasks=["Checkout form","Borrower and due dates","Return workflow","Checkout history"])
@app.route("/reports")
def reports(): return render_template("todo.html",title="Users & Reports",owner="Team Member 3",tasks=["User management","Overdue equipment","Reports/activity","Additional tests"])
if __name__=="__main__": init_db(); app.run(debug=True,host="0.0.0.0",port=5000)
