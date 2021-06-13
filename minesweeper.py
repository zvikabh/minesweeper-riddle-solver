import itertools
import sys
from typing import Tuple

import numpy as np


def parse_file(fname: str) -> Tuple[np.ma.MaskedArray, np.ma.MaskedArray]:
  """Returns masked arrays for num_neighbors and is_bomb."""
  txt = open(fname, 'r').read()
  lines = txt.split()

  shape = (len(lines) + 2, len(lines[0]) + 2)
  is_bomb = np.ma.MaskedArray(data=np.zeros(shape, dtype=bool),
                              mask=np.ones(shape, dtype=bool))
  num_neighbors = np.ma.MaskedArray(data=np.zeros(shape, dtype=np.int32),
                                    mask=np.ones(shape, dtype=bool))
  is_bomb[0, :] = False
  is_bomb[-1, :] = False
  is_bomb[:, 0] = False
  is_bomb[:, -1] = False

  for i, line in enumerate(lines):
    for j, c in enumerate(line):
      if c.isdigit():
        coords = (i + 1, j + 1)
        is_bomb[coords] = False
        num_neighbors[coords] = int(c)

  return num_neighbors, is_bomb


def is_feasible(num_neighbors: np.ma.MaskedArray, is_bomb: np.ma.MaskedArray,
                i_min: int, i_max: int,
                j_min: int, j_max: int) -> bool:
  for ii in range(i_min, i_max+1):
    for jj in range(j_min, j_max+1):
      if num_neighbors[ii, jj] is np.ma.masked:
        # Unknown number of neighbors,
        # so no contribution to feasibility decision.
        continue

      unknown_neighbors = is_bomb[ii-1:ii+2, jj-1:jj+2].mask.sum()
      known_neighbor_bombs = (~is_bomb[ii-1:ii+2, jj-1:jj+2].mask &
                              is_bomb[ii-1:ii+2, jj-1:jj+2].data).sum()
      min_neighbor_bombs = known_neighbor_bombs
      max_neighbor_bombs = known_neighbor_bombs + unknown_neighbors
      if (num_neighbors[ii, jj] < min_neighbor_bombs or
          num_neighbors[ii, jj] > max_neighbor_bombs):
        return False  # contradiction
  return True


def pretty_print(is_bomb: np.ma.MaskedArray, num_neighbors: np.ma.MaskedArray
                 ) -> str:
  cropped_is_bomb = is_bomb[1:-1, 1:-1]
  cropped_num_neighbors = num_neighbors[1:-1, 1:-1]
  pretty_array = np.where(
      cropped_is_bomb.mask,
      '?',
      np.where(cropped_is_bomb.data, 'x',
               np.where(cropped_num_neighbors.mask,
                        '.',
                        cropped_num_neighbors.data)))
  return '\n'.join(''.join(row.tolist()) for row in pretty_array)


def deduce_single_window(num_neighbors: np.ma.MaskedArray,
                         is_bomb: np.ma.MaskedArray,
                         height: int,
                         width: int,
                         i: int,
                         j: int) -> bool:
  """Propagate constraints at a given window."""
  if not is_feasible(num_neighbors, is_bomb, i, i+height-1, j, j+width-1):
    raise RuntimeError('Infeasible input!')

  # For each unknown coord, make a list with True and False for that coord.
  hypotheses = []
  for ii in range(i, i+height):
    for jj in range(j, j+width):
      if is_bomb[ii,jj] is np.ma.masked:
        hypotheses.append([(ii,jj,True), (ii,jj,False)])

  # Now go over all combinations of hypotheses.
  my_is_bomb = np.ma.copy(is_bomb)
  feasible_hypotheses = []
  for hypothesis in itertools.product(*hypotheses):
    for ii, jj, val in hypothesis:
      my_is_bomb[ii,jj] = val
    if is_feasible(num_neighbors, my_is_bomb, i, i+height-1, j, j+width-1):
      feasible_hypotheses.append(np.ma.copy(my_is_bomb))

  # Find conclusions that are identical across all feasible hypotheses.
  print(f'Found {len(feasible_hypotheses)} feasible hypotheses.')
  if not feasible_hypotheses:
    raise RuntimeError('Self-contradictory input!')
  feasible_hypotheses = np.ma.asarray(feasible_hypotheses)
  deduction_locs = np.ma.all(
      feasible_hypotheses[1:,:,:] == feasible_hypotheses[:-1,:,:], axis=0)
  print(f'Deduced {deduction_locs.sum() - (~is_bomb.mask).sum()} new pixels')
  if deduction_locs.sum() == (~is_bomb.mask).sum():
    return False

  # Update is_bomb accordingly.
  is_bomb[deduction_locs] = feasible_hypotheses[0,:,:][deduction_locs]
  print(pretty_print(is_bomb, num_neighbors))
  return True


def solve(num_neighbors: np.ma.MaskedArray, is_bomb: np.ma.MaskedArray,
          height: int, width: int) -> bool:
  shape = num_neighbors.shape
  advanced = True
  while advanced:
    advanced = False
    for i in range(1, shape[0]-height):
      for j in range(1, shape[1]-width):
        print(f'Deducing window @ {i},{j}')
        cur_advanced = deduce_single_window(
            num_neighbors, is_bomb, height, width, i, j)
        advanced = (advanced or cur_advanced)
        if is_bomb.mask.sum() == 0:
          print('Solved!')
          return True
  return False


def main():
  num_neighbors, is_bomb = parse_file(fname=sys.argv[1])
  print(num_neighbors)
  print(pretty_print(is_bomb, num_neighbors))
  solve(num_neighbors, is_bomb, 4, 4)
  print(pretty_print(is_bomb, num_neighbors))


if __name__ == '__main__':
  main()
