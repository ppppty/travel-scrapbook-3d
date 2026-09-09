// THREE.Vector3-compatible corners/target; rotation = camera.quaternion after lookAt.
// tanX/tanY include safe viewport fractions, camera zoom and desired margin.
export function fittedDistance(corners, target, rotation, tanX, tanY) {
  if (!(Number.isFinite(tanX) && Number.isFinite(tanY) && tanX > 0 && tanY > 0)) {
    throw new RangeError('Positive finite angle tangents are required');
  }
  const inverse = rotation.clone().invert(), p = target.clone();
  let distance = 1;
  for (const corner of corners) {
    p.copy(corner).sub(target).applyQuaternion(inverse);
    distance = Math.max(distance, p.z + Math.abs(p.x) / tanX, p.z + Math.abs(p.y) / tanY);
  }
  return distance;
}

export function boxCorners(box) {
  if (box.isEmpty()) return [];
  const points = [];
  for (const x of [box.min.x, box.max.x])
    for (const y of [box.min.y, box.max.y])
      for (const z of [box.min.z, box.max.z]) points.push(box.min.clone().set(x, y, z));
  return points;
}
