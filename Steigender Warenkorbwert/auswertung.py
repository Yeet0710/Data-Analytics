import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# -------------------------------------------------------
# 1) Statista-Zusammenfassung aus CSV (bereits bereinigt)
# -------------------------------------------------------
df = pd.read_csv("warenkorb_auswertung.csv")
df["Jahr"] = pd.to_numeric(df["Jahr"], errors="coerce")

# Auf die letzten 5 Jahre der CSV beschränken
last_year = int(df["Jahr"].max())
window = list(range(last_year - 4, last_year + 1))
df5 = df[df["Jahr"].isin(window)].sort_values("Jahr").reset_index(drop=True)

def growth_pct(series):
    s0, sN = float(series.iloc[0]), float(series.iloc[-1])
    return (sN / s0 - 1) * 100

def cagr(series, years):
    s0, sN = float(series.iloc[0]), float(series.iloc[-1])
    n = int(years.iloc[-1] - years.iloc[0])
    return (sN / s0) ** (1 / n) - 1 if (s0 > 0 and n > 0) else np.nan

# Kennzahlen (letzte 5 Jahre)
metrics = []
for nom, real, label in [
    ("LM_Umsatz_nom", "LM_Umsatz_real", "Lebensmitteleinzelhandel"),
    ("Food_nom",      "Food_real",      "Konsumausgaben Food"),
    ("Bekl_nom",      "Bekl_real",      "Konsumausgaben Bekleidung"),
]:
    g_nom = growth_pct(df5[nom])
    g_real = growth_pct(df5[real])
    c_nom = cagr(df5[nom], df5["Jahr"]) * 100
    c_real = cagr(df5[real], df5["Jahr"]) * 100
    metrics.append([label, g_nom, g_real, c_nom, c_real])

summary = pd.DataFrame(
    metrics, columns=["Reihe", "Δ5J_nom_%", "Δ5J_real_%", "CAGR_nom_%", "CAGR_real_%"]
)
print("\n--- Statista-Zusammenfassung (letzte 5 Jahre) ---")
print(summary.round(1))

# Index-Plot (Startjahr = 100) für nominal vs. real (Lebensmittelhandel)
def to_index(series):
    base = float(series.iloc[0])
    return series / base * 100.0

fig, ax = plt.subplots()
ax.plot(df5["Jahr"], to_index(df5["LM_Umsatz_nom"]), marker="o", label="nominal")
ax.plot(df5["Jahr"], to_index(df5["LM_Umsatz_real"]), marker="o",
        label="real (inflationsbereinigt)")
ax.set_title("Lebensmitteleinzelhandel – Index (Startjahr = 100), letzte 5 Jahre")
ax.set_xlabel("Jahr"); ax.set_ylabel("Index (Start = 100)")
ax.legend()
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig.tight_layout()
Path("Bilder").mkdir(exist_ok=True)
fig.savefig("Bilder/warenkorb_index_lm_5J.png", dpi=300)

# -------------------------------------------------------
# 2) Umfrage einlesen (AN: Veränderung, AO: Zahlungsbereitschaft-Aspekte)
# -------------------------------------------------------
umf = pd.read_excel("umfrage.xlsx", usecols="AN:AO",
                    names=["Veränderung_Warenkorb", "Aspekte"])

# Verteilung der Antworten („deutlich/etwas gestiegen …“)
order_veraenderung = [
    "Deutlich gestiegen", "Etwas gestiegen",
    "Gleich geblieben", "Etwas gesunken", "Deutlich gesunken"
]
ver = (umf["Veränderung_Warenkorb"]
       .value_counts()
       .reindex(order_veraenderung)
       .fillna(0)
       .rename_axis("Antwort")
       .reset_index(name="Anzahl"))
ver["Anteil_%"] = (ver["Anzahl"] / len(umf) * 100).round(1)

# Aspekte (Mehrfachauswahl, Semikolon-separiert)
aspekte = (umf["Aspekte"].fillna("")
           .str.split(";", expand=False)
           .explode().str.strip())
aspekte = aspekte[aspekte.ne("")]

# Einheitliche Reihenfolge für klare Story (an eure Grafik angelehnt)
order_aspekte = [
    "Höhere Produktqualität / Markenprodukte",
    "Verbesserter Kundenservice / Rückgabeservice",
    "Lokale / europäische Anbieter statt Billiganbieter",
    "Nachhaltige oder umweltfreundliche Produkte",
    "Schnellerer Versand / Expresslieferung",
    "Keine erhöhte Zahlungsbereitschaft",
    "Sonstiges"
]
asp = (aspekte.value_counts()
       .reindex(order_aspekte)
       .fillna(0)
       .rename_axis("Aspekt")
       .reset_index(name="Anzahl"))
asp["Anteil_%"] = (asp["Anzahl"] / len(umf) * 100).round(1)

print("\n--- Umfrage: Veränderung des Warenkorbwerts ---")
print(ver.fillna(0))
print("\n--- Umfrage: Wofür zahlt man eher mehr? ---")
print(asp.fillna(0))

# Plot 1: Veränderung Warenkorbwert
fig1, ax1 = plt.subplots()
ax1.bar(ver["Antwort"], ver["Anzahl"])
for i, r in ver.iterrows():
    ax1.text(i, r["Anzahl"] + 0.2, f'{int(r["Anzahl"])} ({r["Anteil_%"]}%)',
             ha="center", va="bottom")
ax1.set_title("Umfrage: Veränderung des durchschnittlichen Warenkorbwerts (5 Jahre)")
ax1.set_ylabel("Anzahl Personen")
plt.xticks(rotation=20, ha="right")
fig1.tight_layout()
fig1.savefig("Bilder/umfrage_warenkorb_verteilung.png", dpi=300)

# Plot 2: Aspekte – horizontale Balken
asp_sorted = asp.sort_values("Anzahl")
fig2, ax2 = plt.subplots()
ax2.barh(asp_sorted["Aspekt"], asp_sorted["Anzahl"])
for i, (v, p) in enumerate(zip(asp_sorted["Anzahl"], asp_sorted["Anteil_%"])):
    ax2.text(v, i, f" {int(v)} ({p}%)", va="center")
ax2.set_title("Umfrage: Wofür sind Teilnehmende eher bereit, mehr zu zahlen?")
ax2.set_xlabel("Anzahl Personen")
ax2.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig2.tight_layout()
fig2.savefig("Bilder/umfrage_warenkorb_aspekte.png", dpi=300)

plt.show()

# -------------------------------------------------------
# 3) „Deskriptiv → Analytisch“: einfache Gegenüberstellung
# -------------------------------------------------------
# Anteil derer, die einen ANSTIEG empfinden:
p_empf_anstieg = ver.loc[
    ver["Antwort"].isin(["Deutlich gestiegen", "Etwas gestiegen"]), "Anzahl"
].sum() / len(umf) * 100

# Reale Entwicklung Lebensmittelhandel (letzte 5 Jahre, %)
p_real_5j = growth_pct(df5["LM_Umsatz_real"])

print("\n--- Vergleich (Wahrnehmung vs. reale Entwicklung) ---")
print(f"Wahrnehmung: {p_empf_anstieg:.1f}% geben an, dass der Warenkorb gestiegen ist.")
print(f"Reale Entwicklung (Lebensmittelhandel, real): {p_real_5j:.1f}% in 5 Jahren.")
print("Interpretation: Beide Signale deuten auf einen Anstieg; "
      "der reale Zuwachs ist jedoch deutlich kleiner als der nominale, "
      "und die Umfrage spiegelt eher die gefühlte Preis-/Warenkorbdynamik wider.")

# Optional: CSV-Exports (falls du sie dokumentieren willst)
out = Path("Ergebnisse"); out.mkdir(exist_ok=True)
summary.to_csv(out / "statista_warenkorb_5J_summary.csv", index=False)
ver.to_csv(out / "umfrage_warenkorb_verteilung.csv", index=False)
asp.to_csv(out / "umfrage_warenkorb_aspekte.csv", index=False)
print(f"\nCSV gespeichert in: {out.resolve()}")
print("Bilder in:", Path('Bilder').resolve())
