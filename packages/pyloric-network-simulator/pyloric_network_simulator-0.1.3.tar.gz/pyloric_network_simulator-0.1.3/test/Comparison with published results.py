# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python (pyloric-sim)
#     language: python
#     name: pyloric-sim
# ---

# %% [markdown]
# ---
# bibliography:
#   - references.bib
# ---

# %% [markdown]
# # Comparison with published results

# %%
import numpy as np
import holoviews as hv
import pint

from types import SimpleNamespace
from addict import Dict

from pyloric_simulator.prinz2004 import (
    Prinz2004, neuron_models, channels, act_vars, h_slice, nhchannels, constants)

ureg = pint.UnitRegistry()
ureg.default_format = "~P"
Q_ = pint.Quantity
s  = ureg.s
ms = ureg.ms

# %% user_expressions=[]
hv.extension("bokeh")#, "matplotlib")

# %%
dims = SimpleNamespace(
    mpl = SimpleNamespace(
        t     = hv.Dimension("t", label="time", unit=r"$\mathrm{ms}$"),
        I_ext = hv.Dimension("I_ext", label="external input", unit=r"$\mathrm{nA}$"),
        Δt = hv.Dimension("Δt", label="time lag", unit=r"$\mathrm{ms}$"),
        I  = hv.Dimension("I", unit=r"$\mathrm{nA}$"),
        I2 = hv.Dimension("I2", label=r"$\langle I^2 \rangle$", unit=r"$\mathrm{nA}^2$"),
        V  = hv.Dimension("V", unit=r"$\mathrm{mV}$"),
        Ca = hv.Dimension("Ca", label="$[Ca^{2+}]$")
    ),
    bokeh = SimpleNamespace(
        t     = hv.Dimension("t", label="time", unit="ms"),
        I_ext = hv.Dimension("I_ext", label="external input", unit="nA"),
        Δt = hv.Dimension("Δt", label="time lag", unit="ms"),
        I  = hv.Dimension("I", unit="nA"),
        I2 = hv.Dimension("I2", label="⟨I²⟩", unit="nA"),
        V  = hv.Dimension("V", unit="mV"),
        Ca = hv.Dimension("Ca", label="[Ca²⁺]")
    )
)
colors = SimpleNamespace(
    curve = hv.Cycle("Dark2").values
)


# %%
def plot_traces(res, varname="V", pop_labels=None, backend="bokeh"):
    #init_run = model.integrate_warm_init()
    pop_names = res.V.columns.get_level_values("pop")
    if pop_labels is None:
        pop_labels = pop_names
    traces = getattr(res, varname).loc[:,[(pop_name,1) for pop_name in pop_names]]
    traces = traces.droplevel("index", axis="columns")  # Now that we have one neuron per pop, we don’t need the index

    hv.output(backend=backend)  # Workaround: If we set the desired backend as default, the curve colours are ignored
    fig = hv.Overlay([hv.Curve(traces, kdims="time", vdims=pop_name, label=pop_label).redim(**{pop_name: varname})
                     for pop_name, pop_label in zip(pop_names, pop_labels)]) \
         .redim(time=dims.bokeh.t)
         #.opts(ylabel=dims.bokeh.V.label)
    # Assign trace colours
    for pop_label, c in zip(pop_labels, colors.curve):
        fig.opts(hv.opts.Curve(f"Curve.{hv.core.util.sanitize_identifier_fn(pop_label)}", color=c))
    fig.opts(hv.opts.Curve(width=800, backend="bokeh"),
             hv.opts.Overlay(width=800, backend="bokeh"),
             hv.opts.Overlay(legend_position="right")
            )
    #fig.cols(1)
    return fig


# %% [markdown]
# ## In depth tracking of a single bursting cell
#
# Here we all dynamic variables (voltage, calcium, ion channels) for a single bursting neuron. The specific model is `AB/PD #3`, also shown in Figure 2 of {cite:t}`prinzSimilarNetworkActivity2004` (grey boxes at the top).

# %%
model = Prinz2004(pop_sizes={"AB": 1}, gs=[[0]], g_ion=neuron_models.loc[[f"AB/PD 3"]])
res = model.thermalize()
plot_traces(res, "V").opts(title="Spontaneous voltage activity, AB/PD 3")

# %%
# axes: time x channel x neuron
V  = res.V.to_numpy()
Ca = res.Ca.to_numpy()
p     = np.array(constants.p)  # Convert JAX to NumPy array
γ     = constants.γ
Caout = constants.Caout
E     = np.array(constants.E) # Convert JAX to NumPy array
Eleak = constants.Eleak
mphVE = res.m**p[:,np.newaxis] * (V[:,np.newaxis,:] - E[:,np.newaxis])
mphVE[:,h_slice,:] *=  res.h

# %% [markdown]
# Restrict plots to the range $[1.2\mathrm{s}, 3.6\mathrm{s}]$, corresponding to two burst periods. (We record a point every $\mathrm{ms}$ – this range is already long enough to make plotting sluggish.)

# %%
tslice = slice(*np.searchsorted(res.t, [1200, 3600]))
t     = res.t[tslice]
V     =  V[tslice, 0]
Ca    = Ca[tslice, 0]
mphVE = mphVE[tslice, :, 0]

# %% [markdown]
# Calcium concentration and calcium reversal potential

# %%
ECa = γ * np.log(Caout / Ca)
Ca_curve = hv.Curve(zip(t, Ca), kdims=dims.bokeh.t, vdims=dims.bokeh.Ca, label="Ca")
ECa_curve = hv.Curve(zip(t, ECa), kdims=dims.bokeh.t, vdims=dims.bokeh.V, label="E_Ca")

(Ca_curve + ECa_curve).opts(
    hv.opts.Curve(height=200, width=400, backend="bokeh"),
    hv.opts.Curve("Curve.Ca", title="Calcium concentration"),
    hv.opts.Curve("Curve.E_Ca", title="Calcium reversal potential"),
)

# %% [markdown]
# Ion currents, per channels
#
# :::{note}
# :class: margin
#
# The plot is interactive: try clicking the legend or zooming along the axes.
# :::

# %%
g     = model.g[0]      # [0] b/c single neuron
gleak = model.gleak[0]
I     = g * mphVE
Ileak = - gleak * (V - Eleak)

I_ion = [hv.Curve(zip(t, I[:,i]), label=channel, kdims=dims.bokeh.t, vdims=dims.bokeh.I)
         for i, channel in enumerate(channels)]
I_leak = hv.Curve(zip(t, Ileak), kdims=dims.bokeh.t, vdims=dims.bokeh.I, label="leak")
I_total = hv.Curve(zip(t, I.sum(axis=1) + Ileak), label="total",
                   kdims=dims.bokeh.t, vdims=dims.bokeh.I, )
ov_I = hv.Overlay([*I_ion, I_leak, I_total])
ov_I.opts(
    *(hv.opts.Curve(f"Curve.{hv.core.util.sanitize_identifier_fn(channel_label)}", color=c)
      for channel_label, c in zip(channels, colors.curve)),
    hv.opts.Curve("Curve.leak", color=colors.curve[7]),
    hv.opts.Curve("Curve.total", color="black", alpha=0.5), hv.opts.Curve("Curve.total", line_dash="dashed", backend="bokeh")
)
ov_I.opts(title="Ion currents per channel", width=700, legend_position="right")

# %% [markdown]
# Activation variables

# %%
m_inf, h_inf, τ_m, τ_h = act_vars(V, Ca)
h_inf = h_inf[h_slice]  # Remove dummy h values for neurons with no h variable
τ_h   = τ_h[h_slice]
# NB: act_vars(V, Ca) returns variables with shape (channel x time)

ov_minf = hv.Overlay([
    hv.Curve(zip(t, m_inf[i,:]), label=lbl, kdims=dims.bokeh.t, vdims="m_inf")
    for i, lbl in enumerate(channels)]
)
ov_minf.opts(title="m_inf")

ov_hinf = hv.Overlay([
    hv.Curve(zip(t, h_inf[i,:]), label=lbl, kdims=dims.bokeh.t, vdims="h_inf")
    for i, lbl in enumerate(channels[h_slice])]
)
ov_hinf.opts(title="h_inf")

ov_τm = hv.Overlay([
    hv.Curve(zip(t, τ_m[i,:]), label=lbl, kdims=dims.bokeh.t, vdims="τ_m")
    for i, lbl in enumerate(channels)]
)
ov_τm.opts(title="τ_m")

ov_τh = hv.Overlay([
    hv.Curve(zip(t, τ_h[i,:]), label=lbl, kdims=dims.bokeh.t, vdims="τ_h")
    for i, lbl in enumerate(channels[h_slice])]
)
ov_τh.opts(title="τ_h")

ov_m = hv.Overlay([
    hv.Curve(zip(t, res.m[tslice,i,0]), label=lbl, kdims=dims.bokeh.t, vdims="m")
    for i, lbl in enumerate(channels)]
)
ov_m.opts(title="m")

ov_h = hv.Overlay([
    hv.Curve(zip(t, res.h[tslice,i,0]), label=lbl, kdims=dims.bokeh.t, vdims="h")
    for i, lbl in enumerate(channels[h_slice])]
)
ov_h.opts(title="h")

# Total activation: m**p * h
hchannels = channels[h_slice]
nonhchannels = [ch for ch in channels if ch not in hchannels]
mph_curves = [hv.Curve(zip(t, res.m[:,i,0]**p[i] * res.h[:,i,0]), label=lbl,
                       kdims=dims.bokeh.t, vdims="m^p h")
              for i, lbl in enumerate(hchannels)]
mp_curves  = [hv.Curve(zip(t, res.m[:,i,0]**constants.p[i]), label=lbl,
                       kdims=dims.bokeh.t, vdims="m^p h")
              for i, lbl in enumerate(nonhchannels, start=len(hchannels))]
ov_mph = hv.Overlay(mph_curves + mp_curves)
ov_mph.opts(title="m^p h")

fig = ov_minf + ov_hinf + ov_τm + ov_τh + ov_m + ov_h + ov_mph

fig.opts(
    *(hv.opts.Curve(f"Curve.{hv.core.util.sanitize_identifier_fn(lbl)}", color=c)
      for lbl, c in zip(channels, colors.curve)),
    hv.opts.Overlay(width=500, legend_position="right", backend="bokeh")
).cols(2)

# %% [markdown]
# # Full three population circuit
#
# Figure 3 of {cite:t}`prinzSimilarNetworkActivity2004` gives example activities for different model parameters. We can use this to compare with simulations from our own model.

# %% [markdown]
# :::{figure} Fig3_Reference_output.webp
#
# Figure 3 from {cite:t}`prinzSimilarNetworkActivity2004`.
# Scale bars are 50 mV and 0.5 s.
# :::

# %% [markdown]
# ## Model definitions

# %% [markdown]
# Sim times

# %%
sim_time = Dict(
    a = 1.5*s,
    b = 10*s,
    c = 10*s,
    d = 15*s,
    e = 5*s,
    f = 1.5*s,
    g = 10*s,
    h = 10*s,
    i = 10*s,
    j = 5*s
)

burnin_time = 3*s
Δt          = 0.25*ms

# %% [markdown]
# a-e

# %% jupyter={"source_hidden": true}
a = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [ 0   , 0      ,   30   ,  0   ],
                  [ 0   , 0      ,   30   ,  0   ],
                  [ 100 ,  10    ,    0   ,  3   ],
                  [   3 ,  10    ,    1   ,  0   ] ],
    g_ion = neuron_models.loc[["AB/PD 2", "AB/PD 2", "LP 4", "PY 1"]],
)

b = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,  0   ],
                  [   0 ,   0    ,   10   ,  0   ],
                  [   3 ,   0    ,    0   ,  0   ],
                  [  30 ,   0    ,    3   ,  0   ] ],
    g_ion = neuron_models.loc[["AB/PD 2", "AB/PD 2", "LP 4", "PY 1"]],
)

c = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,    0   ,  0   ],
                  [   0 ,   0    ,    0   ,  0   ],
                  [   0 , 100    ,    0   ,  0   ],
                  [   1 ,  30    ,    3   ,  0   ] ],
    g_ion = neuron_models.loc[["AB/PD 2", "AB/PD 2", "LP 4", "PY 1"]],
)

d = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 2", "AB/PD 2", "LP 4", "PY 1"]],
)

e = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   30   ,   0  ],
                  [   0 ,   0    ,   30   ,   0  ],
                  [  30 ,  30    ,    0   ,  30  ],
                  [   1 ,  10    ,    1   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 2", "AB/PD 2", "LP 4", "PY 1"]],
)

# %% [markdown]
# f-j

# %% jupyter={"source_hidden": true}
f = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 3", "AB/PD 3", "LP 5", "PY 5"]],
)

g = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 1", "AB/PD 1", "LP 4", "PY 6"]],
)

h = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 5", "AB/PD 5", "LP 2", "PY 1"]],
)

i = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 1", "AB/PD 1", "LP 4", "PY 5"]],
)

j = Prinz2004(
    pop_sizes = {"PD": 2, "AB": 1, "LP": 1, "PY": 5},
    gs        = [ [   0 ,   0    ,   10   ,   0  ],
                  [   0 ,   0    ,   10   ,   0  ],
                  [ 100 ,   3    ,    0   ,  10  ],
                  [   1 ,  10    ,    3   ,   0  ] ],
    g_ion = neuron_models.loc[["AB/PD 4", "AB/PD 4", "LP 2", "PY 1"]],
)

# %% [markdown]
# ## Plotting config

# %%
dims = SimpleNamespace(
    mpl = SimpleNamespace(
        t     = hv.Dimension("t", label="time", unit=r"$\mathrm{ms}$"),
        I_ext = hv.Dimension("I_ext", label="external input", unit=r"$\mathrm{nA}$"),
        Δt = hv.Dimension("Δt", label="time lag", unit=r"$\mathrm{ms}$"),
        I  = hv.Dimension("I", unit=r"$\mathrm{nA}$"),
        I2 = hv.Dimension("I2", label=r"$\langle I^2 \rangle$", unit=r"$\mathrm{nA}^2$"),
        V  = hv.Dimension("V", unit=r"$\mathrm{mV}$")
    ),
    bokeh = SimpleNamespace(
        t     = hv.Dimension("t", label="time", unit="ms"),
        I_ext = hv.Dimension("I_ext", label="external input", unit="nA"),
        Δt = hv.Dimension("Δt", label="time lag", unit="ms"),
        I  = hv.Dimension("I", unit="nA$"),
        I2 = hv.Dimension("I2", label="⟨I²⟩", unit="nA"),
        V  = hv.Dimension("V", unit="mV")     
    )
)
colors = hv.Cycle("Dark2").values


# %%
def plot_Vtrace(sim_result):
    Vtraces = sim_result.V.loc[:,[("AB", 1), ("LP", 1), ("PY", 1)]].droplevel("index", axis="columns")   
    
    AB_curve = hv.Curve(Vtraces.loc[:,"AB"], label="AB/PD")
    LP_curve = hv.Curve(Vtraces.loc[:,"LP"], label="LP")
    PY_curve = hv.Curve(Vtraces.loc[:,"PY"], label="PY")
    
    panel = AB_curve + LP_curve + PY_curve
    
    panel.opts(
        hv.opts.Curve("Curve.AB_over_PD", xaxis="bare", ylabel="AB/PD"),
        hv.opts.Curve("Curve.LP", xaxis="bare"),
        hv.opts.Curve(xticks=(1000, 1500), yticks=(-40, 40), xformatter=" "),
        hv.opts.Curve(show_title=False, axiswise=True),
        hv.opts.Layout(axiswise=True),
        hv.opts.Curve(width=200, height=100, backend="bokeh"),
        hv.opts.Curve("Curve.PY", height=150, backend="bokeh"),  # Extra space for time axis
        hv.opts.Curve(aspect=2, backend="matplotlib"),
        hv.opts.Layout(fig_inches=2, sublabel_format="", backend="matplotlib")
    )
    
    return panel.cols(1)


# %% [markdown]
# ## Run simulations
#
# Plugging the neurons together into the circuit described in the paper, we get different outputs.
# (Panel _c_ could be argued to be qualitatively similar, but all models are very different.)
# The fact that our model reproduces the paper so nicely for single-cell models, but gives different results when three neurons are wired together, is indicative of the sensitivity of these models to parameter choice.
#
# In this case, since our RK45 integration raises numerical warnings – and the original implementation used the even less numerically robust Euler integration – there is reason to suspect that the precise parameter values found by Prinz et al. are contaminated by numerical issues.
# If that is the case, we would need to find different parameter values to reproduce the variety of behaviours with a more accurate integrator.

# %%
panels = {}

# %%
for model, label in [(a, "a"), (b, "b"), (c, "c"), (d, "d"), (e, "e"),
                     (f, "f"), (g, "g"), (h, "h"), (i, "i"), (j, "j")]:
    if label not in {"b", "c"}:
        continue
    n_time_steps = int(round((burnin_time + sim_time[label]) / Δt)) + 1
    res = model(np.arange(n_time_steps)*Δt.m)
    panel = plot_Vtrace(res).opts(title=label)
    panels[label] = panel

# %%
fig = hv.HoloMap(panels, kdims="panel").collate()

# %%
fig.opts(
    #hv.opts.Curve("Curve", height=300, width=500)
)

# %%
hv.save(fig, "reproduce_fig3.html")

# %%
