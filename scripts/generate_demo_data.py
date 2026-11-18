"""Generate deterministic, fictional ticket rows for local interface demos only."""
import csv, random
from datetime import datetime, timedelta, timezone
from pathlib import Path
OUT=Path(__file__).parents[1]/"backend"/"data"/"demo_tickets.csv"
FIELDS=["passenger_count","amount","vehicle_number","ticket_type_id","end_stop_name","route","start_stop_name","created_at","is_ac"]
ROUTES=["SAMPLE-A","SAMPLE-B","SAMPLE-C","SAMPLE-D"]
STOPS=["Kashmere Gate ISBT","Central interchange","Lajpat Nagar","Nehru Place","Market junction","Connaught Place"]
def main():
    random.seed(20261118); OUT.parent.mkdir(parents=True,exist_ok=True); rows=[]
    for day in range(1,32):
        for route_i,route in enumerate(ROUTES):
            for _ in range(random.randint(8,18)):
                peak=random.random()<.62; hour=random.choice([7,8,9,17,18,19]) if peak else random.choice([10,11,12,13,14,15,20,21]); minute=random.randrange(60)
                start=STOPS[(route_i+random.randrange(4))%len(STOPS)]; end=STOPS[(STOPS.index(start)+random.randrange(1,len(STOPS)))%len(STOPS)]
                dt=datetime(2026,10,day,hour,minute,random.randrange(60),tzinfo=timezone(timedelta(hours=5,minutes=30)))
                rows.append({"passenger_count":random.choices([1,2,3,4],weights=[62,25,10,3])[0],"amount":random.choice([10,15,20,22,25,30,35]),"vehicle_number":f"DEMO-{route_i+1}-{random.randrange(10,99)}" if random.random()<.49 else "","ticket_type_id":random.choice([1,1,1,2]),"end_stop_name":end,"route":route,"start_stop_name":start,"created_at":dt.isoformat(timespec="microseconds"),"is_ac":random.choice(["True","False"])})
    with OUT.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    print(f"wrote {len(rows)} synthetic illustrative ticket rows to {OUT}")
if __name__=="__main__": main()
