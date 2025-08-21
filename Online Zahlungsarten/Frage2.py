import pandas as pd
import matplotlib.pyplot as plt

# 1) Einlesen (deins – ggf. Pfade anpassen)
df2023 = pd.read_excel("Online Zahlungsarten 2023.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")
df2021 = pd.read_excel("Online Zahlungsarten 2021.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")
df2019 = pd.read_excel("Online Zahlungsarten 2019.xlsx", skiprows=4, sheet_name=1,
                       names=["Methode", "Prozent"], usecols="B:C")
zahlungsArtenEinzelhandel = pd.read_excel("Anteile von Zahlungsarten.xlsx", skiprows=4, sheet_name=1,
                        names=["Jahr", "Bar", "Girocard", "Kreditkarte", "Lastschrift","Sonstige","Rechnung","Maestro/V-Pay","Handelskarte"], usecols="B:J")
print(zahlungsArtenEinzelhandel)

# 2) Auf eine gemeinsame Kategorie-Norm bringen
#    -> Wörterbuch je Jahr: "Original" -> "Kanonsiche Kategorie"
norm23 = {
    "E-Wallet (Paypal, Alipay)": "E-Wallet",
    "Per Rechnung (und Zahlschein)": "Rechnung",
    "Klarna": "Rechnung (BNPL/Klarna)",            # optional: als eigene Kategorie
    "Kreditkarte einer inländischen Bank / Debitkarte": "Kreditkarte",
    "Visa / Mastercard": "Kreditkarte",
    "Banküberweisung": "Überweisung/Online-Transfer",
    "Direct debit": "Lastschrift/SEPA",
    "Voucher ePay / Geschenkkarte eines Geschäfts / einer Marke": "Gutschein/Geschenkkarte",
    "Bezahlung im Geschäft": "Bezahlung im Geschäft",
    "Giropay": "Giropay",
    "Sofort": "Sofortüberweisung",
    "Kauf auf Kredit": "Kauf auf Kredit",
    "Andere Karten (American Express)": "Andere Karte",
    "Mobile Bezahl-App": "Mobile Wallet",
    "Cash-on-Delivery (COD)": "Nachnahme",
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
    "Andere": "Andere"
}

norm19 = {
    "Über einen Bezahldienstleister (z.B. Paypal)": "E-Wallet",
    "Rechnung": "Rechnung",
    "Kreditkarte": "Kreditkarte",
    "Per Überweisung": "Überweisung/Online-Transfer",
    "Per Lastschrift": "Lastschrift/SEPA",
    "Sofortüberweisung": "Sofortüberweisung",
    "Vorkasse": "Vorkasse"
}

def normalize(df, mapping):
    # saubere Strings
    df = df.copy()
    df["Methode"] = df["Methode"].astype(str).str.strip()
    # mappen, Unbekannte bleiben wie sie sind
    df["Kategorie"] = df["Methode"].map(mapping).fillna(df["Methode"])
    # Prozent sicher numerisch
    df["Prozent"] = pd.to_numeric(df["Prozent"], errors="coerce")
    # falls eine Kategorie mehrfach gemappt wurde: zusammenfassen
    return df.groupby("Kategorie", as_index=False)["Prozent"].sum()

n23 = normalize(df2023, norm23).rename(columns={"Prozent": "pct_2023"})
n21 = normalize(df2021, norm21).rename(columns={"Prozent": "pct_2021"})
n19 = normalize(df2019, norm19).rename(columns={"Prozent": "pct_2019"})

# 3) Outer-Join über alle Kategorien (damit nichts verloren geht)
merged = n23.merge(n21, on="Kategorie", how="outer").merge(n19, on="Kategorie", how="outer")

# 4) Differenzen berechnen (wo Werte fehlen -> NaN)
merged["Δ23_vs_21"] = merged["pct_2023"] - merged["pct_2021"]
merged["Δ23_vs_19"] = merged["pct_2023"] - merged["pct_2019"]

# 5) Beispiel: nach größtem Anstieg/Abfall sortieren
print(merged.sort_values(by="Δ23_vs_21", ascending=False))

# Optional: nur gemeinsame Kategorien aller Jahre
common = merged.dropna(subset=["pct_2023", "pct_2021", "pct_2019"])
print("\nGemeinsame Kategorien:\n", common.sort_values("pct_2023", ascending=False))

# 6) Plotten
plotdf = merged.sort_values("pct_2023", ascending=False).fillna(0)
ax = plotdf.plot(x="Kategorie", y=["pct_2019", "pct_2021", "pct_2023"], kind="bar")
ax.set_ylabel("in %")
ax.set_title("Bevorzugte Online-Zahlungsarten – Vergleich 2019/2021/2023")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("Bilder\Vergleich Online-Zahlungsarten 2019-2023.png", dpi=300)
plt.show()

ax = zahlungsArtenEinzelhandel.plot(
    x="Jahr",
    y=["Bar", "Girocard", "Kreditkarte", "Lastschrift"],
    kind="line",
    marker="o"
)
ax.set_ylabel("Anteil am Umsatz in %")
ax.set_title("Zahlungsarten im stationären Handel 2016–2024")
plt.tight_layout()
plt.savefig("Bilder/Zahlungsarten_Einzelhandel.png", dpi=300)
plt.show()
