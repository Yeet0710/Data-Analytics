import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# -------------------------------------------------------
# 1) Einlesen
# -------------------------------------------------------
df = pd.read_excel(
    "umfrage.xlsx",
    sheet_name=0,
    usecols="AP:AQ",
    names=["Zahlungsarten", "BNPL_Aenderung"]
)
print(df.head())

# -------------------------------------------------------
# 2) Normalisierung
# -------------------------------------------------------
def clean_text(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).replace("\xa0", " ").replace("\u202f", " ")  # NBSP weg
    s = s.replace("„", "").replace("“", "").replace("‚", "").replace("’", "")
    return s.strip().strip(";")

df["Zahlungsarten"] = df["Zahlungsarten"].map(clean_text)
df["BNPL_Aenderung"] = df["BNPL_Aenderung"].map(clean_text)

# BNPL-Antworten vereinheitlichen
map_bnpl = {
    "Ich nutze BNPL häufiger als früher": "Häufiger",
    "Ich nutze BNPL etwa gleich häufig": "Gleich häufig",
    "Ich nutze BNPL seltener als früher": "Seltener",
    "Ich habe BNPL noch nie genutzt": "Nie genutzt",
}
df["BNPL_norm"] = df["BNPL_Aenderung"].map(lambda s: map_bnpl.get(s, s))

# Zahlungsarten-Kategorien vereinheitlichen
def normalize_method(token: str) -> str:
    t = clean_text(token)
    t = re.sub(r"buy\s*now\s*pay\s*later.*", "BNPL (Klarna)", t, flags=re.I)
    t = re.sub(r"krypto\w*", "Krypto", t, flags=re.I)
    mapping = {
        "paypal": "PayPal",
        "kreditkarte": "Kreditkarte",
        "rechnung": "Rechnung",
        "lastschrift": "Lastschrift",
        "sofortüberweisung": "Sofortüberweisung",
        "apple pay": "Apple Pay",
        "bnpl (klarna)": "BNPL (Klarna)",
    }
    key = t.lower()
    return mapping.get(key, t)

# -------------------------------------------------------
# 3) Mehrfachauswahl zerlegen & zählen
# -------------------------------------------------------
methods = (
    df["Zahlungsarten"]
      .str.split(";", expand=False)
      .explode()
      .dropna()
      .map(normalize_method)
      .str.strip()
)
methods = methods[methods != ""]  # echte Einträge

# Häufigkeiten (absolut) + Prozent am Gesamtsample (Basis: Teilnehmende)
total_respondents = len(df)
method_counts = methods.value_counts().rename_axis("Kategorie").reset_index(name="Anzahl")
method_counts["Anteil_%"] = (method_counts["Anzahl"] / total_respondents * 100).round(1)

bnpl_counts = df["BNPL_norm"].value_counts().rename_axis("Kategorie").reset_index(name="Anzahl")
bnpl_counts["Anteil_%"] = (bnpl_counts["Anzahl"] / total_respondents * 100).round(1)

# Kreuztabelle: Hat die Person BNPL als Zahlungsart gewählt?
has_bnpl = df["Zahlungsarten"].str.contains("Buy Now Pay Later", case=False, na=False)
kreuz = pd.crosstab(has_bnpl.map({True: "Mit BNPL gewählt", False: "Ohne BNPL"}), df["BNPL_norm"]).fillna(0).astype(int)

# -------------------------------------------------------
# 4) Plots (werden im Unterordner Bilder gespeichert)
# -------------------------------------------------------
outdir = Path("Bilder"); outdir.mkdir(exist_ok=True)

# A) Zahlungsarten – horizontale Balken (aussagekräftig bei langen Labels)
mc = method_counts.sort_values("Anzahl")
fig1, ax1 = plt.subplots()
ax1.barh(mc["Kategorie"], mc["Anzahl"])
for i, (v, p) in enumerate(zip(mc["Anzahl"], mc["Anteil_%"])):
    ax1.text(v, i, f" {v} ({p}%)", va="center")
ax1.set_title("Regelmäßig genutzte Online-Zahlungsarten (Mehrfachauswahl)")
ax1.set_xlabel("Anzahl Antworten")
ax1.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig1.tight_layout()
fig1.savefig(outdir / "umfrage_zahlungsarten_hbar.png", dpi=300)
plt.show()

# B) BNPL-Nutzungsänderung – Balkendiagramm
bc = bnpl_counts.sort_values("Anzahl", ascending=False)
fig2, ax2 = plt.subplots()
ax2.bar(bc["Kategorie"], bc["Anzahl"])
for x, v, p in zip(bc["Kategorie"], bc["Anzahl"], bc["Anteil_%"]):
    ax2.text(x, v, f"{v} ({p}%)", ha="center", va="bottom")
ax2.set_title("BNPL (z. B. Klarna) – Nutzungsänderung")
ax2.set_ylabel("Anzahl Personen")
ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.xticks(rotation=0)
fig2.tight_layout()
fig2.savefig(outdir / "umfrage_bnpl_aenderung_bar.png", dpi=300)
plt.show()

# C) 100%-gestapeltes Balkendiagramm: BNPL in Zahlungsarten vs. BNPL-Historie
kreuz_pct = (kreuz.T / kreuz.sum(axis=1)).T * 100
fig3, ax3 = plt.subplots()
bottom = None
for col in kreuz_pct.columns:
    vals = kreuz_pct[col].values
    ax3.bar(kreuz_pct.index, vals, bottom=bottom, label=col)
    bottom = vals if bottom is None else bottom + vals
ax3.set_title("BNPL-Auswahl (Zahlungsarten) vs. BNPL-Nutzungsänderung")
ax3.set_ylabel("Anteil in % (100% je Gruppe)")
ax3.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax3.legend(title="Antwort")
fig3.tight_layout()
fig3.savefig(outdir / "umfrage_bnpl_kreuztabelle_stacked.png", dpi=300)
plt.show()

# -------------------------------------------------------
# 5) Ergebnisse exportieren
# -------------------------------------------------------
method_counts.to_csv(outdir / "umfrage_zahlungsarten_counts.csv", index=False)
bnpl_counts.to_csv(outdir / "umfrage_bnpl_counts.csv", index=False)
kreuz.to_csv(outdir / "umfrage_bnpl_kreuztabelle.csv")
print("Fertig. Dateien gespeichert in:", outdir.resolve())
