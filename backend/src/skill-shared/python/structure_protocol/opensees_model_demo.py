#!/usr/bin/env python3
"""
OpenSeesPy demo script generated from unified schema.
Cantilever beam analysis with uniform load.
"""

import openseespy.opensees as ops

print("Starting OpenSeesPy model...")

# Initialize 2D model
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
print("Model initialized (2D)")

# Define nodes
L = 6.0  # span in meters
ops.node(1, 0.0, 0.0)   # fixed support
ops.node(2, L, 0.0)   # free end
print(f"Nodes defined (span = {L} m)")

# Fix supports: cantilever (fixed at node 1, free at node 2)
ops.fix(1, 1, 1, 1)  # fixed: ux, uy, rz
ops.fix(2, 0, 0, 0)  # free
print("Constraints applied (cantilever)")

# Define material (steel for demo, easier to get deflection)
E = 200e9  # 200 GPa (steel)
A = 0.01   # 0.01 m^2
I = 1e-5   # 0.00001 m^4 (smaller I to get visible deflection)
ops.uniaxialMaterial('Elastic', 1, E)
print("Material defined (E=200 GPa, A=0.01 m², I=1e-5 m⁴)")

# Define section (2D elastic: A, E, I)
ops.section('Elastic', 1, A, E, I)
print("Section defined")

# Define transformation
ops.geomTransf('Linear', 1)
print("Transformation defined")

# Define element
ops.element('elasticBeamColumn', 1, 1, 2, 1, 1)
print("Element created")

# Define load: uniform distributed load (downwards)
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
q = 50e3  # 50 kN/m (large load to see deflection)
# For beam element, beamUniform: Wy, Wz (for 2D, Wz is out-of-plane)
# Our model is in X-Y plane, so beam's local y is global Y
ops.eleLoad('-ele', 1, '-type', '-beamUniform', 0, -q)  # -Y direction
print(f"Load applied: uniform {q/1000:.1f} kN/m (downwards)")

# Analysis settings with more load steps
n_steps = 10
ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.integrator('LoadControl', 1.0/n_steps)
ops.test('NormUnbalance', 1e-6, 200)
ops.algorithm('Newton')
ops.analysis('Static')

# Perform analysis
print(f"Starting analysis ({n_steps} load steps)...")
ok = 0
for i in range(n_steps):
    ok = ops.analyze(1)
    if ok != 0:
        print(f'  -> step {i+1} failed')
        # Try modified Newton
        ops.algorithm('ModifiedNewton', '-initial')
        ok = ops.analyze(1)
        if ok != 0:
            print('  -> step failed even with ModifiedNewton')
            break
if ok == 0:
    print('✅ Analysis successful!')
else:
    print('❌ Analysis did not converge')

# Get displacements and reactions
if ok == 0:
    disp_x = ops.nodeDisp(2, 1)
    disp_y = ops.nodeDisp(2, 2)
    disp_rz = ops.nodeDisp(2, 3)
    print(f"\n📊 Results at free end (node 2):")
    print(f"  Horizontal displacement: {disp_x*1000:.6f} mm")
    print(f"  Vertical displacement:   {disp_y*1000:.6f} mm")
    print(f"  Rotation:                {disp_rz:.6f} rad")

    reaction = ops.nodeReaction(1)
    print(f"\n📊 Reactions at fixed support (node 1):")
    print(f"  Shear Fy: {reaction[1]/1000:.3f} kN")
    print(f"  Moment Mz: {reaction[2]/1000:.3f} kN·m")

print("\n✅ OpenSeesPy model executed successfully!")