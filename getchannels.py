#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robuster Parser für KingOfSat-ähnliche HTML-Listen.
Erzeugt eine M3U mit Sat>IP-RTSP-URLs aus einer gespeicherten HTML-Datei.

Aufruf:
    python getchannels_bs.py <server> <inputfile> <src>

Beispiel:
    python getchannels_bs.py newslave pos-19.2E 4
"""
import sys, os, re
from bs4 import BeautifulSoup

def parse_transponder_info(frq_table):
    head_tr = frq_table.find("tr", attrs={"data-frequency-id": True})
    if not head_tr:
        return None
    # Alle Zellen als Text
    tds_text = [td.get_text(" ", strip=True) for td in head_tr.find_all("td")]
    # Frequenz (z.B. "10727.20" -> "10727")
    freq = None
    for txt in tds_text:
        if re.match(r"^\d{4,5}(\.\d+)?$", txt):
            freq = txt.split(".", 1)[0]
            break
    # Polarisation
    pol = None
    for td in head_tr.find_all("td"):
        t = td.get_text(" ", strip=True)
        if t in ("H", "V"):
            pol = t.lower()
            break
    # Modulationssystem
    msys = 'dvbs2' if 'DVB-S2' in tds_text else ('dvbs' if 'DVB-S' in tds_text else None)
    # Modulationstyp (optional)
    mtype = None
    for mod in ['QPSK','8PSK','16APSK','32APSK','8APSK','16QAM','QAM']:
        if mod in tds_text:
            mtype = mod.lower()
            break
    # Symbolrate (aus z.B. "30000 3/4")
    sr = None
    for txt in tds_text:
        m = re.search(r"(\d{4,5})\s*\d\/\d", txt)
        if m:
            sr = m.group(1)
            break
    if not all([freq, pol, msys, sr]):
        return None
    return {'freq': freq, 'pol': pol, 'msys': msys, 'mtype': mtype, 'sr': sr}

def extract_channel_info(row):
    tds = row.find_all("td")
    # Kanalname (Spalte mit class 'ch' oder die 3. Zelle)
    name_td = row.find("td", class_="ch") or (tds[2] if len(tds) >= 3 else None)
    name = name_td.get_text(" ", strip=True) if name_td else None
    is_radio = row.find("img", {"src": "/radio.gif"}) is not None

    # VPID = erste 'td.pid' Zahl != 8191
    vpid = None
    pid_cells = [td for td in tds if 'pid' in (td.get('class') or [])]
    for td in pid_cells:
        nums = re.findall(r"\d{2,5}", td.get_text(" ", strip=True))
        for n in nums:
            if n != "8191":
                vpid = n
                break
        if vpid:
            break

    # APIDs: 'td.apid' + ggf. Spalte mit Sprachliste (td ohne class)
    apids = []
    for td in tds:
        classes = td.get('class') or []
        txt = td.get_text(" ", strip=True)
        if 'apid' in classes:
            for n in re.findall(r"\d{2,5}", txt):
                if n not in apids:
                    apids.append(n)
        if not classes:
            for n in re.findall(r"\d{2,5}", txt):
                if n not in apids:
                    apids.append(n)

    # Weitere PIDs (PCR/PMT etc.) = übrige 'td.pid' nach dem ersten
    other_pids = []
    started = False
    for td in pid_cells:
        nums = re.findall(r"\d{2,5}", td.get_text(" ", strip=True))
        for n in nums:
            if not started:
                started = True
                continue
            if n not in apids and n != "8191" and n not in other_pids:
                other_pids.append(n)
        if not started and nums:
            started = True

    # Reihenfolge wie im alten Skript: vpid (nur TV), dann apids, dann rest
    pid_list = []
    if vpid and not is_radio:
        pid_list.append(vpid)
    for a in apids:
        if a not in pid_list:
            pid_list.append(a)
    for op in other_pids:
        if op not in pid_list:
            pid_list.append(op)

    return name, is_radio, pid_list

def main():
    if len(sys.argv) != 4:
        print("Aufruf: python getchannels_bs.py <server> <inputfile> <src>")
        sys.exit(1)
    server, inputFilename, source = sys.argv[1], sys.argv[2], sys.argv[3]
    base, ext = os.path.splitext(inputFilename)
    if ext.lower() in ('.php', '.html', '.htm'):
        outputFilename = base + '.m3u'
    else:
        outputFilename = inputFilename + '.m3u'

    with open(inputFilename, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f, "html.parser")

    entries = []
    current_tp = None

    # Dokument der Reihe nach durchgehen: 'frq' (Transponderkopf) -> 'fl' (Kanäle)
    for elem in soup.find_all("table"):
        classes = elem.get("class", [])
        if 'frq' in classes:
            current_tp = parse_transponder_info(elem)
        elif 'fl' in classes and current_tp:
            for row in elem.find_all("tr", attrs={"data-channel-id": True}):
                name, is_radio, pid_list = extract_channel_info(row)
                if name and pid_list:
                    entries.append((name, current_tp, is_radio, pid_list))

    # Schreiben
    with open(outputFilename, "w", encoding="utf-8") as o:
        for name, tp, is_radio, pids in entries:
            o.write(f"#EXTINF:0,{name}\n")
            url = f"rtsp://@{server}/?src={source}&freq={tp['freq']}&pol={tp['pol']}&msys={tp['msys']}"
            if tp['mtype']:
                url += f"&mtype={tp['mtype']}"
            url += f"&sr={tp['sr']}&pids=0," + ",".join(pids)
            o.write(url + "\n")

    print(f"{len(entries)} Einträge geschrieben -> {outputFilename}")

if __name__ == "__main__":
    main()
