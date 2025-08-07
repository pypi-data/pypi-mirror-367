import torch
import time
from scipy.stats import poisson
from scipy.spatial import Delaunay, Voronoi
import numpy as np

class Voidwalker:
    """
    Voidwalker finds maximally empty spheres (voids) in point-cloud data with auto-parameter estimation
     and various seeding strategies.

    Seeding options:
      - 'delaunay': Delaunay circumcenters
      - 'delaunay-reverse': small-radius simplices only
      - 'voronoi-vertices': finite Voronoi vertices
      - 'hill-climb': uniform random starts + ascent
      - 'hill-climb-data': k-NN midpoints + ascent
      - 'poisson-disk': dart-throwing exclusion
    """

    def __init__(
        self,
        points,
        initial_radius=None,
        margin=None,
        growth_step=None,
        move_step=None,
        max_radius=None,
        max_steps=25000,
        max_failures=10,
        alpha=0.05,
        record_frames=False,
        seeding_type="voronoi",
        hill_steps=50,
        n_hill_starts=100,
        poisson_exclusion_radius=None,
        knn_k=5,
        jitter=1e-3,
        max_simplex_radius=None
    ):
        # Data and dimensions
        self.points = points
        N, d = points.shape
        self.d = d

        # Auto-estimate parameters via NN-distance peak detection
        with torch.no_grad():
            dmat = torch.cdist(points, points)
            dmat.fill_diagonal_(float('inf'))
            nn_dist, _ = dmat.min(dim=1)
        nn = nn_dist.cpu().numpy()
        hist, edges = np.histogram(nn, bins=50)
        centers = (edges[:-1] + edges[1:]) / 2
        peaks = np.where((hist[1:-1] > hist[:-2]) & (hist[1:-1] > hist[2:]))[0] + 1
        peak_loc = centers[peaks[0]] if len(peaks) > 0 else np.median(nn)

        self.initial_radius = float(initial_radius) if initial_radius is not None else 0.8 * peak_loc
        self.margin = float(margin) if margin is not None else peak_loc
        self.outer_ring_width = 2 * self.margin
        self.growth_step = float(growth_step) if growth_step is not None else 0.2 * peak_loc
        self.move_step = float(move_step) if move_step is not None else peak_loc

        # Growth parameters
        self.max_radius = max_radius
        self.max_steps = max_steps
        self.max_failures = max_failures
        self.alpha = alpha
        self.record_frames = record_frames
        self.frames = []
        self.memberships = None
        self.max_simplex_radius = max_simplex_radius

        # Bounding box & global density
        min_vals = points.min(dim=0).values
        max_vals = points.max(dim=0).values
        self.bounds = torch.stack([min_vals, max_vals], dim=1)
        area = torch.prod(self.bounds[:,1] - self.bounds[:,0])
        self.global_density = N / area

        # Seeding with timing
        t0 = time.perf_counter()
        self.seeds = self._seed_voids(
            seeding_type, hill_steps, n_hill_starts,
            poisson_exclusion_radius, knn_k, jitter
        )
        self.t_seeding = time.perf_counter() - t0

        self.n_voids = self.seeds.shape[0]
        if self.n_voids == 0:
            raise RuntimeError(f"No seeds generated for seeding_type={seeding_type}")

        # Initialize voids tensor [centers, radius]
        init_r = float(self.initial_radius)
        self.voids = torch.cat([
            self.seeds,
            torch.full((self.n_voids,1), init_r, device=points.device)
        ], dim=1)

        # Tracking state
        self.active = torch.ones(self.n_voids, dtype=torch.bool, device=points.device)
        self.consec_failures = torch.zeros(self.n_voids, dtype=torch.int, device=points.device)
        self.termination_reason = torch.full((self.n_voids,), -1, dtype=torch.int, device=points.device)

        # Initialize CSR timer
        self.t_csr = 0.0

    def _seed_voids(self, seeding_type, hill_steps, n_starts, exclusion_radius, knn_k, jitter):
        if seeding_type == 'delaunay':
            return self._seed_delaunay()
        if seeding_type == 'delaunay-reverse':
            return self._seed_delaunay_reverse(self.max_simplex_radius)
        if seeding_type == 'voronoi':
            return self._seed_voronoi_vertices()
        if seeding_type == 'hill-climb':
            return self._seed_hill_climb(hill_steps, n_starts)
        if seeding_type == 'hill-climb-data':
            return self._seed_hill_climb_data(hill_steps, n_starts, knn_k, jitter)
        if seeding_type == 'poisson-disk':
            return self._seed_poisson_disk(exclusion_radius)
        raise ValueError(f"Unknown seeding_type: {seeding_type}")

    def _seed_delaunay(self):
        pts = self.points.cpu().numpy()
        tri = Delaunay(pts)
        simp = torch.tensor(pts[tri.simplices], device=self.points.device, dtype=self.points.dtype)
        v0, vs = simp[:,0], simp[:,1:]
        B = vs - v0.unsqueeze(1)
        vi2 = (vs**2).sum(dim=2)
        v02 = (v0**2).sum(dim=1, keepdim=True)
        off = torch.linalg.solve(B, ((vi2 - v02)*0.5).unsqueeze(2)).squeeze(2)
        centers = v0 + off
        mask = ((centers >= self.bounds[:,0]) & (centers <= self.bounds[:,1])).all(dim=1)
        centers = centers[mask]
        centers = torch.unique(centers, dim=0)
        return torch.clamp(centers, self.bounds[:,0], self.bounds[:,1])

    def _seed_delaunay_reverse(self, max_R):
        if max_R is None:
            raise ValueError("max_simplex_radius required for reverse seeding")
        pts = self.points.cpu().numpy()
        tri = Delaunay(pts)
        simp = torch.tensor(pts[tri.simplices], device=self.points.device, dtype=self.points.dtype)
        v0, vs = simp[:,0], simp[:,1:]
        B = vs - v0.unsqueeze(1)
        vi2 = (vs**2).sum(dim=2)
        v02 = (v0**2).sum(dim=1, keepdim=True)
        off = torch.linalg.solve(B, ((vi2 - v02)*0.5).unsqueeze(2)).squeeze(2)
        radii = off.norm(dim=1)
        centers = v0 + off
        mask = (radii <= max_R) & ((centers >= self.bounds[:,0]) & (centers <= self.bounds[:,1])).all(dim=1)
        filtered = centers[mask]
        if filtered.shape[0] == 0:
            return self._seed_delaunay()
        return torch.clamp(filtered, self.bounds[:,0], self.bounds[:,1])

    def _seed_voronoi_vertices(self):
        pts = self.points.cpu().numpy()
        vor = Voronoi(pts)
        verts = []
        for v in vor.vertices:
            vt = torch.tensor(v, device=self.points.device, dtype=self.points.dtype)
            if ((vt >= self.bounds[:,0]) & (vt <= self.bounds[:,1])).all():
                verts.append(vt)
        seeds = torch.stack(verts) if verts else torch.empty((0,self.d), device=self.points.device)
        if seeds.shape[0]:
            dmin = torch.cdist(seeds, self.points).min(dim=1).values
            seeds = seeds[dmin > (self.initial_radius + self.margin)]
        return seeds

    def _seed_hill_climb(self, hill_steps, n_starts):
        starts = torch.rand(n_starts, self.d, device=self.points.device)
        starts = starts * (self.bounds[:,1] - self.bounds[:,0]) + self.bounds[:,0]
        centers = starts.clone()
        for _ in range(hill_steps):
            d = torch.cdist(centers, self.points)
            idx = d.argmin(dim=1)
            nearest = self.points[idx]
            dirs = centers - nearest
            norm = dirs.norm(dim=1, keepdim=True)
            centers += dirs / (norm + 1e-8) * norm
        tmp = (centers * 1e4).round() / 1e4
        uniq = torch.unique(tmp, dim=0)
        return torch.clamp(uniq, self.bounds[:,0], self.bounds[:,1])

    def _seed_hill_climb_data(self, hill_steps, n_starts, k, jitter):
        dmat = torch.cdist(self.points, self.points)
        nn = dmat.topk(k+1, largest=False).indices[:,1:]
        i = torch.randint(len(self.points), (n_starts,), device=self.points.device)
        col = torch.randint(k, (n_starts,), device=self.points.device)
        j = nn[i, col]
        pi, pj = self.points[i], self.points[j]
        starts = 0.5 * (pi + pj) + torch.randn_like(pi) * jitter
        centers = starts.clone()
        for _ in range(hill_steps):
            d = torch.cdist(centers, self.points)
            idx = d.argmin(dim=1)
            nearest = self.points[idx]
            dirs = centers - nearest
            norm = dirs.norm(dim=1, keepdim=True)
            centers += dirs / (norm + 1e-8) * norm
        tmp = (centers * 1e4).round() / 1e4
        uniq = torch.unique(tmp, dim=0)
        return torch.clamp(uniq, self.bounds[:,0], self.bounds[:,1])

    def _seed_poisson_disk(self, exclusion_radius):
        if exclusion_radius is None:
            exclusion_radius = self.initial_radius + self.margin
        seeds, grid = [], {}
        cell = exclusion_radius / torch.sqrt(torch.tensor(self.d, dtype=torch.float32))
        def key(pt): return tuple((pt/cell).floor().int().tolist())
        attempts, max_a = 0, 10 * len(self.points)
        while attempts < max_a:
            p = torch.rand(self.d, device=self.points.device)
            p = p * (self.bounds[:,1] - self.bounds[:,0]) + self.bounds[:,0]
            if torch.min(torch.norm(self.points-p, dim=1)) < exclusion_radius:
                attempts += 1
                continue
            k0 = key(p); close = False
            for off in torch.cartesian_prod(torch.tensor([-1,0,1]), torch.tensor([-1,0,1])):
                nk = (k0[0]+off[0].item(), k0[1]+off[1].item())
                for q in grid.get(nk, []):
                    if torch.norm(p-q) < exclusion_radius:
                        close = True
                        break
                if close: break
            if not close:
                grid.setdefault(k0, []).append(p)
                seeds.append(p)
            attempts += 1
        return torch.stack(seeds) if seeds else torch.empty((0,self.d), device=self.points.device)

    def _record_frame(self):
        if self.record_frames:
            c = self.voids[:,:self.d].clone()
            r = self.voids[:,self.d].clone()
            self.frames.append((c, r))

    def get_outer_ring_membership(self):
        centers = self.voids[:,:self.d]
        r = self.voids[:,self.d]
        d = torch.cdist(self.points, centers)
        inner = r.unsqueeze(0)
        outer = (r + self.outer_ring_width).unsqueeze(0)
        w = (d > inner) & (d < outer)
        self.memberships = [torch.where(w[:,i])[0] for i in range(self.n_voids)]
        return self.memberships

    def _can_grow_mask(self):
        centers = self.voids[:,:self.d]
        pr = self.voids[:,self.d] + self.growth_step
        md = torch.cdist(centers, self.points).min(dim=1).values
        safe = md > pr + self.margin
        if self.max_radius is not None:
            safe &= pr <= self.max_radius
        return safe

    def _attempt_walk(self, mask=None):
        if mask is None:
            mask = self.active.clone()
        centers = self.voids[:,:self.d]
        r = self.voids[:,self.d]
        # Combined repulsion from points & voids
        rep = torch.zeros_like(centers)
        # point repulsion
        vp = torch.cdist(centers, self.points) < (r.unsqueeze(1) + self.margin)
        for i in range(self.n_voids):
            if mask[i]:
                pts_off = self.points[vp[i]]
                if pts_off.numel():
                    dirs = centers[i] - pts_off
                    rep[i] += (dirs / (dirs.norm(dim=1, keepdim=True) + 1e-8)).sum(dim=0)
        # void-void repulsion
        vv_dist = torch.cdist(centers, centers)
        for i in range(self.n_voids):
            for j in range(i+1, self.n_voids):
                sep = r[i] + r[j] + self.margin
                if vv_dist[i,j] < sep:
                    dir_ij = centers[i] - centers[j]
                    if dir_ij.norm():
                        u = dir_ij / dir_ij.norm()
                        rep[i] += u
                        rep[j] -= u
        # normalize & move
        norms = rep.norm(dim=1, keepdim=True)
        valid = norms.squeeze() > 0
        rep[valid] /= norms[valid]
        prop = centers + self.move_step * rep
        can = self._can_grow_mask() | (~mask)
        self.voids[can,:self.d] = prop[can]
        # clamp
        self.voids[:,:self.d] = torch.clamp(self.voids[:,:self.d], self.bounds[:,0], self.bounds[:,1])

    def _attempt_grow(self):
        t1 = time.perf_counter() # Begin CSR timer
        if not hasattr(self, 'csr_violated'):
            self.csr_violated = torch.zeros(self.n_voids, dtype=torch.bool, device=self.points.device)
        mems = self.get_outer_ring_membership()
        counts = torch.tensor([len(m) for m in mems], dtype=torch.float32, device=self.points.device)
        r = self.voids[:,self.d]
        exp = self.global_density * torch.pi * ((r + self.outer_ring_width)**2 - r**2)
        exp = exp.clamp(min=1e-8)
        pvals = 1.0 - torch.tensor(poisson.cdf(counts.cpu().numpy(), exp.cpu().numpy()), device=self.points.device)
        newcsr = (pvals <= self.alpha) & self.active & (~self.csr_violated)
        self.t_csr += time.perf_counter() - t1 # End CSR timer
        self.csr_violated |= newcsr
        can_grow = self._can_grow_mask()
        self.voids[can_grow, self.d] += self.growth_step
        self.consec_failures[can_grow] = 0
        fail = ~can_grow & self.active
        self.consec_failures[fail] += 1
        self.active &= self.consec_failures < self.max_failures
        # set termination reasons
        csr_end = self.csr_violated & (~self.active) & (self.termination_reason == -1)
        fail_end = (~self.csr_violated) & (~self.active) & (self.termination_reason == -1)
        self.termination_reason[csr_end] = 0
        self.termination_reason[fail_end] = 1
        self._record_frame()

    def run(self):
        t_start = time.perf_counter() # begin timer
        for _ in range(self.max_steps):
            if not self.active.any():
                break
            self._attempt_grow()
        t_total = time.perf_counter() - t_start # end timer

        # Final membership update
        self.memberships = self.get_outer_ring_membership()
        still = self.active & (self.termination_reason == -1)
        self.termination_reason[still] = 2

        # Print timing breakdown
        print(f"Seeding time:      {self.t_seeding:.3f}s")
        print(f"Total runtime:     {t_total:.3f}s")
        print(f"  CSR testing:     {self.t_csr:.3f}s")

        return self.voids, self.voids[:,self.d], self.frames if self.record_frames else None
