import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import chi2_contingency

# -------------------------------------------------------
# 1) Statista-Daten einlesen und normalisieren
# -------------------------------------------------------
df2023 = pd.read_excel("Online Zahlungsarten 2023.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")
df2021 = pd.read_excel("Online Zahlungsarten 2021.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")
df2019 = pd.read_excel("Online Zahlungsarten 2019.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")

# Normalisierungstabellen
norm23 = {
    "E-Wallet (Paypal, Alipay)": "E-Wallet",
    "Per Rechnung (und Zahlschein)": "Rechnung",
    "Klarna": "BNPL (Klarna)",
    "Kreditkarte einer inländischen Bank / Debitkarte": "Kreditkarte",
    "Visa / Mastercard": "Kreditkarte",
    "Banküberweisung": "Überweisung/Online-Transfer",
    "Direct debit": "Lastschrift/SEPA",
    "Sofort": "Überweisung/Online-Transfer",
    "Mobile Bezahl-App": "Mobile Wallet",
    "Virtuelle Währungen (Bitcoin)": "Krypto"
}
norm21 = {
    "E-Wallets": "E-Wallet",
    "Auf Rechnung": "Rechnung",
    "Bezahlung mit Kreditkarte": "Kreditkarte",
    "SEPA-Direktmandat": "Lastschrift/SEPA",
    "Online-Transfer": "Überweisung/Online-Transfer",
    "Mobile Geldbörsen": "Mobile Wallet",
    "Lieferung per Nachnahme": "Nachnahme",
}
norm19 = {
    "Über einen Bezahldienstleister (z.B. Paypal)": "E-Wallet",
    "Rechnung": "Rechnung",
    "Kreditkarte": "Kreditkarte",
    "Per Überweisung": "Überweisung/Online-Transfer",
    "Per Lastschrift": "Lastschrift/SEPA",
    "Sofortüberweisung": "Überweisung/Online-Transfer",
    "Vorkasse": "Nachnahme"
}

def normalize(df, mapping):
    df = df.copy()
    df["Methode"] = df["Methode"].astype(str).str.strip()
    df["Kategorie"] = df["Methode"].map(mapping).fillna(df["Methode"])
    df["Prozent"] = pd.to_numeric(df["Prozent"], errors="coerce")
    return df.groupby("Kategorie", as_index=False)["Prozent"].sum()

n23 = normalize(df2023, norm23).rename(columns={"Prozent": "pct_2023"})
n21 = normalize(df2021, norm21).rename(columns={"Prozent": "pct_2021"})
n19 = normalize(df2019, norm19).rename(columns={"Prozent": "pct_2019"})

statista_merged = n23.merge(n21, on="Kategorie", how="outer").merge(n19, on="Kategorie", how="outer")
statista_2023 = statista_merged[["Kategorie", "pct_2023"]].set_index("Kategorie")

# -------------------------------------------------------
# 2) Eigene Umfrage einlesen und normalisieren
# -------------------------------------------------------
df_umfrage = pd.read_excel("umfrage.xlsx", usecols="AP:AQ", names=["Zahlungsarten", "BNPL"])

def clean_text(s):
    if pd.isna(s):
        return ""
    return str(s).replace("\xa0", " ").replace("„", "").replace("“", "").strip()

def normalize_method(token):
    t = clean_text(token)
    t = re.sub(r"buy\s*now\s*pay\s*later.*", "BNPL (Klarna)", t, flags=re.I)
    t = re.sub(r"krypto.*", "Krypto", t, flags=re.I)
    mapping = {
        "paypal": "E-Wallet",
        "kreditkarte": "Kreditkarte",
        "rechnung": "Rechnung",
        "lastschrift": "Lastschrift/SEPA",
        "sofortüberweisung": "Überweisung/Online-Transfer",
        "apple pay": "Mobile Wallet",
        "bnpl (klarna)": "BNPL (Klarna)",
    }
    return mapping.get(t.lower(), t)

methods = (
    df_umfrage["Zahlungsarten"]
    .astype(str).map(clean_text)
    .str.split(";", expand=False)
    .explode()
    .dropna()
    .map(normalize_method)
    .str.strip()
)
methods = methods[methods != ""]

umfrage_counts = methods.value_counts().rename_axis("Kategorie").reset_index(name="Anzahl")
umfrage_counts["pct_umfrage"] = (umfrage_counts["Anzahl"] / len(df_umfrage) * 100).round(1)
umfrage = umfrage_counts.set_index("Kategorie")

# -------------------------------------------------------
# 3) Vergleich Statista vs. Umfrage (lesbarer Plot)
# -------------------------------------------------------
vergleich = umfrage.join(statista_2023, how="outer").fillna(0)

# Kürzere Namen und Fokus-Kategorien für gute Lesbarkeit
rename_short = {
    "Überweisung/Online-Transfer": "Überweisung",
    "Lastschrift/SEPA": "Lastschrift",
    "Mobile Wallet": "Mobile Wallet",
    "BNPL (Klarna)": "BNPL (Klarna)",
    "E-Wallet": "E-Wallet (PayPal)",
    "Andere Karten (American Express)": "Andere Karten",
    "Voucher ePay / Geschenkkarte eines Geschäfts / einer Marke": "Gutscheinkarten",
}
vergleich.index = vergleich.index.map(lambda s: rename_short.get(s, s))

focus = [
    "E-Wallet (PayPal)",
    "Kreditkarte",
    "Rechnung",
    "Lastschrift",
    "Überweisung",
    "Mobile Wallet",
    "BNPL (Klarna)"
]
plotdf = vergleich.reindex(focus).fillna(0)

# Horizontaler Vergleichsplot
fig, ax = plt.subplots(figsize=(10, 6))
plotdf[["pct_umfrage", "pct_2023"]].plot(kind="barh", ax=ax)
ax.set_xlabel("in %"); ax.set_ylabel("")
ax.set_title("Vergleich Zahlungsarten: Eigene Umfrage vs. Statista 2023")
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
for bars in ax.containers:
    ax.bar_label(bars, fmt="%.1f", label_type="edge", padding=2)
fig.tight_layout()
fig.savefig("Bilder/Vergleich_Umfrage_vs_Statista.png", dpi=300)
plt.show()

print(plotdf[["pct_umfrage", "pct_2023"]])

# -------------------------------------------------------
# 4) Chi²-Test korrekt mit ZÄHLWERTEN (robust)
# -------------------------------------------------------
# Statista-Prozente auf deine Stichprobengröße N skalieren
N = len(df_umfrage)
stat_counts = np.rint(plotdf["pct_2023"].to_numpy() / 100 * N)
umf_counts  = np.rint(plotdf["pct_umfrage"].to_numpy() / 100 * N)

cont = np.vstack([umf_counts, stat_counts]).astype(float)

# Spalten entfernen, die in beiden Gruppen 0 sind (sonst erwartete Frequenz=0)
keep = ~(np.logical_and(cont[0] == 0, cont[1] == 0))
cont = cont[:, keep]

# Wenn irgendwo 0 vorkommt, kleine Korrektur addieren (Haldane–Anscombe)
if (cont == 0).any():
    cont += 0.5

chi2, p, dof, expected = chi2_contingency(cont)
print(f"Chi²={chi2:.2f}, df={dof}, p={p:.4f}")
if p < 0.05:
    print("→ Verteilungen unterscheiden sich signifikant (5%-Niveau).")
else:
    print("→ Kein signifikanter Unterschied (5%-Niveau).")
