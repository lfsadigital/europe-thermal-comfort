---
name: Comfy Days filter surface
description: Observed compact map filters and optional daily-low controls
colors:
  navy: "#0a2463"
  deep: "#061640"
  gold: "#f5c518"
  blue: "#2da0e0"
  surface: "#fff"
  border: "#d8dfeb"
  muted: "#50617d"
  chip: "#f5f7fb"
rounded:
  chip: "6px"
  control: "8px"
  panel: "12px"
---

# Design System: Daily-low filter surface

## Overview

This is a scoped record of the current map controls. It does not replace the project DESIGN.md. Sources inspected: `dist/index.html`, `dist/workspace-ui.css`, `dist/workspace-ui.js`, `dist/lfsa-brand.css`, and `.impeccable/review/desktop-controls.png` and `mobile-controls.png`.

The surface uses a compact Weather / Cities group, applied-rule chips, and a persistent Highlights bar. The screenshots show Weather open with daily lows enabled, inputs set to 12 and 22, and unapplied changes. The desktop screenshot states that map processing is pending. Complete remote data readiness is unknown from this inspection.

The requested references were ReUI filters and inputs, and Reactbits navigation. The inspected implementation uses local HTML, CSS, and JavaScript. These observations do not establish that either reference library is installed.

## Colors

Navy supplies control text, the open navigation segment, checkbox accents, and range accents. Gold supplies the Apply weather action. Blue marks pending Weather edits and focused number inputs. White panels and light borders separate controls from the map. Muted text carries supporting information.

**The Data Color Rule.** The brand stylesheet identifies the climate palette as data encoding, independent of brand action colors.

## Typography

Inter is used for body text, navigation, inputs, and labels. Space Grotesk is assigned to headings and prominent location metrics. Local font files are declared in the brand stylesheet.

Weather navigation uses compact labels (13px desktop; 12px at the 760px breakpoint). Panel headings use 16px. Number fields use 13px desktop and 16px at the 650px breakpoint. Number inputs use tabular figures.

## Layout

Applied-rule chips sit above the map. The Weather / Cities group sits inside the map at the upper left; export sits at the upper right. Highlights occupies a separate white bar below navigation. The open filter sheet starts below that bar. A ResizeObserver measures the Highlights bar and writes its height for sheet positioning.

The filter sheet is at most 360px wide. Its height depends on map height and Highlights height. The Weather form keeps its heading and Apply area outside its scrolling rule grid. Both screenshots show Highlights visible while Weather is open.

At widths up to 760px, Highlights uses two columns with sliders below the threshold inputs. The map has a declared height of 620px. Navigation summaries, Highlights toggle, threshold number inputs, threshold sliders, and the Highlights information control have a minimum target height of 44px. At widths up to 650px, Weather number inputs and toggle rows also have a minimum height of 44px. Applied-rule chips use a separate minimum height of 36px at that breakpoint; the 44px rule does not cover every control.

## Elevation & Depth

White surfaces use thin borders and soft navy shadows over the map. Navigation and export use `0 4px 16px #06164020`; the filter sheet uses `0 8px 28px #06164030`. The navigation group, Highlights, and sheet occupy separate layers.

When reduced motion is not requested, navigation colors transition over 0.18 seconds and the sheet reveals over 0.18 seconds with a short upward offset. The reveal animation is absent from the reduced-motion path.

## Shapes

Navigation and filter sheets use gently rounded panel corners. Navigation segments, fieldsets, inputs, and Highlights use smaller rounded corners. Applied chips have the smallest rounded rectangle. Information controls are circular. All three main surface types use the same light border family.

## Components

### Filter navigation

Weather and Cities are native disclosure controls grouped in one white container. The open segment uses navy with white text; a closed segment has a pale hover fill. JavaScript closes the other panel when one opens. Clicking outside the filter overlay and information popovers closes panels. Escape closes an open panel and returns focus to its summary.

### Applied-rule chips

JavaScript builds buttons from applied high temperature, rain, optional low temperature, optional sunshine, and relevant city-filter descriptions. Each chip opens the corresponding Weather or Cities panel. Its accessible label begins with “Edit”. The chips describe applied state; they do not copy pending Weather field edits.

### Daily low

The initial HTML marks daily low as optional. Its checkbox is unchecked. Its From and To number inputs start disabled, with values 12 and 22°C. CSS hides the input row while the checkbox is unchecked. These are two numeric range limits, not a dual-thumb slider.

The information text defines daily minimum over the same UTC day. It says both high and low must meet their ranges when enabled, the larger temperature deviation sets the penalty, and missing minima do not count as passing. This is observed interface text; this document does not verify the remote calculation or archive coverage.

### Pending Weather edits

Workspace JavaScript compares current Weather fields with applied parameters. A difference shows the pending message and a blue dot in the Weather segment. The screenshots show “Changes not applied” above the gold Apply weather button. Export is disabled while Weather edits are pending; its title asks the user to apply Weather changes first. The UI's applied callback refreshes state and closes Weather.

### Highlights

Highlights remains separate from Weather. Initial HTML has Highlights checked, Score ≥8, and Days/year ≥180. Each threshold has a number input and a range input. The screenshot checkbox is unchecked, showing a captured interaction state rather than the initial HTML state.

Its information text says both climate thresholds must pass, these thresholds change highlights rather than daily scores, and city points must also meet population and active city filters with known data. Numeric validity is checked before export is enabled.

## Do's and Don'ts

- Do preserve the LFSA navy and gold palette, and the Inter / Space Grotesk pairing.
- Do keep applied rules distinct from pending Weather edits.
- Do keep Highlights visible above an open filter sheet.
- Do identify daily low as optional and preserve its initial unchecked state.
- Don't describe these numeric From / To fields as sliders.
- Don't claim all mobile controls have 44px targets; the source gives chips a smaller minimum.
- Don't claim complete remote daily-low data readiness from the screenshots or control markup.
- Don't treat this scoped surface record as a broad redesign or a replacement for DESIGN.md.
