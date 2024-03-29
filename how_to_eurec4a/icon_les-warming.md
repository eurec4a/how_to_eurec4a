---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.7.1
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# EUREC<sup>4</sup>A warming experiments with ICON-LES

## Motivation

We aim to get a deeper understanding of the trade-wind cloud feedback. The quantitative aspect of this is to get an accurate estimate of the magnitude of cloud feedback, the qualitative aspect is to get a better understanding of processes involved in the clouds' response to global warming. Our large-domain LES with realistic boundary conditions allows a good representation of mesoscale processes and thus opens a unique view on this topic.

## Domain

We use the non-hydrostatic ICON model with two nested domains in the EUREC<sup>4</sup>A field campaign area. The simulations with unperturbed boundary conditions (our control run) are available as part of the [EUREC<sup>4</sup>A intake catalog](https://github.com/eurec4a/eurec4a-intake) {cite:p}`Schulz_Stevens:2023`. 

![](https://gitlab.gwdg.de/hernan.campos/warm_eurec4a/-/raw/f107ebccdd2940629f9d388cdbed1a48bc643367/03_adiabatic_warming/img/fig_rectangle_domains_1and2_with_resolution.png)

## Forcing

For the process understanding we will follow the idea that the effects of global warming on the trade-wind regime can be separated into a dynamic (large scale circulation changes) and a thermodynamic part (increased temperatures; {cite:t}`Bonyetal:2004`). To get an accurate estimate we will use the pseudo global warming technique (PGW) with its comprehensive and realistic, GCM derived, climate change signal, which combines and scales thermodynamic and dynamic effects. This leaves us with three warming experiment setups:

- A thermodynamic global warming, increasing only (surface and air) temperatures by 4 kelvin.
- A dynamic global warming, only decreasing the subsidence, mimicing the slow down of the hadley circulation
- A pseudo-global warming (PGW) experiment, aiming for a comprehensible, multi-variable climate change signal. 


## Thermodynamic global warming

In this - our first - setup we raise the surface temperature by 4 kelvin. To extrapolate this warming into the vertical profile, we construct two moist adiabatic profiles from two surface temperatures and use the difference between the two as a *delta*. This idealised *delta* is then added to the existing boundary conditions of the control setup. We keep relative humidity constant through warming by adjusting the specific humidity accordingly.

![](https://gitlab.gwdg.de/hernan.campos/warm_eurec4a/-/raw/main/03_adiabatic_warming/img/fig_delta_from_moist_adiabats_4K.png?ref_type=heads)

## A dynamic global warming
__in planning__

## A pseudo-global warming (PGW) experiment
__in planning as part of EUREC4A-MIP__