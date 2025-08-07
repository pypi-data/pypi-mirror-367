import torch
from voidwalker import Voidwalker
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

# Set random seed
torch.manual_seed(42)

# Load 2D localization CSV
data_prefix = "Nup96_sparse"
file_path = (
    f"/Users/jackpeyton/LocalDocs/groupa_data/outputs/"
    f"{data_prefix}_gra_seed_0_JACKSIM_infomap_S_5.0nm_sigma_BF1.0_"
    f"rollingball-1.0nm/CLUSTERING_RESULTS_clustered_results_2d.csv"
)
df = pd.read_csv(file_path)
emitter_pos = df[["x", "y"]].to_numpy(dtype=np.float32)
X = torch.tensor(emitter_pos, dtype=torch.float32)

# Instantiate Voidwalker with auto-parameters
vw = Voidwalker(
    points=X,
    initial_radius=None,
    margin=None,
    growth_step=None,
    move_step=None,
    max_radius=50,
    max_steps=50_000,
    max_failures=50,
    alpha=0.05,

    seeding_type="voronoi",
    max_simplex_radius=25.0,
    hill_steps=100,
    n_hill_starts=500
)

# Print out all key parameters (auto-estimated or user-supplied)
print(f"initial_radius = {vw.initial_radius:.3f}")
print(f"margin         = {vw.margin:.3f}")
print(f"growth_step    = {vw.growth_step:.3f}")
print(f"move_step      = {vw.move_step:.3f}")
print(f"max_radius     = {vw.max_radius}")

# Run the growth & CSR workflow
voids, radii, _ = vw.run()

# Print summary
#print("Termination reasons:", vw.termination_reason.tolist())
#for i, members in enumerate(vw.memberships):
    #print(f"Void {i}: {len(members)} points")

# Safely build unique_members
members_list = [m for m in vw.memberships if len(m) > 0]
if members_list:
    all_members = torch.cat(members_list)
else:
    all_members = torch.empty((0,), dtype=torch.long, device=X.device)
unique_members = torch.unique(all_members)
print(f"Total unique member points: {len(unique_members)}")

term_np = vw.termination_reason.cpu().numpy()

# Prepare point arrays
X_np = X.cpu().numpy()
unique = unique_members.cpu().numpy()
all_idx = np.arange(len(X_np))
non_members = np.setdiff1d(all_idx, unique)

fig = go.Figure()

# Unassigned
fig.add_trace(go.Scattergl(
    x=X_np[non_members,0], y=X_np[non_members,1],
    mode='markers',
    marker=dict(color='red', size=4, opacity=0.6),
    name='Unassigned points'
))

# Members
fig.add_trace(go.Scattergl(
    x=X_np[unique,0], y=X_np[unique,1],
    mode='markers',
    marker=dict(color='blue', size=4, opacity=0.6),
    name='Void-member points'
))

# Void circles
centres = voids[:, :2].cpu().numpy()
radii_np = radii.cpu().numpy()
terms = vw.termination_reason.cpu().numpy()
theta = np.linspace(0, 2*np.pi, 16)
xs_blue, ys_blue, xs_black, ys_black = [], [], [], []

for (cx, cy), r, term in zip(centres, radii_np, terms):
    x_circ = cx + r*np.cos(theta)
    y_circ = cy + r*np.sin(theta)
    # insert NaN to break between circles
    if term == 0:
        xs_blue.extend(x_circ.tolist() + [np.nan])
        ys_blue.extend(y_circ.tolist() + [np.nan])
    else:
        xs_black.extend(x_circ.tolist() + [np.nan])
        ys_black.extend(y_circ.tolist() + [np.nan])

fig.add_trace(go.Scattergl(
    x=xs_blue, y=ys_blue,
    mode='lines', line=dict(color='blue', width=1.5),
    name='CSR‐terminated'
))
fig.add_trace(go.Scattergl(
    x=xs_black, y=ys_black,
    mode='lines', line=dict(color='black', width=1.5),
    name='Other terminations'
))

fig.update_layout(
    title="Member (blue) vs Unassigned (red) Localizations",
    xaxis_title="X (nm)", yaxis_title="Y (nm)",
    width=800, height=800,
    yaxis=dict(scaleanchor="x", scaleratio=1)
)

fig.update_traces(hoverinfo='skip', selector=dict(mode='markers'))
fig.update_traces(hoverinfo='skip', selector=dict(mode='lines'))

fig.show()