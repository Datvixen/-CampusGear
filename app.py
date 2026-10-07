from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import date
app=Flask(__name__); app.secret_key="campusgear-dev"; DB=Path(__file__).with_name("campusgear.db")
CATEGORIES=["Laptop","Tablet","Camera","Projector","Charger","Lab Equipment","Other"]
CONDITIONS=["New","Good","Fair","Needs Repair","Out of Service"]
LOCATIONS=["Library","IT Department","Media Lab","Science Building","Student Center","Other"]
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def refresh_overdue_statuses():
 c=db()
 c.execute("UPDATE checkouts SET status=CASE WHEN due_date < ? THEN 'Overdue' ELSE 'Checked Out' END WHERE return_date IS NULL",(date.today().isoformat(),))
 c.commit(); c.close()
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
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
 refresh_overdue_statuses()
 c=db()
 form_data=request.form if request.method=="POST" else {}
 if request.method=="POST":
  borrower_name=request.form.get("borrower_name","").strip()
  borrower_email=request.form.get("borrower_email","").strip()
  raw_equipment_id=request.form.get("equipment_id","")
  raw_quantity=request.form.get("quantity","")
  checkout_date=request.form.get("checkout_date","")
  due_date=request.form.get("due_date","")
  error=None
  try: equipment_id=int(raw_equipment_id)
  except (TypeError,ValueError): equipment_id=None
  try: quantity=int(raw_quantity)
  except (TypeError,ValueError): quantity=None
  try: checkout_day=date.fromisoformat(checkout_date)
  except ValueError: checkout_day=None
  try: due_day=date.fromisoformat(due_date)
  except ValueError: due_day=None
  if not borrower_name: error="Borrower name is required."
  elif not borrower_email: error="Borrower email is required."
  elif quantity is None or quantity < 1: error="Quantity must be at least 1."
  elif checkout_day is None: error="Enter a valid checkout date."
  elif due_day is None: error="Enter a valid due date."
  elif due_day < checkout_day: error="Due date cannot be before the checkout date."
  elif equipment_id is None: error="Select a valid equipment item."
  if error:
   flash(error,"danger")
  else:
   c.execute("BEGIN IMMEDIATE")
   item=c.execute("SELECT quantity FROM equipment WHERE id=?",(equipment_id,)).fetchone()
   if item is None:
    c.rollback()
    flash("The selected equipment could not be found.","danger")
   else:
    checked_out=c.execute("SELECT COALESCE(SUM(quantity),0) FROM checkouts WHERE equipment_id=? AND return_date IS NULL",(equipment_id,)).fetchone()[0]
    available=item["quantity"]-checked_out
    if quantity > available:
     c.rollback()
     flash(f"Only {max(0,available)} unit(s) are currently available.","danger")
    else:
     c.execute("INSERT INTO checkouts(equipment_id,borrower_name,borrower_email,quantity,checkout_date,due_date,return_date,status) VALUES(?,?,?,?,?,?,NULL,?)",(equipment_id,borrower_name,borrower_email,quantity,checkout_date,due_date,"Checked Out"))
     c.commit()
     c.close()
     flash("Equipment checked out successfully.","success")
     return redirect(url_for("checkout"))
 items=c.execute("SELECT e.id,e.asset_tag,e.name,e.quantity-COALESCE((SELECT SUM(ch.quantity) FROM checkouts ch WHERE ch.equipment_id=e.id AND ch.return_date IS NULL),0) AS available_quantity FROM equipment e ORDER BY e.name").fetchall()
 active_checkouts=c.execute("SELECT ch.*,e.name AS equipment_name,e.asset_tag FROM checkouts ch LEFT JOIN equipment e ON e.id=ch.equipment_id WHERE ch.return_date IS NULL ORDER BY ch.due_date,ch.id").fetchall()
 c.close()
 return render_template("checkout.html",items=items,form_data=form_data,active_checkouts=active_checkouts)
@app.route("/checkout/<int:checkout_id>/return", methods=["POST"])
def return_checkout(checkout_id):
 c=db()
 c.execute("BEGIN IMMEDIATE")
 checkout=c.execute("SELECT return_date FROM checkouts WHERE id=?",(checkout_id,)).fetchone()
 if checkout is None:
  c.rollback()
  c.close()
  flash("Checkout record not found.","danger")
  return redirect(url_for("checkout"))
 if checkout["return_date"] is not None:
  c.rollback()
  c.close()
  flash("This checkout has already been returned.","danger")
  return redirect(url_for("checkout"))
 updated=c.execute("UPDATE checkouts SET return_date=?,status='Returned' WHERE id=? AND return_date IS NULL",(date.today().isoformat(),checkout_id))
 if updated.rowcount != 1:
  c.rollback()
  c.close()
  flash("This checkout has already been returned.","danger")
  return redirect(url_for("checkout"))
 c.commit()
 c.close()
 flash("Equipment return recorded successfully.","success")
 return redirect(url_for("checkout"))
@app.route("/checkout/history")
def checkout_history():
 refresh_overdue_statuses()
 c=db()
 history=c.execute("SELECT ch.*,COALESCE(e.name,'Removed Equipment') AS equipment_name,e.asset_tag FROM checkouts ch LEFT JOIN equipment e ON e.id=ch.equipment_id ORDER BY ch.checkout_date DESC,ch.id DESC").fetchall()
 c.close()
 return render_template("checkout_history.html",history=history)
@app.route("/reports")
def reports(): return render_template("todo.html",title="Users & Reports",owner="Team Member 3",tasks=["User management","Overdue equipment","Reports/activity","Additional tests"])
if __name__=="__main__": init_db(); app.run(debug=True,host="0.0.0.0",port=5000)
