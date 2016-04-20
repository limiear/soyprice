# -*- coding: utf-8 -*-
from variables.core import app, db, get_var, requests, beautifulsoup, Change
from datetime import datetime, timedelta


# dt = datetime.now() + timedelta(minutes=1)
# @app.run_every("day", dt.strftime("%H:%M"))
@app.run_every("day", "20:30")
def update_bcra_reserves():
    url = "http://www.bcra.gov.ar/Estadisticas/estprv010001.asp"
    bcra_vars = {
        u"reserve": {
            u"name": u"reserve/bcra",
            u"description": u"Reservas en dolares del Banco Central de la República Argentina",
            u"reference": u"USD"
        }
    }
    variables = {k: get_var(**v) for k, v in bcra_vars.items()}
    variable = variables["reserve"]
    first_date = datetime(1996, 03, 02)
    data = {
        'desde': first_date.strftime("%d/%m/%Y"),
        'hasta': datetime.now().strftime("%d/%m/%Y"),
        'descri': 1,
        'I1.x': 40,
        'I1.y': 7,
        'I1': 'Enviar',
        'fecha': 'Fecha_Serie',
        'campo': 'Res_Int_BCRA'
    }
    page = beautifulsoup(requests.post(url, data=data).text)
    rows = page.select("#texto_columna_2 tr")
    data = map(lambda r: map(lambda c: c.text, r.select('td')), rows)
    data = data[1:]
    reserves = map(lambda d:
                   (datetime.strptime(d[0], "%d/%m/%Y").date(),
                    float(d[1]) * 1000000),
                   data)
    last_reg = variable.changes.order_by(Change.moment.desc()).first()
    last_dt = last_reg.moment if last_reg else first_date.date()
    reserves = filter(lambda r: r[0] > last_dt, reserves)
    for d, v in reserves:
        ch = Change(value=v, moment=d)
        variable.changes.append(ch)
        db.session.add(ch)
    db.session.add(variable)
    db.session.commit()
