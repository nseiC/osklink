"""Diagrama de Bode a partir de um arquivo de ensaio (sample.py) via detecção lock-in.

Para cada frequência f e cada canal, usando o vetor de tempo da captura:
    X = (2/N) * sum(v * cos(2*pi*f*t))
    Y = (2/N) * sum(v * sin(2*pi*f*t))
    amplitude = sqrt(X^2 + Y^2)          (amplitude de pico do seno em f)
    fase      = atan2(-Y, X)             (v ~ A*cos(2*pi*f*t + fase))

Como t é medido a partir do trigger do osciloscópio, as fases dos dois canais têm
a mesma referência, e a resposta em frequência é a razão entre os fasores:
    H     = (X2 - jY2) / (X1 - jY1)
    mag   = 20*log10(A2/A1)  [dB]
    phase = fase2 - fase1    [graus]

Antes da demodulação cada captura é cortada num número inteiro de períodos e a
componente DC é removida; sem isso o lock-in "vaza" e a amplitude/fase oscilam.

Uso:
    python3 bode.py ensaio.txt
gera ensaio_bode.png e ensaio_bode.csv ao lado do arquivo de entrada.
"""
import os
import sys
import re
import numpy as np

HEADER = re.compile(r"#\s*Frequencia:\s*([0-9.eE+-]+)\s*Hz\s*\((CH\d)\)")


def read_ensaio(path):
    """Retorna {frequência: {"CH1": (t, v), "CH2": (t, v)}}."""
    data = {}
    key, rows = None, []

    def flush():
        if key is not None and rows:
            arr = np.array(rows)
            data.setdefault(key[0], {})[key[1]] = (arr[:, 0], arr[:, 1])

    with open(path) as f:
        for line in f:
            m = HEADER.match(line)
            if m:
                flush()
                key, rows = (float(m.group(1)), m.group(2)), []
            elif line[0] not in "#\n":
                t, v = line.strip().rstrip(";").split(",")
                rows.append((float(t), float(v)))
    flush()
    return data


def lockin(t, v, f):
    """Fasor complexo Z = X - jY da componente em f (|Z| = amplitude de pico)."""
    w = 2 * np.pi * f
    v = v - v.mean()
    X = 2 * np.mean(v * np.cos(w * t))
    Y = 2 * np.mean(v * np.sin(w * t))
    return complex(X, -Y)


def integer_cycles(t, f):
    """Máscara com o maior número inteiro de períodos que cabe na captura."""
    dt = t[1] - t[0]
    cycles = int(np.floor((t[-1] - t[0] + dt) * f))
    if cycles < 1:
        return np.ones_like(t, dtype=bool), 0
    return (t - t[0]) < cycles / f - dt / 2, cycles


def clipped_fraction(v):
    """Fração de amostras grudadas no máximo/mínimo (sinal cortado pelo ADC)."""
    return max(np.mean(v == v.max()), np.mean(v == v.min()))


def fit_quality(t, v, f, Z):
    """1 = senoide perfeita; valores baixos indicam ruído, distorção ou f errada."""
    v = v - v.mean()
    fit = np.real(Z * np.exp(1j * 2 * np.pi * f * t))
    return 1 - np.sum((v - fit) ** 2) / np.sum(v ** 2)


def bode(data):
    rows = []
    for f in sorted(data):
        (t1, v1), (t2, v2) = data[f]["CH1"], data[f]["CH2"]
        mask, cycles = integer_cycles(t1, f)
        Z1 = lockin(t1[mask], v1[mask], f)
        Z2 = lockin(t2[mask], v2[mask], f)
        H = Z2 / Z1
        rows.append({
            "f": f,
            "A1": abs(Z1), "A2": abs(Z2),
            "mag_db": 20 * np.log10(abs(H)),
            "phase_deg": np.degrees(np.angle(H)),
            "cycles": cycles,
            "clip1": clipped_fraction(v1), "clip2": clipped_fraction(v2),
            "fit1": fit_quality(t1[mask], v1[mask], f, Z1),
            "fit2": fit_quality(t2[mask], v2[mask], f, Z2),
        })
    mark_suspect(rows)
    unwrap_phase(rows)
    return rows


def mark_suspect(rows, max_clip=0.10, max_dev=0.20):
    """Captura suspeita: canal saturado na tela ou amplitude de entrada (CH1) fora
    do padrão do ensaio, já que o gerador mantém a mesma amplitude em todas as
    frequências. Ruído não entra no critério: o lock-in foi feito para isso."""
    a1 = np.median([r["A1"] for r in rows])
    for r in rows:
        r["suspect"] = int(max(r["clip1"], r["clip2"]) > max_clip or abs(r["A1"] / a1 - 1) > max_dev)


def unwrap_phase(rows):
    """Fase contínua ao longo da frequência (sem saltos de 360°), desenrolada só com
    os pontos confiáveis e ancorada em (-180°, 180°] no pico de magnitude."""
    good = [r for r in rows if not r["suspect"]] or rows
    p = np.degrees(np.unwrap(np.radians([r["phase_deg"] for r in good])))
    peak = int(np.argmax([r["mag_db"] for r in good]))
    p -= 360 * np.round(p[peak] / 360)
    for r, ph in zip(good, p):
        r["phase_deg"] = ph
    gf = np.log10([r["f"] for r in good])
    for r in rows:
        if r not in good:
            near = p[int(np.argmin(abs(gf - np.log10(r["f"]))))]
            r["phase_deg"] += 360 * np.round((near - r["phase_deg"]) / 360)


def save_csv(rows, path):
    cols = list(rows[0])
    with open(path, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(f"{r[c]:.6g}" for c in cols) + "\n")


def plot(rows, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, ink2, grid, series, flag = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#d03b3b"
    f = np.array([r["f"] for r in rows])
    mag = np.array([r["mag_db"] for r in rows])
    phase = np.array([r["phase_deg"] for r in rows])
    bad = np.array([bool(r["suspect"]) for r in rows])

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9, 7), facecolor="#fcfcfb")
    for ax, y, label in ((ax1, mag, "Magnitude (dB)"), (ax2, phase, "Fase (graus)")):
        ax.set_facecolor("#fcfcfb")
        ax.semilogx(f[~bad], y[~bad], color=series, linewidth=2, zorder=2)
        ax.scatter(f[~bad], y[~bad], s=28, color=series, edgecolor="#fcfcfb", linewidth=1.5, zorder=3)
        if bad.any():
            ax.scatter(f[bad], y[bad], s=40, marker="x", color=flag, linewidth=2, zorder=4,
                       label="captura suspeita (CH1 cortado ou com amplitude errada)")
        ax.set_ylabel(label, color=ink2)
        ax.grid(True, which="both", color=grid, linewidth=0.8)
        ax.tick_params(colors=ink2)
        for s in ax.spines.values():
            s.set_color(grid)
    ax2.set_xlabel("Frequência (Hz)", color=ink2)
    ax1.set_title(title, color=ink, loc="left", fontsize=12)
    if bad.any():
        ax1.legend(frameon=False, labelcolor=ink2, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def main(path):
    rows = bode(read_ensaio(path))
    base = os.path.splitext(path)[0]
    save_csv(rows, base + "_bode.csv")
    plot(rows, base + "_bode.png", "Diagrama de Bode  —  H(f) = CH2 / CH1")
    print(f"{'f (Hz)':>10} {'A1 (V)':>9} {'A2 (V)':>9} {'mag (dB)':>9} {'fase (°)':>9} "
          f"{'ciclos':>6} {'clip1':>6} {'clip2':>6} {'fit1':>6} {'fit2':>6}  suspeita")
    for r in rows:
        print(f"{r['f']:10.1f} {r['A1']:9.4f} {r['A2']:9.4f} {r['mag_db']:9.2f} {r['phase_deg']:9.1f} "
              f"{r['cycles']:6d} {r['clip1']:6.1%} {r['clip2']:6.1%} {r['fit1']:6.3f} {r['fit2']:6.3f}  {'X' if r['suspect'] else ''}")
    print(f"\nSalvo: {base}_bode.png e {base}_bode.csv")


if __name__ == "__main__":
    main(sys.argv[1])
