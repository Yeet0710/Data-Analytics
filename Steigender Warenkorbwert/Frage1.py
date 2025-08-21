import pandas as pd
import matplotlib.pyplot as plt

# ---------- 1) Daten laden ----------

inflation = pd.read_excel(
    "Inflationsrate.xlsx", sheet_name=1, skiprows=4, usecols="B:C", names=["Jahr", "Inflation"]
)

lm = pd.read_excel(
    "Umsatz Lebensmitteleinzelhandel.xlsx", sheet_name=1, skiprows=4, usecols="B:C",
    names=["Jahr", "LM_Umsatz_nom"]
)

einzel_vj = pd.read_excel(
    "Umsatzentwicklung im Einzelhandel.xlsx", sheet_name=1, skiprows=4, usecols="B:C",
    names=["Jahr", "EH_Veraenderung_%"]
)

bekl = pd.read_excel(
    "Konsumausgaben Bekleidung und Schuhe.xlsx", sheet_name=1, skiprows=4, usecols="B:C",
    names=["Jahr", "Bekl_nom"]
)

food = pd.read_excel(
    "Konsumausgaben Nahrungsmittel, Getränke Tabakwaren Drogen.xlsx",
    sheet_name=1, skiprows=4, usecols="B:C",
    names=["Jahr", "Food_nom"]
)

# ---------- 2) Reinigung ----------

# a) Inflations-Jahre "'01" -> 2001
def fix_year(x):
    s = str(x).strip()
    if s.startswith("'") and len(s) == 3:  # z.B. '01
        return 2000 + int(s[1:])
    # falls schon richtige Jahreszahl:
    try:
        return int(s)
    except ValueError:
        return pd.NA

inflation["Jahr"] = inflation["Jahr"].apply(fix_year).astype("Int64")
inflation["Inflation"] = pd.to_numeric(inflation["Inflation"], errors="coerce")

# andere Tabellen: sicherstellen, dass Jahr int ist
for df in (lm, einzel_vj, bekl, food):
    df["Jahr"] = pd.to_numeric(df["Jahr"], errors="coerce").astype("Int64")
    for col in df.columns:
        if col != "Jahr":
            df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------- 3) Preisindex aus Inflationsraten bauen ----------
# Startindex = 100 im ersten gemeinsamen Jahr
first_year = max(lm["Jahr"].min(), bekl["Jahr"].min(), food["Jahr"].min(), inflation["Jahr"].min())
infl = inflation[inflation["Jahr"] >= first_year].sort_values("Jahr").reset_index(drop=True)

# CPI: cumprod(1 + infl/100) * 100
infl["CPI"] = (1 + infl["Inflation"] / 100.0).cumprod() * 100.0
base_cpi = infl["CPI"].iloc[0]
infl["CPI"] = infl["CPI"] / base_cpi * 100.0  # Basisjahr = 100

# ---------- 4) Mergen & reale Werte rechnen ----------
df = infl[["Jahr", "CPI"]].merge(lm, on="Jahr", how="inner")
df = df.merge(bekl, on="Jahr", how="inner")
df = df.merge(food, on="Jahr", how="inner")

# reale Werte = nominal * (100 / CPI)
df["LM_Umsatz_real"] = df["LM_Umsatz_nom"] * (100.0 / df["CPI"])
df["Bekl_real"]      = df["Bekl_nom"]      * (100.0 / df["CPI"])
df["Food_real"]      = df["Food_nom"]      * (100.0 / df["CPI"])

print(df.head())

# ---------- 5) Kurz-Auswertung (CAGR) ----------
def cagr(series, years):
    s0, sN = float(series.iloc[0]), float(series.iloc[-1])
    n = int(years.iloc[-1] - years.iloc[0])
    if s0 <= 0 or n <= 0:
        return float("nan")
    return (sN / s0) ** (1 / n) - 1

for label_nom, label_real in [
    ("LM_Umsatz_nom", "LM_Umsatz_real"),
    ("Bekl_nom", "Bekl_real"),
    ("Food_nom", "Food_real"),
]:
    g_nom  = cagr(df[label_nom], df["Jahr"])
    g_real = cagr(df[label_real], df["Jahr"])
    print(f"{label_nom}: CAGR nominal = {g_nom:.2%}, real = {g_real:.2%}")

# ---------- 6) Plots speichern (erst speichern, dann show) ----------

# a) Lebensmittel-Einzelhandel: nominal vs real
fig1, ax1 = plt.subplots()
ax1.plot(df["Jahr"], df["LM_Umsatz_nom"], marker="o", label="nominal")
ax1.plot(df["Jahr"], df["LM_Umsatz_real"], marker="o", label="real (inflationsbereinigt)")
ax1.set_title("Lebensmitteleinzelhandel – Umsatz nominal vs. real")
ax1.set_xlabel("Jahr"); ax1.set_ylabel("Mio. €")
ax1.legend()
fig1.tight_layout()
fig1.savefig("Bilder\lm_umsatz_nominal_vs_real.png", dpi=300)
plt.show()

# b) Konsumausgaben Food & Bekleidung: nominal vs real
fig2, ax2 = plt.subplots()
ax2.plot(df["Jahr"], df["Food_nom"], marker="o", label="Food nominal")
ax2.plot(df["Jahr"], df["Food_real"], marker="o", label="Food real")
ax2.plot(df["Jahr"], df["Bekl_nom"], marker="o", label="Bekleidung nominal")
ax2.plot(df["Jahr"], df["Bekl_real"], marker="o", label="Bekleidung real")
ax2.set_title("Konsumausgaben – nominal vs. real")
ax2.set_xlabel("Jahr"); ax2.set_ylabel("Mrd. €/Index-Einheiten")
ax2.legend()
fig2.tight_layout()
fig2.savefig("Bilder\konsum_nominal_vs_real.png", dpi=300)
plt.show()

# Optional: Datenexport
df.to_csv("warenkorb_auswertung.csv", index=False)
