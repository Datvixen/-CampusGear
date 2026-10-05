from pathlib import Path
import tempfile
import app as cg
def test_dashboard():
 with tempfile.TemporaryDirectory() as d:
  cg.DB=Path(d)/"test.db"; cg.init_db(); cg.app.config["TESTING"]=True
  client=cg.app.test_client(); assert client.get("/").status_code==200
