# PRISM Investigator Dashboard Design System

## Aesthetic Overview
- **Theme**: "Cyber-Clay-Glass" - A fusion of classic glassmorphism with curvy texture claymorphism.
- **Color Palette**: 
  - **Background / Primary Dark**: Midnight Navy (#1A202C or similar deep blue/slate).
  - **Accents / Highlights**: Platinum (#E5E4E2) for typography and subtle edges.
  - **Softer Accents / Cards**: Cream (#FFFDD0) used sparingly for soft glow or specific clay UI elements.

## Design Patterns
1. **Glassmorphism**:
   - High `backdrop-blur`.
   - Semi-transparent fills (e.g., `rgba(255, 255, 255, 0.05)`).
   - Crisp 1px translucent borders (`border-white/10`).
2. **Claymorphism**:
   - Soft, puffy 3D elements.
   - Large `border-radius`.
   - Complex box-shadows (dark drop shadow + light inset shadow to create extrusion effect).

## Core Layout
- A persistent sidebar navigation (glassmorphism).
- A main content area with a deep Midnight Navy background.

## Key Screens
1. **Dashboard**: High-level metric clay cards and active investigations list.
2. **Investigation View**: Split pane containing visualizers and data panels.
3. **Actor Graph**: Interactive node graph utilizing **React Flow**. Nodes styled as glass/clay orbs.
4. **Timeline**: Vertical milestone list for chronological events.
5. **Evidence Panel**: Progress bars for Support/Contradict weights.
6. **Adversarial Panel**: Red-team warnings and leave-one-out metrics.
