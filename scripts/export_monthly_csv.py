#!/usr/bin/env python3
"""Exporta mediciones de agua desde MariaDB a CSV estáticos para GitHub Pages."""
from __future__ import annotations

import argparse, csv, json, os
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import mysql.connector

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_START = date(2025, 1, 1)
HEADER = ["fecha","ph","conductividad_us_cm","temperatura_agua_c","oxigeno_disuelto_mg_l","temperatura_sistema_c","voltaje_v","senal_csq"]
MODELS = {
    "ENV-20-pH": {1:"ph"}, "ENV-20-EC-K1.0": {2:"conductividad_us_cm"},
    "DS18B20": {3:"temperatura_agua_c"}, "ENV-40-DOX": {52:"oxigeno_disuelto_mg_l"},
    "DS3231": {3:"temperatura_sistema_c"}, "Divisor de Voltaje": {4:"voltaje_v"},
    "SIM7600G": {15:"senal_csq"},
    "CWT-BL-PH(T)-S": {1:"ph",3:"temperatura_agua_c"},
    "CWT-BL-EC-15K-S": {2:"conductividad_us_cm"},
}
PUBLIC_VARS = {
    "ph":{"label":"pH","unit":"pH"},
    "conductividad_us_cm":{"label":"Conductividad eléctrica","unit":"µS/cm"},
    "temperatura_agua_c":{"label":"Temperatura del agua","unit":"°C"},
    "oxigeno_disuelto_mg_l":{"label":"Oxígeno disuelto","unit":"mg/L","note":"Sensor en validación"},
    "temperatura_sistema_c":{"label":"Temperatura del sistema","unit":"°C","diagnostic":True},
    "voltaje_v":{"label":"Voltaje","unit":"V","diagnostic":True},
    "senal_csq":{"label":"Señal celular","unit":"CSQ","diagnostic":True},
}

def env(path: Path):
    if path.exists():
        for raw in path.read_text().splitlines():
            line=raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k,v=line.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip("\"'"))

def db(env_file):
    env(env_file)
    return mysql.connector.connect(host=os.environ["DB_HOST"],port=int(os.getenv("DB_PORT","3306")),user=os.environ["DB_USER"],password=os.environ["DB_PASSWORD"],database=os.environ["DB_NAME"],connection_timeout=15)

def months(first: date, last: date):
    y,m=first.year,first.month
    while (y,m) <= (last.year,last.month):
        yield f"{y:04d}-{m:02d}"
        y,m=(y+1,1) if m==12 else (y,m+1)

def bounds(month):
    start=datetime.strptime(month,"%Y-%m")
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    return start,end

def clean(model, field, value):
    value=float(value)
    if field=="ph" and not 0 < value < 14: return None
    if field=="conductividad_us_cm" and value <= 0: return None
    if model=="DS18B20" and not 0 < value <= 60: return None
    if field=="temperatura_agua_c" and not -5 < value <= 60: return None
    if field=="temperatura_sistema_c" and not -30 < value <= 85: return None
    if field=="voltaje_v" and not 0 < value < 30: return None
    if field=="senal_csq" and not 0 <= value <= 31: return None
    if field=="oxigeno_disuelto_mg_l" and not 0 <= value <= 30: return None
    return f"{value:.3f}".rstrip("0").rstrip(".")

def sources(conn, device_id):
    cur=conn.cursor(dictionary=True)
    cur.execute("""SELECT s.id_sensor,st.modelo FROM sensores_en_dispositivo sd JOIN sensores s ON s.id_sensor=sd.id_sensor JOIN sensores_tipo st ON st.id_sensor_tipo=s.id_sensor_tipo WHERE sd.id_dispositivo=%s ORDER BY s.id_sensor""",(device_id,))
    out=[r for r in cur.fetchall() if r["modelo"] in MODELS]; cur.close(); return out

def first_date(conn, src):
    found=[]
    for s in src:
        cur=conn.cursor(); cur.execute("SELECT fecha FROM datos FORCE INDEX (idx_datos_sensor_fecha) WHERE id_sensor=%s ORDER BY fecha LIMIT 1",(s["id_sensor"],)); row=cur.fetchone(); cur.close()
        if row: found.append(row[0])
    return max(min(found).date(), PUBLIC_START) if found else None

def export_month(conn, station, src, month, outdir):
    start,end=bounds(month); rows=defaultdict(dict)
    for s in src:
        mapping=MODELS[s["modelo"]]; ids=sorted(mapping); marks=",".join(["%s"]*len(ids))
        cur=conn.cursor(); cur.execute(f"SELECT fecha,id_variable,valor FROM datos FORCE INDEX (idx_datos_sensor_fecha) WHERE id_sensor=%s AND id_variable IN ({marks}) AND fecha >= %s AND fecha < %s ORDER BY fecha",(s["id_sensor"],*ids,start,end))
        for when,var_id,value in cur:
            value=clean(s["modelo"],mapping[var_id],value)
            if value is not None: rows[when][mapping[var_id]]=value
        cur.close()
    target=outdir/station["code"]/f"{month}-part-001.csv"; target.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        target.unlink(missing_ok=True)
        return rows,None
    tmp=target.with_suffix(".tmp")
    with tmp.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=HEADER); w.writeheader()
        for when,values in sorted(rows.items()): w.writerow({"fecha":when.isoformat(sep=" "),**values})
        f.flush(); os.fsync(f.fileno())
    tmp.replace(target)
    return rows,target

def main():
    p=argparse.ArgumentParser(); p.add_argument("--all",action="store_true"); p.add_argument("--env-file",type=Path,default=Path("/var/www/api_sensores/.env")); p.add_argument("--output",type=Path,default=ROOT/"data"); args=p.parse_args()
    stations=json.loads((ROOT/"config/stations.json").read_text()); conn=db(args.env_file); today=date.today(); manifest=[]; latest=[]
    try:
        for station in stations:
            src=sources(conn,station["device_id"]); first=first_date(conn,src)
            selected=list(months(first,today)) if args.all and first else [today.strftime("%Y-%m")]
            month_map={}; newest=None
            for month in selected:
                rows,path=export_month(conn,station,src,month,args.output)
                if path: month_map[month]=[path.relative_to(ROOT).as_posix()]
                for when,values in rows.items():
                    if newest is None or when>newest[0]: newest=(when,values)
            existing=sorted((args.output/station["code"]).glob("*-part-*.csv"))
            for path in existing: month_map.setdefault(path.name[:7],[]).append(path.relative_to(ROOT).as_posix())
            month_map={k:sorted(set(v)) for k,v in sorted(month_map.items())}
            variables=sorted({field for s in src for field in MODELS[s["modelo"]].values()})
            manifest.append({**station,"variables":variables,"months":month_map})
            if newest:
                for variable,value in newest[1].items(): latest.append({"codigo":station["code"],"fecha":newest[0].isoformat(sep=" "),"variable":variable,"valor":value})
    finally: conn.close()
    args.output.mkdir(exist_ok=True)
    with (args.output/"latest.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["codigo","fecha","variable","valor"]); w.writeheader(); w.writerows(latest)
    updated=max((r["fecha"] for r in latest),default="")
    (args.output/"manifest.json").write_text(json.dumps({"schema_version":1,"updated_at":updated,"timezone":"America/Santiago","stations":manifest,"variables":PUBLIC_VARS},ensure_ascii=False,indent=2)+"\n")
    print(f"Exportación lista: {len(stations)} estaciones; última medición {updated}")

if __name__=="__main__": main()
