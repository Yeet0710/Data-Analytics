import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from scipy.stats import binomtest

# -------------------------------------------------------
# 1) Statista-Zusammenfassung aus CSV (bereits bereinigt)
# -------------------------------------------------------
df = pd.read_csv("warenkorb_auswertung.csv")
df["Jahr"] = pd.to_numeric(df["Jahr"], errors="coerce")

# Auf die letzten 5 Jahre beschränken
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

Path("Bilder").mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(df5["Jahr"], to_index(df5["LM_Umsatz_nom"]), marker="o", label="nominal")
ax.plot(df5["Jahr"], to_index(df5["LM_Umsatz_real"]), marker="o",
        label="real (inflationsbereinigt)")
ax.set_title("Lebensmitteleinzelhandel – Index (Startjahr = 100), letzte 5 Jahre")
ax.set_xlabel("Jahr"); ax.set_ylabel("Index (Start = 100)")
ax.legend()
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig.tight_layout()
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

# ---------- Plots schön formatiert ----------
# Plot 1: Veränderung Warenkorbwert (vertikal, feste Reihenfolge)
ver_sorted = ver.set_index("Antwort").reindex(order_veraenderung).reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 6))
bars = ax1.bar(ver_sorted["Antwort"], ver_sorted["Anzahl"])
ax1.set_title("Umfrage: Veränderung des Warenkorbwerts (letzte 5 Jahre)")
ax1.set_ylabel("Anzahl Personen")
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
plt.xticks(rotation=25, ha="right")
for rect, cnt, pct in zip(bars, ver_sorted["Anzahl"], ver_sorted["Anteil_%"]):
    ax1.text(rect.get_x()+rect.get_width()/2, rect.get_height()+0.2,
             f"{int(cnt)} ({pct}%)", ha="center", va="bottom")
fig1.tight_layout()
fig1.savefig("Bilder/umfrage_warenkorb_verteilung.png", dpi=300)

# Plot 2: Aspekte (horizontal, mit Labels am Balkenende)
asp_sorted = asp.sort_values("Anzahl")

fig2, ax2 = plt.subplots(figsize=(11, 6))
bars = ax2.barh(asp_sorted["Aspekt"], asp_sorted["Anzahl"])
ax2.set_title("Umfrage: Wofür sind Teilnehmende eher bereit, mehr zu zahlen?")
ax2.set_xlabel("Anzahl Personen")
ax2.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
for rect, cnt, pct in zip(bars, asp_sorted["Anzahl"], asp_sorted["Anteil_%"]):
    ax2.text(rect.get_width()+0.2, rect.get_y()+rect.get_height()/2,
             f"{int(cnt)} ({pct}%)", va="center")
fig2.tight_layout()
fig2.savefig("Bilder/umfrage_warenkorb_aspekte.png", dpi=300)

plt.show()

# -------------------------------------------------------
# 3) „Deskriptiv → Analytisch“: Gegenüberstellung + Tests
# -------------------------------------------------------
# Anteil derer, die einen ANSTIEG empfinden:
k_gestiegen = int(ver.loc[
    ver["Antwort"].isin(["Deutlich gestiegen", "Etwas gestiegen"]), "Anzahl"
].sum())
n = len(umf)
p_empf_anstieg = k_gestiegen / n * 100

# Reale Entwicklung Lebensmittelhandel (letzte 5 Jahre, %)
p_real_5j = growth_pct(df5["LM_Umsatz_real"])

print("\n--- Vergleich (Wahrnehmung vs. reale Entwicklung) ---")
print(f"Wahrnehmung: {p_empf_anstieg:.1f}% geben an, dass der Warenkorb gestiegen ist.")
print(f"Reale Entwicklung (Lebensmittelhandel, real): {p_real_5j:.1f}% in 5 Jahren.")
print("Interpretation: Beide Signale deuten auf einen Anstieg; "
      "der reale Zuwachs ist jedoch deutlich kleiner als der nominale, "
      "und die Umfrage spiegelt eher die gefühlte Preis-/Warenkorbdynamik wider.")

# Binomialtest H0: p = 0.5 (keine Mehrheit)
res50 = binomtest(k=k_gestiegen, n=n, p=0.5, alternative="greater")
print(f"\nBinomialtest H0: p=0.5 (Mehrheit für 'gestiegen'?)  "
      f"k={k_gestiegen}, n={n}, p-Wert={res50.pvalue:.4f}")
if res50.pvalue < 0.05:
    print("→ Signifikant: Mehr als die Hälfte der Befragten nimmt einen Anstieg wahr.")
else:
    print("→ Nicht signifikant: Mehrheit statistisch nicht belegt.")

# Optional: strengere/lockerere Referenz, z. B. p0=0.33
res33 = binomtest(k=k_gestiegen, n=n, p=1/3, alternative="greater")
print(f"Binomialtest H0: p=0.33  p-Wert={res33.pvalue:.4f}")

# -------------------------------------------------------
# 4) CSV-Exports
# -------------------------------------------------------
out = Path("Ergebnisse"); out.mkdir(exist_ok=True)
summary.to_csv(out / "statista_warenkorb_5J_summary.csv", index=False)
ver.to_csv(out / "umfrage_warenkorb_verteilung.csv", index=False)
asp.to_csv(out / "umfrage_warenkorb_aspekte.csv", index=False)
print(f"\nCSV gespeichert in: {out.resolve()}")
print("Bilder in:", Path('Bilder').resolve())
