import numpy as np
from multitrackpy.rigid_body_transform_3d import rigid_transform_3D


def find_trafo_nocorr(pc1, pc2, corr_thres, track_ambiguous=False):
    errors = np.empty(pc1.shape[0])
    errors[:] = np.nan

    corrs = find_correspondences(pc1, pc2, corr_thres, track_ambiguous)

    if not np.any(np.equal(corrs.shape, 0)):
        (R, t) = rigid_transform_3D(pc1[corrs[0]].T, pc2[corrs[1]].T)
        errors[corrs[0]] = np.sqrt(np.sum(((R @ pc1[corrs[0]].T + t) - pc2[corrs[1]].T) ** 2, axis=0))
    else:
        R = np.empty((3, 3))
        R[:] = np.nan
        t = np.empty((3, 1))
        t[:] = np.nan

    return R, t, errors


def calc_dists(points, idx):
    return np.sqrt(np.sum((points - points[idx]) ** 2, axis=1))


# Finds correspondences between two point clouds by identifying points by their distances to other points
def find_correspondences(p1, p2, corr_thres=0.1, track_ambiguous=False):
    p1dists = [np.sort(calc_dists(p1, i)) for i in range(p1.shape[0])]
    p2dists = [np.sort(calc_dists(p2, i)) for i in range(p2.shape[0])]

    # Matrix of counts how often a distance in p1 matches a distance in p2
    disterr_n = np.zeros((len(p1dists), len(p2dists)))
    for (i, p1d) in enumerate(p1dists):
        for (j, p2d) in enumerate(p2dists):
            for d in p1d:
                if d != 0 and np.min(np.abs(p2d - d)) < corr_thres:
                    disterr_n[i, j] = disterr_n[i, j] + 1

    corrmat = np.where(np.all([np.equal(disterr_n, np.max(disterr_n, axis=0)[np.newaxis, :]),
                               disterr_n > (p1.shape[0] - 1) * 0.6], axis=0))
    corrs = np.asarray(corrmat)

    if not track_ambiguous:
        # Discard ambiguities
        uniquemask = [np.sum(corrs[0] == c) == 1 for c in corrs[0]]
        corrs = corrs.T[uniquemask].T
    else:
        old_corrs = corrs.copy().T
        corrs = np.zeros((0, 2), dtype=np.int64)
        for oc in old_corrs:
            if not oc[0] in corrs[:, 0] and not oc[1] in corrs[:, 1]:
                corrs = np.vstack((corrs, oc))
        corrs = corrs.T
        # Pick a set
    return corrs
