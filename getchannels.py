#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, re
from bs4 import BeautifulSoup

def parse_transponder_info(frq_table):
    head_tr = frq_table.find("tr", attrs={"data-frequency-id": True})
    if not head_tr:
        return None
    tds_text = [td.get_text(" ", strip=True) for td in head_tr.find_all("td")]
    # Frequency
    freq = None
    for txt in tds_text:
        if re.match(r"^\d{4,5}(\.\d+)?$", txt):
            freq = txt.split(".", 1)[0]
            break
    # Polarity
    pol = None
    for td in head_tr.find_all("td"):
        t = td.get_text(" ", strip=True)
        if t in ("H","V"):
            pol = t.lower()
            break
    # System
    msys = 'dvbs2' if 'DVB-S2' in tds_text else ('dvbs' if 'DVB-S' in tds_text else None)
    # Modulation
    mtype = next((mod.lower() for mod in 
                  ['QPSK','8PSK','16APSK','32APSK','8APSK','16QAM','QAM']
                  if mod in tds_text), None)
    # Symbolrate
    sr = None
    for txt in tds_text:
        m = re.search(r'(\d{4,5})\s*\d/\d', txt)
        if m:
            sr = m.group(1)
            break
    if not all([freq, pol, msys, sr]):
        return None
    return {'freq': freq, 'pol': pol, 'msys': msys, 'mtype': mtype, 'sr': sr}

def extract_channel_info(row):
    tds = row.find_all("td")
    name_td = row.find("td", class_="ch") or (tds[2] if len(tds) >= 3 else None)
    name = name_td.get_text(" ", strip=True) if name_td else None
    is_radio = row.find("img", {"src": "/radio.gif"}) is not None

    # SID
    sid = None
    sid_td = row.find('td', class_='s')
    if sid_td:
        m = re.search(r"\d{1,5}", sid_td.get_text(" ", strip=True))
        if m:
            sid = m.group(0)

    # VPID (nur für TV relevant)
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

    # APIDs
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

    # Alle weiteren PIDs aus den pid-Zellen
    all_pids = []
    for td in pid_cells:
        for n in re.findall(r"\d{2,5}", td.get_text(" ", strip=True)):
            if n != "8191" and n not in all_pids:
                all_pids.append(n)

    # Zusammenbau
    pid_list = []
    if not is_radio:
        if vpid:
            pid_list.append(vpid)
        for a in apids:
            if a not in pid_list:
                pid_list.append(a)
        for n in all_pids:
            if n not in pid_list:
                pid_list.append(n)
    else:
        # Radio: APIDs + alle anderen PIDs (inkl. PMT/PCR)
        for a in apids:
            if a not in pid_list:
                pid_list.append(a)
        for n in all_pids:
            if n not in pid_list:
                pid_list.append(n)

    return name, is_radio, pid_list, sid

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
    for fl in soup.find_all("table", class_="fl"):
        rows = fl.find_all("tr", attrs={"data-channel-id": True})
        if not rows:
            continue
        frq = fl.find_previous("table", class_="frq")
        tp = parse_transponder_info(frq) if frq else None
        if not tp:
            continue
        for row in rows:
            name, is_radio, pids, sid = extract_channel_info(row)
            if name and pids:
                entries.append((name, tp, is_radio, pids, sid))

    with open(outputFilename, "w", encoding="utf-8") as o:
        for name, tp, is_radio, pids, sid in entries:
            o.write(f"#EXTINF:0,{name}\n")
            url = f"rtsp://@{server}/?src={source}&freq={tp['freq']}&pol={tp['pol']}&msys={tp['msys']}"
            if tp['mtype']:
                url += f"&mtype={tp['mtype']}"
            url += f"&sr={tp['sr']}"
            if sid:
                url += f"&sid={sid}"
            url += "&pids=0," + ",".join(pids)
            o.write(url + "\n")

    print(f"{len(entries)} Einträge geschrieben -> {outputFilename}")

if __name__ == "__main__":
    main()
