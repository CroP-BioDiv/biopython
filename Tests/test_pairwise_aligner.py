# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.


"""Tests for the PairwiseAligner in Bio.Align."""

import array
import os
import unittest

try:
    import numpy
except ImportError:
    from Bio import MissingPythonDependencyError

    raise MissingPythonDependencyError(
        "Install numpy if you want to use Bio.Align."
    ) from None

from Bio import Align, SeqIO
from Bio.Seq import Seq, reverse_complement
from Bio.SeqUtils import GC


class TestAlignerProperties(unittest.TestCase):
    def test_aligner_property_epsilon(self):
        aligner = Align.PairwiseAligner()
        self.assertAlmostEqual(aligner.epsilon, 1.0e-6)
        aligner.epsilon = 1.0e-4
        self.assertAlmostEqual(aligner.epsilon, 1.0e-4)
        aligner.epsilon = 1.0e-8
        self.assertAlmostEqual(aligner.epsilon, 1.0e-8)
        with self.assertRaises(TypeError):
            aligner.epsilon = "not a number"
        with self.assertRaises(TypeError):
            aligner.epsilon = None

    def test_aligner_property_mode(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        self.assertEqual(aligner.mode, "global")
        aligner.mode = "local"
        self.assertEqual(aligner.mode, "local")
        with self.assertRaises(ValueError):
            aligner.mode = "wrong"

    def test_aligner_property_match_mismatch(self):
        aligner = Align.PairwiseAligner()
        aligner.match_score = 3.0
        self.assertAlmostEqual(aligner.match_score, 3.0)
        aligner.mismatch_score = -2.0
        self.assertAlmostEqual(aligner.mismatch_score, -2.0)
        with self.assertRaises(ValueError):
            aligner.match_score = "not a number"
        with self.assertRaises(ValueError):
            aligner.mismatch_score = "not a number"
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 3.000000
  mismatch_score: -2.000000
  target_internal_open_gap_score: 0.000000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: 0.000000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: 0.000000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: 0.000000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: 0.000000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: 0.000000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )

    def test_aligner_property_gapscores(self):
        aligner = Align.PairwiseAligner()
        open_score, extend_score = (-5, -1)
        aligner.target_open_gap_score = open_score
        aligner.target_extend_gap_score = extend_score
        self.assertAlmostEqual(aligner.target_open_gap_score, open_score)
        self.assertAlmostEqual(aligner.target_extend_gap_score, extend_score)
        open_score, extend_score = (-6, -7)
        aligner.query_open_gap_score = open_score
        aligner.query_extend_gap_score = extend_score
        self.assertAlmostEqual(aligner.query_open_gap_score, open_score)
        self.assertAlmostEqual(aligner.query_extend_gap_score, extend_score)
        open_score, extend_score = (-3, -9)
        aligner.target_end_open_gap_score = open_score
        aligner.target_end_extend_gap_score = extend_score
        self.assertAlmostEqual(aligner.target_end_open_gap_score, open_score)
        self.assertAlmostEqual(aligner.target_end_extend_gap_score, extend_score)
        open_score, extend_score = (-1, -2)
        aligner.query_end_open_gap_score = open_score
        aligner.query_end_extend_gap_score = extend_score
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -5.000000
  target_internal_extend_gap_score: -1.000000
  target_left_open_gap_score: -3.000000
  target_left_extend_gap_score: -9.000000
  target_right_open_gap_score: -3.000000
  target_right_extend_gap_score: -9.000000
  query_internal_open_gap_score: -6.000000
  query_internal_extend_gap_score: -7.000000
  query_left_open_gap_score: -1.000000
  query_left_extend_gap_score: -2.000000
  query_right_open_gap_score: -1.000000
  query_right_extend_gap_score: -2.000000
  mode: global
""",
        )
        self.assertAlmostEqual(aligner.query_end_open_gap_score, open_score)
        self.assertAlmostEqual(aligner.query_end_extend_gap_score, extend_score)
        score = -3
        aligner.target_gap_score = score
        self.assertAlmostEqual(aligner.target_gap_score, score)
        self.assertAlmostEqual(aligner.target_open_gap_score, score)
        self.assertAlmostEqual(aligner.target_extend_gap_score, score)
        score = -2
        aligner.query_gap_score = score
        self.assertAlmostEqual(aligner.query_gap_score, score)
        self.assertAlmostEqual(aligner.query_open_gap_score, score)
        self.assertAlmostEqual(aligner.query_extend_gap_score, score)
        score = -4
        aligner.target_end_gap_score = score
        self.assertAlmostEqual(aligner.target_end_gap_score, score)
        self.assertAlmostEqual(aligner.target_end_open_gap_score, score)
        self.assertAlmostEqual(aligner.target_end_extend_gap_score, score)
        self.assertAlmostEqual(aligner.target_left_gap_score, score)
        self.assertAlmostEqual(aligner.target_left_open_gap_score, score)
        self.assertAlmostEqual(aligner.target_left_extend_gap_score, score)
        self.assertAlmostEqual(aligner.target_right_gap_score, score)
        self.assertAlmostEqual(aligner.target_right_open_gap_score, score)
        self.assertAlmostEqual(aligner.target_right_extend_gap_score, score)
        score = -5
        aligner.query_end_gap_score = score
        self.assertAlmostEqual(aligner.query_end_gap_score, score)
        self.assertAlmostEqual(aligner.query_end_open_gap_score, score)
        self.assertAlmostEqual(aligner.query_end_extend_gap_score, score)
        self.assertAlmostEqual(aligner.query_left_gap_score, score)
        self.assertAlmostEqual(aligner.query_left_open_gap_score, score)
        self.assertAlmostEqual(aligner.query_left_extend_gap_score, score)
        self.assertAlmostEqual(aligner.query_right_gap_score, score)
        self.assertAlmostEqual(aligner.query_right_open_gap_score, score)
        self.assertAlmostEqual(aligner.query_right_extend_gap_score, score)
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -3.000000
  target_internal_extend_gap_score: -3.000000
  target_left_open_gap_score: -4.000000
  target_left_extend_gap_score: -4.000000
  target_right_open_gap_score: -4.000000
  target_right_extend_gap_score: -4.000000
  query_internal_open_gap_score: -2.000000
  query_internal_extend_gap_score: -2.000000
  query_left_open_gap_score: -5.000000
  query_left_extend_gap_score: -5.000000
  query_right_open_gap_score: -5.000000
  query_right_extend_gap_score: -5.000000
  mode: global
""",
        )
        with self.assertRaises(ValueError):
            aligner.target_gap_score = "wrong"
        with self.assertRaises(ValueError):
            aligner.query_gap_score = "wrong"
        with self.assertRaises(TypeError):
            aligner.target_end_gap_score = "wrong"
        with self.assertRaises(TypeError):
            aligner.query_end_gap_score = "wrong"

    def test_aligner_nonexisting_property(self):
        aligner = Align.PairwiseAligner()
        with self.assertRaises(AttributeError) as cm:
            aligner.no_such_property
        self.assertEqual(
            str(cm.exception),
            "'PairwiseAligner' object has no attribute 'no_such_property'",
        )
        with self.assertRaises(AttributeError) as cm:
            aligner.no_such_property = 1
        self.assertEqual(
            str(cm.exception),
            "'PairwiseAligner' object has no attribute 'no_such_property'",
        )


class TestPairwiseGlobal(unittest.TestCase):
    def test_needlemanwunsch_simple1(self):
        seq1 = "GAACT"
        seq2 = "GAT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: 0.000000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: 0.000000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: 0.000000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: 0.000000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: 0.000000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: 0.000000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        self.assertEqual(aligner.algorithm, "Needleman-Wunsch")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), "-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GAACT
||--|
GA--T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 5]], [[0, 2], [2, 3]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GAACT
|-|-|
G-A-T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 1], [2, 3], [4, 5]], [[0, 1], [1, 2], [2, 3]]]),
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GAACT
||--|
GA--T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 5]], [[3, 1], [1, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GAACT
|-|-|
G-A-T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 1], [2, 3], [4, 5]], [[3, 2], [2, 1], [1, 0]]]),
            )
        )

    def test_align_affine1_score(self):
        seq1 = "CC"
        seq2 = "ACCT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 0
        aligner.mismatch_score = -1
        aligner.open_gap_score = -5
        aligner.extend_gap_score = -1
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 0.000000
  mismatch_score: -1.000000
  target_internal_open_gap_score: -5.000000
  target_internal_extend_gap_score: -1.000000
  target_left_open_gap_score: -5.000000
  target_left_extend_gap_score: -1.000000
  target_right_open_gap_score: -5.000000
  target_right_extend_gap_score: -1.000000
  query_internal_open_gap_score: -5.000000
  query_internal_extend_gap_score: -1.000000
  query_left_open_gap_score: -5.000000
  query_left_extend_gap_score: -1.000000
  query_right_open_gap_score: -5.000000
  query_right_extend_gap_score: -1.000000
  mode: global
""",
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, -7.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, -7.0)


class TestPairwiseLocal(unittest.TestCase):
    def test_smithwaterman(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Smith-Waterman")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: -0.100000
  mode: local
""",
        )
        score = aligner.score("AwBw", "zABz")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align("AwBw", "zABz")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
 AwBw
 |-|
zA-Bz
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[1, 2], [2, 3]]])
            )
        )

    def test_gotoh_local(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.open_gap_score = -0.1
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: 0.000000
  mode: local
""",
        )
        score = aligner.score("AwBw", "zABz")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align("AwBw", "zABz")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
 AwBw
 |-|
zA-Bz
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[1, 2], [2, 3]]])
            )
        )


class TestUnknownCharacter(unittest.TestCase):
    def test_needlemanwunsch_simple1(self):
        seq1 = "GACT"
        seq2 = "GA?T"
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.gap_score = -1.0
        aligner.mismatch_score = -1.0
        aligner.wildcard = "?"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GA?T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[0, 4]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GA?T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[4, 0]]]))
        )
        seq2 = "GAXT"
        aligner.wildcard = "X"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GAXT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[0, 4]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GAXT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[4, 0]]]))
        )
        aligner.wildcard = None
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GAXT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[0, 4]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
||.|
GAXT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 4]], [[4, 0]]]))
        )

    def test_needlemanwunsch_simple2(self):
        seq1 = "GA?AT"
        seq2 = "GAA?T"
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.wildcard = "?"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 4.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 4.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 4.0)
        self.assertEqual(
            str(alignment),
            """\
GA?A-T
||-|-|
GA-A?T
""",
        )
        self.assertEqual(alignment.shape, (2, 6))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 5]], [[0, 2], [2, 3], [4, 5]]]),
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 4.0)
        self.assertEqual(
            str(alignment),
            """\
GA?A-T
||-|-|
GA-A?T
""",
        )
        self.assertEqual(alignment.shape, (2, 6))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 5]], [[5, 3], [3, 2], [1, 0]]]),
            )
        )
        seq1 = "GAXAT"
        seq2 = "GAAXT"
        aligner.wildcard = "X"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 4.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 4.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 4.0)
        self.assertEqual(
            str(alignment),
            """\
GAXA-T
||-|-|
GA-AXT
""",
        )
        self.assertEqual(alignment.shape, (2, 6))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 5]], [[0, 2], [2, 3], [4, 5]]]),
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 4.0)
        self.assertEqual(
            str(alignment),
            """\
GAXA-T
||-|-|
GA-AXT
""",
        )
        self.assertEqual(alignment.shape, (2, 6))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 5]], [[5, 3], [3, 2], [1, 0]]]),
            )
        )


class TestPairwiseOpenPenalty(unittest.TestCase):
    def test_match_score_open_penalty1(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 2
        aligner.mismatch_score = -1
        aligner.open_gap_score = -0.1
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 2.000000
  mismatch_score: -1.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        seq1 = "AA"
        seq2 = "A"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.9)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
AA
-|
-A
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[1, 2]], [[0, 1]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
AA
|-
A-
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 1]], [[0, 1]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
AA
-|
-A
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[1, 2]], [[1, 0]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
AA
|-
A-
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 1]], [[1, 0]]]))
        )

    def test_match_score_open_penalty2(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 1.5
        aligner.mismatch_score = 0.0
        aligner.open_gap_score = -0.1
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.500000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        seq1 = "GAA"
        seq2 = "GA"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.9)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.9)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAA
|-|
G-A
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[0, 1], [1, 2]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAA
||-
GA-
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[0, 2]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAA
|-|
G-A
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[2, 1], [1, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAA
||-
GA-
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[2, 0]]]))
        )

    def test_match_score_open_penalty3(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.query_open_gap_score = -0.1
        aligner.query_extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: 0.000000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: 0.000000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: 0.000000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        seq1 = "GAACT"
        seq2 = "GAT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.9)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.9)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAACT
||--|
GA--T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 5]], [[0, 2], [2, 3]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.9)
        self.assertEqual(
            str(alignment),
            """\
GAACT
||--|
GA--T
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 5]], [[3, 1], [1, 0]]])
            )
        )

    def test_match_score_open_penalty4(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.mismatch_score = -2.0
        aligner.open_gap_score = -0.1
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -2.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        seq1 = "GCT"
        seq2 = "GATA"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.7)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.7)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
G-CT-
|--|-
GA-TA
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[0, 1], [2, 3]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
GC-T-
|--|-
G-ATA
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[0, 1], [2, 3]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
G-CT-
|--|-
GA-TA
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[4, 3], [2, 1]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
GC-T-
|--|-
G-ATA
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[4, 3], [2, 1]]])
            )
        )


class TestPairwiseExtendPenalty(unittest.TestCase):
    def test_extend_penalty1(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -0.2
        aligner.extend_gap_score = -0.5
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.200000
  target_internal_extend_gap_score: -0.500000
  target_left_open_gap_score: -0.200000
  target_left_extend_gap_score: -0.500000
  target_right_open_gap_score: -0.200000
  target_right_extend_gap_score: -0.500000
  query_internal_open_gap_score: -0.200000
  query_internal_extend_gap_score: -0.500000
  query_left_open_gap_score: -0.200000
  query_left_extend_gap_score: -0.500000
  query_right_open_gap_score: -0.200000
  query_right_extend_gap_score: -0.500000
  mode: global
""",
        )
        seq1 = "GACT"
        seq2 = "GT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.3)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.3)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.3)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[0, 1], [1, 2]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.3)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[2, 1], [1, 0]]])
            )
        )

    def test_extend_penalty2(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -0.2
        aligner.extend_gap_score = -1.5
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.200000
  target_internal_extend_gap_score: -1.500000
  target_left_open_gap_score: -0.200000
  target_left_extend_gap_score: -1.500000
  target_right_open_gap_score: -0.200000
  target_right_extend_gap_score: -1.500000
  query_internal_open_gap_score: -0.200000
  query_internal_extend_gap_score: -1.500000
  query_left_open_gap_score: -0.200000
  query_left_extend_gap_score: -1.500000
  query_right_open_gap_score: -0.200000
  query_right_extend_gap_score: -1.500000
  mode: global
""",
        )
        seq1 = "GACT"
        seq2 = "GT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 0.6)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 0.6)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 0.6)
        self.assertEqual(
            str(alignment),
            """\
GACT
-.-|
-G-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[1, 2], [3, 4]], [[0, 1], [1, 2]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 0.6)
        self.assertEqual(
            str(alignment),
            """\
GACT
|-.-
G-T-
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[0, 1], [1, 2]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 0.6)
        self.assertEqual(
            str(alignment),
            """\
GACT
-.-|
-G-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[1, 2], [3, 4]], [[2, 1], [1, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 0.6)
        self.assertEqual(
            str(alignment),
            """\
GACT
|-.-
G-T-
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[2, 1], [1, 0]]])
            )
        )


class TestPairwisePenalizeExtendWhenOpening(unittest.TestCase):
    def test_penalize_extend_when_opening(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -1.7
        aligner.extend_gap_score = -1.5
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -1.700000
  target_internal_extend_gap_score: -1.500000
  target_left_open_gap_score: -1.700000
  target_left_extend_gap_score: -1.500000
  target_right_open_gap_score: -1.700000
  target_right_extend_gap_score: -1.500000
  query_internal_open_gap_score: -1.700000
  query_internal_extend_gap_score: -1.500000
  query_left_open_gap_score: -1.700000
  query_left_extend_gap_score: -1.500000
  query_right_open_gap_score: -1.700000
  query_right_extend_gap_score: -1.500000
  mode: global
""",
        )
        seq1 = "GACT"
        seq2 = "GT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, -1.2)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, -1.2)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -1.2)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[0, 1], [1, 2]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -1.2)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[2, 1], [1, 0]]])
            )
        )


class TestPairwisePenalizeEndgaps(unittest.TestCase):
    def test_penalize_end_gaps(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -0.2
        aligner.extend_gap_score = -0.8
        end_score = 0.0
        aligner.target_end_gap_score = end_score
        aligner.query_end_gap_score = end_score
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.200000
  target_internal_extend_gap_score: -0.800000
  target_left_open_gap_score: 0.000000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: 0.000000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.200000
  query_internal_extend_gap_score: -0.800000
  query_left_open_gap_score: 0.000000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: 0.000000
  query_right_extend_gap_score: 0.000000
  mode: global
""",
        )
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        seq1 = "GACT"
        seq2 = "GT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 3)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
--.|
--GT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 4]], [[0, 2]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[0, 1], [1, 2]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
|.--
GT--
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[0, 2]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 3)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
--.|
--GT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 4]], [[2, 0]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
|--|
G--T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [3, 4]], [[2, 1], [1, 0]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, 1.0)
        self.assertEqual(
            str(alignment),
            """\
GACT
|.--
GT--
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[2, 0]]]))
        )


class TestPairwiseSeparateGapPenalties(unittest.TestCase):
    def test_separate_gap_penalties1(self):
        seq1 = "GAT"
        seq2 = "GTCT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        open_score, extend_score = (-0.3, 0)
        aligner.target_open_gap_score = open_score
        aligner.target_extend_gap_score = extend_score
        aligner.target_end_open_gap_score = open_score
        aligner.target_end_extend_gap_score = extend_score
        open_score, extend_score = (-0.8, 0)
        aligner.query_open_gap_score = open_score
        aligner.query_extend_gap_score = extend_score
        aligner.query_end_open_gap_score = open_score
        aligner.query_end_extend_gap_score = extend_score
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.800000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.800000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.800000
  query_right_extend_gap_score: 0.000000
  mode: local
""",
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.7)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.7)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
G-AT
|-.|
GTCT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [1, 3]], [[0, 1], [2, 4]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
GA-T
|.-|
GTCT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [2, 3]], [[0, 2], [3, 4]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
G-AT
|-.|
GTCT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [1, 3]], [[4, 3], [2, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.7)
        self.assertEqual(
            str(alignment),
            """\
GA-T
|.-|
GTCT
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [2, 3]], [[4, 2], [1, 0]]])
            )
        )

    def test_separate_gap_penalties2(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.target_open_gap_score = -0.3
        aligner.target_extend_gap_score = 0.0
        aligner.query_open_gap_score = -0.2
        aligner.query_extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.200000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: -0.200000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: -0.200000
  query_right_extend_gap_score: 0.000000
  mode: local
""",
        )
        seq1 = "GAT"
        seq2 = "GTCT"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.8)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.8)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.8)
        self.assertEqual(
            str(alignment),
            """\
GAT
|-|
G-TCT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[0, 1], [1, 2]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.8)
        self.assertEqual(
            str(alignment),
            """\
GAT
|-|
G-TCT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[4, 3], [3, 2]]])
            )
        )


class TestPairwiseSeparateGapPenaltiesWithExtension(unittest.TestCase):
    def test_separate_gap_penalties_with_extension(self):
        seq1 = "GAAT"
        seq2 = "GTCCT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        open_score, extend_score = (-0.1, 0)
        aligner.target_open_gap_score = open_score
        aligner.target_extend_gap_score = extend_score
        aligner.target_end_open_gap_score = open_score
        aligner.target_end_extend_gap_score = extend_score
        score = -0.1
        aligner.query_gap_score = score
        aligner.query_end_gap_score = score
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.100000
  target_internal_extend_gap_score: 0.000000
  target_left_open_gap_score: -0.100000
  target_left_extend_gap_score: 0.000000
  target_right_open_gap_score: -0.100000
  target_right_extend_gap_score: 0.000000
  query_internal_open_gap_score: -0.100000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.100000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.100000
  query_right_extend_gap_score: -0.100000
  mode: local
""",
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 1.9)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 3)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
G-AAT
|-..|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [1, 4]], [[0, 1], [2, 5]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
GA-AT
|.-.|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [2, 4]], [[0, 2], [3, 5]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
GAA-T
|..-|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 3], [3, 4]], [[0, 3], [4, 5]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 3)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
G-AAT
|-..|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [1, 4]], [[5, 4], [3, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
GA-AT
|.-.|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [2, 4]], [[5, 3], [2, 0]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
GAA-T
|..-|
GTCCT
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 3], [3, 4]], [[5, 2], [1, 0]]])
            )
        )


class TestPairwiseMatchDictionary(unittest.TestCase):

    match_dict = {("A", "A"): 1.5, ("A", "T"): 0.5, ("T", "A"): 0.5, ("T", "T"): 1.0}

    def test_match_dictionary1(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(data=self.match_dict)
        seq1 = "ATAT"
        seq2 = "ATT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -0.5
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -0.500000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -0.500000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -0.500000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -0.500000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -0.500000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -0.500000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||-|
AT-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [3, 4]], [[0, 2], [2, 3]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[3, 0]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||-|
AT-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [3, 4]], [[3, 1], [1, 0]]])
            )
        )

    def test_match_dictionary2(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(data=self.match_dict)
        seq1 = "ATAT"
        seq2 = "ATT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -1.0
        aligner.extend_gap_score = 0.0
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -1.000000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -1.000000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -1.000000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -1.000000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[3, 0]]]))
        )

    def test_match_dictionary3(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(data=self.match_dict)
        seq1 = "ATT"
        seq2 = "ATAT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -1.0
        aligner.extend_gap_score = 0.0
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -1.000000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -1.000000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -1.000000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -1.000000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATT
||.
ATAT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATT
||.
ATAT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[4, 1]]]))
        )

    def test_match_dictionary4(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(alphabet="AT", dims=2)
        self.assertEqual(substitution_matrix.shape, (2, 2))
        substitution_matrix.update(self.match_dict)
        seq1 = "ATAT"
        seq2 = "ATT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -0.5
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -0.500000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -0.500000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -0.500000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -0.500000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -0.500000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -0.500000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||-|
AT-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [3, 4]], [[0, 2], [2, 3]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[3, 0]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||-|
AT-T
""",
        )
        self.assertEqual(alignment.shape, (2, 4))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [3, 4]], [[3, 1], [1, 0]]])
            )
        )

    def test_match_dictionary5(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(alphabet="AT", dims=2)
        self.assertEqual(substitution_matrix.shape, (2, 2))
        substitution_matrix.update(self.match_dict)
        seq1 = "ATAT"
        seq2 = "ATT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -1.0
        aligner.extend_gap_score = 0.0
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -1.000000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -1.000000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -1.000000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -1.000000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATAT
||.
ATT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[3, 0]]]))
        )

    def test_match_dictionary6(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        substitution_matrix = substitution_matrices.Array(alphabet="AT", dims=2)
        self.assertEqual(substitution_matrix.shape, (2, 2))
        substitution_matrix.update(self.match_dict)
        seq1 = "ATT"
        seq2 = "ATAT"
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = substitution_matrix
        aligner.open_gap_score = -1.0
        aligner.extend_gap_score = 0.0
        lines = str(aligner).splitlines()
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], "Pairwise sequence aligner with parameters")
        line = lines[1]
        prefix = "  substitution_matrix: <Array object at "
        suffix = ">"
        self.assertTrue(line.startswith(prefix))
        self.assertTrue(line.endswith(suffix))
        address = int(line[len(prefix) : -len(suffix)], 16)
        self.assertEqual(lines[2], "  target_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[3], "  target_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[4], "  target_left_open_gap_score: -1.000000")
        self.assertEqual(lines[5], "  target_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[6], "  target_right_open_gap_score: -1.000000")
        self.assertEqual(lines[7], "  target_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[8], "  query_internal_open_gap_score: -1.000000")
        self.assertEqual(lines[9], "  query_internal_extend_gap_score: 0.000000")
        self.assertEqual(lines[10], "  query_left_open_gap_score: -1.000000")
        self.assertEqual(lines[11], "  query_left_extend_gap_score: 0.000000")
        self.assertEqual(lines[12], "  query_right_open_gap_score: -1.000000")
        self.assertEqual(lines[13], "  query_right_extend_gap_score: 0.000000")
        self.assertEqual(lines[14], "  mode: local")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATT
||.
ATAT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[0, 3]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ATT
||.
ATAT
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 3]], [[4, 1]]]))
        )


class TestPairwiseOneCharacter(unittest.TestCase):
    def test_align_one_char1(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.open_gap_score = -0.3
        aligner.extend_gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.300000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.300000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.300000
  query_right_extend_gap_score: -0.100000
  mode: local
""",
        )
        score = aligner.score("abcde", "c")
        self.assertAlmostEqual(score, 1)
        alignments = aligner.align("abcde", "c")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1)
        self.assertEqual(
            str(alignment),
            """\
abcde
  |
  c
""",
        )
        self.assertEqual(alignment.shape, (2, 1))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 3]], [[0, 1]]]))
        )

    def test_align_one_char2(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.open_gap_score = -0.3
        aligner.extend_gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.300000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.300000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.300000
  query_right_extend_gap_score: -0.100000
  mode: local
""",
        )
        score = aligner.score("abcce", "c")
        self.assertAlmostEqual(score, 1)
        alignments = aligner.align("abcce", "c")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1)
        self.assertEqual(
            str(alignment),
            """\
abcce
  |
  c
""",
        )
        self.assertEqual(alignment.shape, (2, 1))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 3]], [[0, 1]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 1)
        self.assertEqual(
            str(alignment),
            """\
abcce
   |
   c
""",
        )
        self.assertEqual(alignment.shape, (2, 1))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[3, 4]], [[0, 1]]]))
        )

    def test_align_one_char3(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -0.3
        aligner.extend_gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.300000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.300000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.300000
  query_right_extend_gap_score: -0.100000
  mode: global
""",
        )
        seq1 = "abcde"
        seq2 = "c"
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 0.2)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 0.2)
        self.assertEqual(
            str(alignment),
            """\
abcde
--|--
--c--
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 3]], [[0, 1]]]))
        )

    def test_align_one_char_score3(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -0.3
        aligner.extend_gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.300000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.300000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.300000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.300000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.300000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.300000
  query_right_extend_gap_score: -0.100000
  mode: global
""",
        )
        score = aligner.score("abcde", "c")
        self.assertAlmostEqual(score, 0.2)


class TestPerSiteGapPenalties(unittest.TestCase):
    """Check gap penalty callbacks use correct gap opening position.

    This tests that the gap penalty callbacks are really being used
    with the correct gap opening position.
    """

    def test_gap_here_only_1(self):
        seq1 = "AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA"
        seq2 = "AABBBAAAACCCCAAAABBBAA"
        breaks = [0, 11, len(seq2)]

        # Very expensive to open a gap in seq1:
        def nogaps(x, y):
            return -2000 - y

        # Very expensive to open a gap in seq2 unless it is in one of the allowed positions:
        def specificgaps(x, y):
            if x in breaks:
                return -2 - y
            else:
                return -2000 - y

        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.target_gap_score = nogaps
        aligner.query_gap_score = specificgaps
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -1.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: global
"""
            % (nogaps, specificgaps),
        )
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer global alignment algorithm"
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
--|||||||||||----------|||||||||||--
--AABBBAAAACC----------CCAAAABBBAA--
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[2, 13], [23, 34]], [[0, 11], [11, 22]]]),
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
--|||||||||||----------|||||||||||--
--AABBBAAAACC----------CCAAAABBBAA--
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[2, 13], [23, 34]], [[22, 11], [11, 0]]]),
            )
        )

    def test_gap_here_only_2(self):
        # Force a bad alignment.
        #
        # Forces a bad alignment by having a very expensive gap penalty
        # where one would normally expect a gap, and a cheap gap penalty
        # in another place.
        seq1 = "AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA"
        seq2 = "AABBBAAAACCCCAAAABBBAA"
        breaks = [0, 3, len(seq2)]

        # Very expensive to open a gap in seq1:
        def nogaps(x, y):
            return -2000 - y

        # Very expensive to open a gap in seq2 unless it is in one of the allowed positions:
        def specificgaps(x, y):
            if x in breaks:
                return -2 - y
            else:
                return -2000 - y

        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.target_gap_score = nogaps
        aligner.query_gap_score = specificgaps
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -1.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: global
"""
            % (nogaps, specificgaps),
        )
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer global alignment algorithm"
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, -10)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, -10)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -10)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
--|||----------......|||||||||||||--
--AAB----------BBAAAACCCCAAAABBBAA--
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[2, 5], [15, 34]], [[0, 3], [3, 22]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, -10)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
||.------------......|||||||||||||--
AAB------------BBAAAACCCCAAAABBBAA--
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 3], [15, 34]], [[0, 3], [3, 22]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -10)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
--|||||||||||||......------------.||
--AABBBAAAACCCCAAAABB------------BAA
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[2, 21], [33, 36]], [[22, 3], [3, 0]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, -10)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
--|||||||||||||......----------|||--
--AABBBAAAACCCCAAAABB----------BAA--
""",
        )
        self.assertEqual(alignment.shape, (2, 36))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[2, 21], [31, 34]], [[22, 3], [3, 0]]])
            )
        )

    def test_gap_here_only_3(self):
        # Check if gap open and gap extend penalties are handled correctly.
        seq1 = "TTCCAA"
        seq2 = "TTGGAA"

        def gap_score(i, n):
            if i == 3:
                return -10
            if n == 1:
                return -1
            return -10

        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = 1
        aligner.mismatch_score = -10
        aligner.target_gap_score = gap_score
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer global alignment algorithm"
        )
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -10.000000
  target_gap_function: %s
  query_internal_open_gap_score: 0.000000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: 0.000000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: 0.000000
  query_right_extend_gap_score: 0.000000
  mode: global
"""
            % gap_score,
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CC-AA
||----||
TTG--GAA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[0, 2], [4, 6]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CC-AA
||----||
TTG--GAA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[6, 4], [2, 0]]])
            )
        )
        aligner.query_gap_score = gap_score
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -10.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: global
"""
            % (gap_score, gap_score),
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, -8.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, -8.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 4)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CCAA
||-.-||
TTGG-AA
""",
        )
        self.assertEqual(alignment.shape, (2, 7))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [2, 3], [4, 6]], [[0, 2], [3, 4], [4, 6]]]),
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TTC--CAA
||----||
TT-GG-AA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[0, 2], [4, 6]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TTCC-AA
||-.-||
TT-GGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 7))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 6]], [[0, 2], [2, 3], [4, 6]]]),
            )
        )
        alignment = alignments[3]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CC-AA
||----||
TTG--GAA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[0, 2], [4, 6]]])
            )
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 4)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CCAA
||-.-||
TTGG-AA
""",
        )
        self.assertEqual(alignment.shape, (2, 7))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [2, 3], [4, 6]], [[6, 4], [3, 2], [2, 0]]]),
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TTC--CAA
||----||
TT-GG-AA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[6, 4], [2, 0]]])
            )
        )
        alignment = alignments[2]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TTCC-AA
||-.-||
TT-GGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 7))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 2], [3, 4], [4, 6]], [[6, 4], [4, 3], [2, 0]]]),
            ),
        )
        alignment = alignments[3]
        self.assertAlmostEqual(alignment.score, -8.0)
        self.assertEqual(
            str(alignment),
            """\
TT-CC-AA
||----||
TTG--GAA
""",
        )
        self.assertEqual(alignment.shape, (2, 8))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 6]], [[6, 4], [2, 0]]])
            )
        )

    def test_gap_here_only_local_1(self):
        seq1 = "AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA"
        seq2 = "AABBBAAAACCCCAAAABBBAA"
        breaks = [0, 11, len(seq2)]

        # Very expensive to open a gap in seq1:
        def nogaps(x, y):
            return -2000 - y

        # Very expensive to open a gap in seq2 unless it is in one of the allowed positions:
        def specificgaps(x, y):
            if x in breaks:
                return -2 - y
            else:
                return -2000 - y

        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.target_gap_score = nogaps
        aligner.query_gap_score = specificgaps
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer local alignment algorithm"
        )
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -1.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: local
"""
            % (nogaps, specificgaps),
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 13)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 13)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
  |||||||||||||
  AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 15]], [[0, 13]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
                     |||||||||||||
            AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[21, 34]], [[9, 22]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
  |||||||||||||
  AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 15]], [[22, 9]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
                     |||||||||||||
            AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[21, 34]], [[13, 0]]]))
        )

    def test_gap_here_only_local_2(self):
        # Force a bad alignment.
        #
        # Forces a bad alignment by having a very expensive gap penalty
        # where one would normally expect a gap, and a cheap gap penalty
        # in another place.
        seq1 = "AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA"
        seq2 = "AABBBAAAACCCCAAAABBBAA"
        breaks = [0, 3, len(seq2)]

        # Very expensive to open a gap in seq1:
        def nogaps(x, y):
            return -2000 - y

        # Very expensive to open a gap in seq2 unless it is in one of the allowed positions:
        def specificgaps(x, y):
            if x in breaks:
                return -2 - y
            else:
                return -2000 - y

        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.target_gap_score = nogaps
        aligner.query_gap_score = specificgaps
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -1.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: local
"""
            % (nogaps, specificgaps),
        )
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer local alignment algorithm"
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 13)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 13)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
  |||||||||||||
  AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 15]], [[0, 13]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
                     |||||||||||||
            AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[21, 34]], [[9, 22]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
  |||||||||||||
  AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[2, 15]], [[22, 9]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 13)
        self.assertEqual(
            str(alignment),
            """\
AAAABBBAAAACCCCCCCCCCCCCCAAAABBBAAAA
                     |||||||||||||
            AABBBAAAACCCCAAAABBBAA
""",
        )
        self.assertEqual(alignment.shape, (2, 13))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[21, 34]], [[13, 0]]]))
        )

    def test_gap_here_only_local_3(self):
        # Check if gap open and gap extend penalties are handled correctly.
        seq1 = "TTCCAA"
        seq2 = "TTGGAA"

        def gap_score(i, n):
            if i == 3:
                return -10
            if n == 1:
                return -1
            return -10

        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.match_score = 1
        aligner.mismatch_score = -10
        aligner.target_gap_score = gap_score
        self.assertEqual(
            aligner.algorithm, "Waterman-Smith-Beyer local alignment algorithm"
        )
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -10.000000
  target_gap_function: %s
  query_internal_open_gap_score: 0.000000
  query_internal_extend_gap_score: 0.000000
  query_left_open_gap_score: 0.000000
  query_left_extend_gap_score: 0.000000
  query_right_open_gap_score: 0.000000
  query_right_extend_gap_score: 0.000000
  mode: local
"""
            % gap_score,
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[0, 2]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
    ||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[4, 6]], [[4, 6]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[6, 4]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
    ||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[4, 6]], [[2, 0]]]))
        )
        aligner.query_gap_score = gap_score
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: -10.000000
  target_gap_function: %s
  query_gap_function: %s
  mode: local
"""
            % (gap_score, gap_score),
        )
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 2.0)
        score = aligner.score(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(score, 2.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[0, 2]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
    ||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[4, 6]], [[4, 6]]]))
        )
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[0, 2]], [[6, 4]]]))
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 2.0)
        self.assertEqual(
            str(alignment),
            """\
TTCCAA
    ||
TTGGAA
""",
        )
        self.assertEqual(alignment.shape, (2, 2))
        self.assertTrue(
            numpy.array_equal(alignment.aligned, numpy.array([[[4, 6]], [[2, 0]]]))
        )

    def test_broken_gap_function(self):
        # Check if an Exception is propagated if the gap function raises one
        seq1 = "TTCCAA"
        seq2 = "TTGGAA"

        def gap_score(i, n):
            raise RuntimeError("broken gap function")

        aligner = Align.PairwiseAligner()
        aligner.target_gap_score = gap_score
        aligner.query_gap_score = -1
        aligner.mode = "global"
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, seq2)
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, reverse_complement(seq2), strand="-")
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, seq2)
            alignments = list(alignments)
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
            alignments = list(alignments)
        aligner.mode = "local"
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, seq2)
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, reverse_complement(seq2), strand="-")
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, seq2)
            alignments = list(alignments)
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
            alignments = list(alignments)
        aligner.target_gap_score = -1
        aligner.query_gap_score = gap_score
        aligner.mode = "global"
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, seq2)
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, reverse_complement(seq2), strand="-")
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, seq2)
            alignments = list(alignments)
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
            alignments = list(alignments)
        aligner.mode = "local"
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, seq2)
        with self.assertRaises(RuntimeError):
            aligner.score(seq1, reverse_complement(seq2), strand="-")
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, seq2)
            alignments = list(alignments)
        with self.assertRaises(RuntimeError):
            alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
            alignments = list(alignments)


class TestSequencesAsLists(unittest.TestCase):
    """Check aligning sequences provided as lists.

    This tests whether we can align sequences that are provided as lists
    consisting of three-letter codons or three-letter amino acids.
    """

    def test_three_letter_amino_acids_global(self):
        seq1 = ["Gly", "Ala", "Thr"]
        seq2 = ["Gly", "Ala", "Ala", "Cys", "Thr"]
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        # fmt: off
        aligner.alphabet = [
            "Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile",
            "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val",
        ]
        # fmt: on
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        self.assertEqual(
            str(alignments[0]),
            """\
Gly Ala --- --- Thr
||| ||| --- --- |||
Gly Ala Ala Cys Thr
""",
        )
        self.assertEqual(
            str(alignments[1]),
            """\
Gly --- Ala --- Thr
||| --- ||| --- |||
Gly Ala Ala Cys Thr
""",
        )
        self.assertAlmostEqual(alignments[0].score, 3.0)
        self.assertAlmostEqual(alignments[1].score, 3.0)

        seq1 = ["Pro", "Pro", "Gly", "Ala", "Thr"]
        seq2 = ["Gly", "Ala", "Ala", "Cys", "Thr", "Asn", "Asn"]
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        self.assertEqual(
            str(alignments[0]),
            """\
Pro Pro Gly Ala --- --- Thr --- ---
--- --- ||| ||| --- --- ||| --- ---
--- --- Gly Ala Ala Cys Thr Asn Asn
""",
        )
        self.assertEqual(
            str(alignments[1]),
            """\
Pro Pro Gly --- Ala --- Thr --- ---
--- --- ||| --- ||| --- ||| --- ---
--- --- Gly Ala Ala Cys Thr Asn Asn
""",
        )
        self.assertAlmostEqual(alignments[0].score, 3.0)
        self.assertAlmostEqual(alignments[1].score, 3.0)

    def test_three_letter_amino_acids_local(self):
        seq1 = ["Asn", "Asn", "Gly", "Ala", "Thr", "Glu", "Glu"]
        seq2 = ["Pro", "Pro", "Gly", "Ala", "Ala", "Cys", "Thr", "Leu"]
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        # fmt: off
        aligner.alphabet = [
            "Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile",
            "Leu", "Lys", "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val",
        ]
        # fmt: on
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        self.assertEqual(
            str(alignments[0]),
            """\
Gly Ala --- --- Thr
||| ||| --- --- |||
Gly Ala Ala Cys Thr
""",
        )
        self.assertEqual(
            str(alignments[1]),
            """\
Gly --- Ala --- Thr
||| --- ||| --- |||
Gly Ala Ala Cys Thr
""",
        )
        self.assertAlmostEqual(alignments[0].score, 3.0)
        self.assertAlmostEqual(alignments[1].score, 3.0)


class TestArgumentErrors(unittest.TestCase):
    def test_aligner_string_errors(self):
        aligner = Align.PairwiseAligner()
        message = "^argument should support the sequence protocol$"
        with self.assertRaisesRegex(TypeError, message):
            aligner.score("AAA", 3)
        message = "^sequence has zero length$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score("AAA", "")
        with self.assertRaisesRegex(ValueError, message):
            aligner.score("AAA", "", strand="-")
        message = "^sequence contains letters not in the alphabet$"
        aligner.alphabet = "ABCD"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score("AAA", "AAE")

    def test_aligner_array_errors(self):
        aligner = Align.PairwiseAligner()
        s1 = "GGG"
        s2 = array.array("i", [ord("G"), ord("A"), ord("G")])
        score = aligner.score(s1, s2)
        self.assertAlmostEqual(score, 2.0)
        s2 = array.array("f", [1.0, 0.0, 1.0])
        message = "^sequence has incorrect data type 'f'$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2)
        aligner.wildcard = chr(99)
        s1 = array.array("i", [1, 5, 6])
        s2 = array.array("i", [1, 8, 6])
        s2a = array.array("i", [1, 8, 99])
        s2b = array.array("i", [1, 28, 6])
        aligner.match = 3.0
        aligner.mismatch = -2.0
        aligner.gap_score = -10.0
        score = aligner.score(s1, s2)
        self.assertAlmostEqual(score, 4.0)
        # the following two are valid as we are using match/mismatch scores
        # instead of a substitution matrix:
        score = aligner.score(s1, s2a)
        # since we set the wildcard character to chr(99), the number 99
        # is interpreted as an unknown character, and gets a zero score:
        self.assertAlmostEqual(score, 1.0)
        score = aligner.score(s1, s2b)
        self.assertAlmostEqual(score, 4.0)
        try:
            import numpy
        except ImportError:
            return
        aligner = Align.PairwiseAligner()
        aligner.wildcard = chr(99)
        s1 = "GGG"
        s2 = numpy.array([ord("G"), ord("A"), ord("G")], numpy.int32)
        score = aligner.score(s1, s2)
        self.assertAlmostEqual(score, 2.0)
        s2 = numpy.array([1.0, 0.0, 1.0])
        message = "^sequence has incorrect data type 'd'$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2)
        s2 = numpy.zeros((3, 2), numpy.int32)
        message = "^sequence has incorrect rank \\(2 expected 1\\)$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2)
        s1 = numpy.array([1, 5, 6], numpy.int32)
        s2 = numpy.array([1, 8, 6], numpy.int32)
        s2a = numpy.array([1, 8, 99], numpy.int32)
        s2b = numpy.array([1, 28, 6], numpy.int32)
        s2c = numpy.array([1, 8, -6], numpy.int32)
        aligner.match = 3.0
        aligner.mismatch = -2.0
        aligner.gap_score = -10.0
        score = aligner.score(s1, s2)
        self.assertAlmostEqual(score, 4.0)
        # the following two are valid as we are using match/mismatch scores
        # instead of a substitution matrix:
        score = aligner.score(s1, s2a)
        self.assertAlmostEqual(score, 1.0)
        score = aligner.score(s1, s2b)
        self.assertAlmostEqual(score, 4.0)
        # when using a substitution matrix, all indices should be between 0
        # and the size of the substitution matrix:
        m = 5 * numpy.eye(10)
        aligner.substitution_matrix = m
        score = aligner.score(s1, s2)  # no ValueError
        self.assertAlmostEqual(score, 10.0)
        message = "^sequence item 2 is negative \\(-6\\)$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2c)
        message = "^sequence item 1 is out of bound \\(28, should be < 10\\)$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2b)
        # note that the wildcard character is ignored when using a substitution
        # matrix, so 99 is interpreted as an index here:
        message = "^sequence item 2 is out of bound \\(99, should be < 10\\)$"
        with self.assertRaisesRegex(ValueError, message):
            aligner.score(s1, s2a)


class TestOverflowError(unittest.TestCase):
    def test_align_overflow_error(self):
        aligner = Align.PairwiseAligner()
        path = os.path.join("Align", "bsubtilis.fa")
        record = SeqIO.read(path, "fasta")
        seq1 = record.seq
        path = os.path.join("Align", "ecoli.fa")
        record = SeqIO.read(path, "fasta")
        seq2 = record.seq
        alignments = aligner.align(seq1, seq2)
        self.assertAlmostEqual(alignments.score, 1286.0)
        message = "^number of optimal alignments is larger than (%d|%d)$" % (
            2147483647,  # on 32-bit systems
            9223372036854775807,
        )  # on 64-bit systems
        with self.assertRaisesRegex(OverflowError, message):
            n = len(alignments)
        # confirm that we can still pull out individual alignments
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
ATTTA-TC-GGA-GAGTTTGATCC-TGGCTCAGGAC--GAACGCTGGCGGC-GTGCCTAAT-ACATGCAAGTCGAG-CGG-A-CAG-AT-GGGA-GCTTGCT-C----CCTGAT-GTTAGC-GGCGGACGGGTGAGTAACAC-GT--GGGTAA-CCTGCCTGTAA-G-ACTGGG--ATAACT-CC-GGGAAACCGG--GGCTAATACCGG-ATGGTTGTTTGAACCGCAT-GGTTCAA-AC-ATAA-AAGGTGG--C-TTCGG-C-TACCACTTA-C-A--G-ATG-GACCC-GC--GGCGCATTAGCTAGTT-GGTGAGG-TAACGGCTCACC-AAGGCGACGATGCG--TAGCC-GA--CCTGAGAGGG-TGATC--GGCCACACTGGGA-CTGAGACACGG-CCCAGACTCCTACGGGAGGCAGCAGTAGGG-AATC-TTCCGCA-A-TGGA-CG-AAAGTC-TGAC-GG-AGCAAC--GCCGCGTG-AGTGAT-GAAGG--TTTTCGGA-TC-GTAAAGCT-CTGTTGTT-AG-GG--A--A-G--A--ACAAGTGCCGTTCGAATAGGGC----GG-TACC-TTGACGGT-ACCTAAC-CAGAA-A-GCCAC-GGCTAACTAC-GTGCCAGCAGCCGCGGTAATACGT-AGG-TGGCAAGCGTTG--TCCGGAATTA-TTGGGCGTAAAG-GGCT-CGCAGGCGGTTTC-TTAAGTCT-GATGTGAAAG-CCCCCGG-CTCAACC-GGGGAGGG--T-CAT-TGGA-AACTGGGG-AA-CTTGAGTGCA--G-AAGAGGAGAGTGG-A-A-TTCCACG-TGTAGCGGTGAAATGCGTAGAGATG-TGGAGGAAC-ACCAG-TGGCGAAGGCGA-CTCTC--TGGT-CTGTAA--CTGACGCTG-AGGA-GCGAAAGCGTGGGGAGCGAA-CAGGATTAGATACCCTGGTAGTCCACGCCGTAAACGATGAGT-G-CTAAGTGTT-AGGGGGTT-TCCGCCCCTT-AGTGC-TG-C------AGCTAACGCA-TTAAG-C-ACTCCGCCTGGGGAGTACGGTC-GCAAGACTG--AAA-CTCAAA-GGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGAA-GCAACGCGAAGAACCTTACCA-GGTCTTGACATCCTCTGACA-A--T--CCTAGAGATAGGAC--G-T-CCCCTTCGGGGGCAGA--GTGA--CAGGTGG-TGCATGG-TTGTCGTCAGCTCGTGTC-GTGAGA-TGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGATCTTA--GTTGCCAGCA--TTCA-GTTG--GGC-A-CTCTAA-GGT-GACTGCC-GGTGAC-AAACC-GGAGGAAGGTGGGGATGACGTCAAA-TCATCATG-CCCCTTAT-GACCT-GGGCTACACACGTGCTACAATGGACAG-A-ACAAAG-GGCA-GCGAAACC--GCGAG-GTT-AAGCC--AATCC-CAC-AAA-T-CTGTTC-TCAGTTC-GGATC-GC-AGTCTGCAACTCGACTGCG--TGAAGCT-GGAATCGCTAGTAATCGC-GGATCAGCA-TGCCG-CGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCAC-GAG-AGT---TTGT-AACACCC-GAAGTC-GGTGAGG-T-AACCTTTTA-GG-AG--C-C--AGCCG-CC---GAAGGTGGGA--CAGATGA-TTGGGGTGAAGTCGTAACAAGGTAG-CCGTATCGGAAGG----TGCGGCT-GGATCACCTCCTTTCTA
|---|-|--|-|-||||||||||--||||||||-|---|||||||||||||-|-||||||--|||||||||||||--|||-|-|||-|--|--|-|||||||-|----|-|||--|--||--|||||||||||||||||----||--|||-||-|-||||||-|--|-|--|||--||||||-|--||-||||-||--|-|||||||||--||---------|||-|--|-|---|||-||-|-||-|-||-||--|-|||||-|-|-|---||--|-|--|-|||-|-|||-|---||-|-||||||||||--||||-||-||||||||||||-|-|||||||||-|---||||--|---|-|||||||--|||-|--|-|||||||||-|-|||||||||||-||-|||||||||||||||||||||||-|||-|||--||--|||-|-|||--||-||-|-|-|||--|--|||--|--||||||||-|-|||--|||||--||--|||--|--||||||-|-||-||----||-||--|--|-|--|--|-||||----|---||||---|----|--|-|--||||||-|-|||---|-|||||-|-||-||-||||||||-|-|||||||||||||||||||||||--|||-||-||||||||---||-|||||||-|-||||||||||-|-|--||||||||||||--|||||||--|||||||||--||||-||-|||||||-|||-|-----|-|||-||-|-|-||||---||-|||||||-|---|-|-||||-|-|-||-|-|-|||||-|-||||||||||||||||||||||||--||||||||--|||-|-|||||||||||--|-|-|--|||--|-|-||--||||||||--|||--|||||||||||||||||-||-|||||||||||||||||||||||||||||||||||||||--|-|-||---||---|||---||-|--||||-||-||-||-||-|------|||||||||--|||||-|-||-|-|||||||||||||||-|-|||||---|--|||-||||||-|-|||||||||||||||||||||||||||||||||||||||||||||||--||||||||||||||||||||--|||||||||||||----|||-|--|--||-||||||-|||---|-|-||--||||||---|-|--||||--||||||--|||||||-|-|||||||||||||||--||||-|-||||||||||||||||||||||||||||||||||-|||||---|||||||||---|-|--|--|--||--|-|||-||-||--|||||||-|-|||--||||--||||||||||||||||||||||||--||||||||-|||-|||--||||--|||||||||||||||||||||||-|-|-|-||||||-|--|-||||--||--|||||-|---||||---|--||-||--|||-|-|-||-|-|-|||-|-||||--|--||||||||||||||||-|---|||||-|-|||||||||||||||||--|||||||-|-||||--|||||||||||||||||||||||||||||||||||||||||||||--|-|-|||---|||--||-|----|||||--|||-||--|-||||||----||-||--|-|--|-||--|----|----||--|--||--|||-|-||||||||||||||||||||||--|||||--||--||----|||||-|-|||||||||||||---|
A---AAT-TG-AAGAGTTTGATC-ATGGCTCAG-A-TTGAACGCTGGCGGCAG-GCCTAA-CACATGCAAGTCGA-ACGGTAACAGGA-AG--AAGCTTGCTTCTTTGC-TGA-CG--AG-TGGCGGACGGGTGAGTAA---TGTCTGGG-AAAC-TGCCTG-A-TGGA--GGGGGATAACTAC-TGG-AAAC-GGTAG-CTAATACCG-CAT---------AAC-G--TCG---CAAGACCA-AAGA-GG-GGGACCTTCGGGCCT-C---TT-GCCATCGGATGTG-CCCAG-ATGG-G-ATTAGCTAGT-AGGTG-GGGTAACGGCTCACCTA-GGCGACGAT-C-CCTAGC-TG-GTC-TGAGAGG-ATGA-CCAG-CCACACTGG-AACTGAGACACGGTCC-AGACTCCTACGGGAGGCAGCAGT-GGGGAAT-ATT--GCACAATGG-GCGCAA-G-CCTGA-TG-CAGC--CATGCCGCGTGTA-TGA-AGAAGGCCTT--CGG-GT-TGTAAAG-TACT-TT---CAGCGGGGAGGAAGGGAGTA-AAGT----T---AATA---CCTTTG-CT-C-ATTGACG-TTACC---CGCAGAAGAAGC-ACCGGCTAACT-CCGTGCCAGCAGCCGCGGTAATACG-GAGGGTG-CAAGCGTT-AATC-GGAATTACT-GGGCGTAAAGCG-C-ACGCAGGCGGTTT-GTTAAGTC-AGATGTGAAA-TCCCC-GGGCTCAACCTGGG-A---ACTGCATCTG-ATA-CTGG--CAAGCTTGAGT-C-TCGTA-GAGG-G-G-GGTAGAATTCCA-GGTGTAGCGGTGAAATGCGTAGAGAT-CTGGAGGAA-TACC-GGTGGCGAAGGCG-GC-C-CCCTGG-AC-G-AAGACTGACGCT-CAGG-TGCGAAAGCGTGGGGAGC-AAACAGGATTAGATACCCTGGTAGTCCACGCCGTAAACGATG--TCGACT---TG--GAGG---TTGT--GCCC-TTGAG-GCGTGGCTTCCGGAGCTAACGC-GTTAAGTCGAC-C-GCCTGGGGAGTACGG-CCGCAAG---GTTAAAACTCAAATG-AATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGA-TGCAACGCGAAGAACCTTACC-TGGTCTTGACATCC----ACAGAACTTTCC-AGAGAT-GGA-TTGGTGCC--TTCGGG---A-ACTGTGAGACAGGTG-CTGCATGGCT-GTCGTCAGCTCGTGT-TGTGA-AATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTT-ATCTT-TTGTTGCCAGC-GGT-C-CG--GCCGG-GAACTC-AAAGG-AGACTGCCAG-TGA-TAAAC-TGGAGGAAGGTGGGGATGACGTCAA-GTCATCATGGCCC-TTA-CGACC-AGGGCTACACACGTGCTACAATGG-C-GCATACAAAGAG--AAGCGA--CCTCGCGAGAG--CAAGC-GGA--CCTCA-TAAAGTGC-GT-CGT-AGT-CCGGAT-TG-GAGTCTGCAACTCGACT-C-CATGAAG-TCGGAATCGCTAGTAATCG-TGGATCAG-AATGCC-ACGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCA-TG-GGAGTGGGTTG-CAA-A---AGAAGT-AGGT-AG-CTTAACCTT---CGGGAGGGCGCTTA-CC-AC-TTTG----TG--ATTCA--TGACT-GGGGTGAAGTCGTAACAAGGTA-ACCGTA--GG--GGAACCTGCGG-TTGGATCACCTCCTT---A
""",
        )
        self.assertEqual(alignment.shape, (2, 1811))
        self.assertAlmostEqual(alignment.score, 1286.0)
        alignments = aligner.align(seq1, reverse_complement(seq2), strand="-")
        self.assertAlmostEqual(alignments.score, 1286.0)
        message = "^number of optimal alignments is larger than (%d|%d)$" % (
            2147483647,  # on 32-bit systems
            9223372036854775807,
        )  # on 64-bit systems
        with self.assertRaisesRegex(OverflowError, message):
            n = len(alignments)
        # confirm that we can still pull out individual alignments
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
ATTTA-TC-GGA-GAGTTTGATCC-TGGCTCAGGAC--GAACGCTGGCGGC-GTGCCTAAT-ACATGCAAGTCGAG-CGG-A-CAG-AT-GGGA-GCTTGCT-C----CCTGAT-GTTAGC-GGCGGACGGGTGAGTAACAC-GT--GGGTAA-CCTGCCTGTAA-G-ACTGGG--ATAACT-CC-GGGAAACCGG--GGCTAATACCGG-ATGGTTGTTTGAACCGCAT-GGTTCAA-AC-ATAA-AAGGTGG--C-TTCGG-C-TACCACTTA-C-A--G-ATG-GACCC-GC--GGCGCATTAGCTAGTT-GGTGAGG-TAACGGCTCACC-AAGGCGACGATGCG--TAGCC-GA--CCTGAGAGGG-TGATC--GGCCACACTGGGA-CTGAGACACGG-CCCAGACTCCTACGGGAGGCAGCAGTAGGG-AATC-TTCCGCA-A-TGGA-CG-AAAGTC-TGAC-GG-AGCAAC--GCCGCGTG-AGTGAT-GAAGG--TTTTCGGA-TC-GTAAAGCT-CTGTTGTT-AG-GG--A--A-G--A--ACAAGTGCCGTTCGAATAGGGC----GG-TACC-TTGACGGT-ACCTAAC-CAGAA-A-GCCAC-GGCTAACTAC-GTGCCAGCAGCCGCGGTAATACGT-AGG-TGGCAAGCGTTG--TCCGGAATTA-TTGGGCGTAAAG-GGCT-CGCAGGCGGTTTC-TTAAGTCT-GATGTGAAAG-CCCCCGG-CTCAACC-GGGGAGGG--T-CAT-TGGA-AACTGGGG-AA-CTTGAGTGCA--G-AAGAGGAGAGTGG-A-A-TTCCACG-TGTAGCGGTGAAATGCGTAGAGATG-TGGAGGAAC-ACCAG-TGGCGAAGGCGA-CTCTC--TGGT-CTGTAA--CTGACGCTG-AGGA-GCGAAAGCGTGGGGAGCGAA-CAGGATTAGATACCCTGGTAGTCCACGCCGTAAACGATGAGT-G-CTAAGTGTT-AGGGGGTT-TCCGCCCCTT-AGTGC-TG-C------AGCTAACGCA-TTAAG-C-ACTCCGCCTGGGGAGTACGGTC-GCAAGACTG--AAA-CTCAAA-GGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGAA-GCAACGCGAAGAACCTTACCA-GGTCTTGACATCCTCTGACA-A--T--CCTAGAGATAGGAC--G-T-CCCCTTCGGGGGCAGA--GTGA--CAGGTGG-TGCATGG-TTGTCGTCAGCTCGTGTC-GTGAGA-TGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGATCTTA--GTTGCCAGCA--TTCA-GTTG--GGC-A-CTCTAA-GGT-GACTGCC-GGTGAC-AAACC-GGAGGAAGGTGGGGATGACGTCAAA-TCATCATG-CCCCTTAT-GACCT-GGGCTACACACGTGCTACAATGGACAG-A-ACAAAG-GGCA-GCGAAACC--GCGAG-GTT-AAGCC--AATCC-CAC-AAA-T-CTGTTC-TCAGTTC-GGATC-GC-AGTCTGCAACTCGACTGCG--TGAAGCT-GGAATCGCTAGTAATCGC-GGATCAGCA-TGCCG-CGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCAC-GAG-AGT---TTGT-AACACCC-GAAGTC-GGTGAGG-T-AACCTTTTA-GG-AG--C-C--AGCCG-CC---GAAGGTGGGA--CAGATGA-TTGGGGTGAAGTCGTAACAAGGTAG-CCGTATCGGAAGG----TGCGGCT-GGATCACCTCCTTTCTA
|---|-|--|-|-||||||||||--||||||||-|---|||||||||||||-|-||||||--|||||||||||||--|||-|-|||-|--|--|-|||||||-|----|-|||--|--||--|||||||||||||||||----||--|||-||-|-||||||-|--|-|--|||--||||||-|--||-||||-||--|-|||||||||--||---------|||-|--|-|---|||-||-|-||-|-||-||--|-|||||-|-|-|---||--|-|--|-|||-|-|||-|---||-|-||||||||||--||||-||-||||||||||||-|-|||||||||-|---||||--|---|-|||||||--|||-|--|-|||||||||-|-|||||||||||-||-|||||||||||||||||||||||-|||-|||--||--|||-|-|||--||-||-|-|-|||--|--|||--|--||||||||-|-|||--|||||--||--|||--|--||||||-|-||-||----||-||--|--|-|--|--|-||||----|---||||---|----|--|-|--||||||-|-|||---|-|||||-|-||-||-||||||||-|-|||||||||||||||||||||||--|||-||-||||||||---||-|||||||-|-||||||||||-|-|--||||||||||||--|||||||--|||||||||--||||-||-|||||||-|||-|-----|-|||-||-|-|-||||---||-|||||||-|---|-|-||||-|-|-||-|-|-|||||-|-||||||||||||||||||||||||--||||||||--|||-|-|||||||||||--|-|-|--|||--|-|-||--||||||||--|||--|||||||||||||||||-||-|||||||||||||||||||||||||||||||||||||||--|-|-||---||---|||---||-|--||||-||-||-||-||-|------|||||||||--|||||-|-||-|-|||||||||||||||-|-|||||---|--|||-||||||-|-|||||||||||||||||||||||||||||||||||||||||||||||--||||||||||||||||||||--|||||||||||||----|||-|--|--||-||||||-|||---|-|-||--||||||---|-|--||||--||||||--|||||||-|-|||||||||||||||--||||-|-||||||||||||||||||||||||||||||||||-|||||---|||||||||---|-|--|--|--||--|-|||-||-||--|||||||-|-|||--||||--||||||||||||||||||||||||--||||||||-|||-|||--||||--|||||||||||||||||||||||-|-|-|-||||||-|--|-||||--||--|||||-|---||||---|--||-||--|||-|-|-||-|-|-|||-|-||||--|--||||||||||||||||-|---|||||-|-|||||||||||||||||--|||||||-|-||||--|||||||||||||||||||||||||||||||||||||||||||||--|-|-|||---|||--||-|----|||||--|||-||--|-||||||----||-||--|-|--|-||--|----|----||--|--||--|||-|-||||||||||||||||||||||--|||||--||--||----|||||-|-|||||||||||||---|
A---AAT-TG-AAGAGTTTGATC-ATGGCTCAG-A-TTGAACGCTGGCGGCAG-GCCTAA-CACATGCAAGTCGA-ACGGTAACAGGA-AG--AAGCTTGCTTCTTTGC-TGA-CG--AG-TGGCGGACGGGTGAGTAA---TGTCTGGG-AAAC-TGCCTG-A-TGGA--GGGGGATAACTAC-TGG-AAAC-GGTAG-CTAATACCG-CAT---------AAC-G--TCG---CAAGACCA-AAGA-GG-GGGACCTTCGGGCCT-C---TT-GCCATCGGATGTG-CCCAG-ATGG-G-ATTAGCTAGT-AGGTG-GGGTAACGGCTCACCTA-GGCGACGAT-C-CCTAGC-TG-GTC-TGAGAGG-ATGA-CCAG-CCACACTGG-AACTGAGACACGGTCC-AGACTCCTACGGGAGGCAGCAGT-GGGGAAT-ATT--GCACAATGG-GCGCAA-G-CCTGA-TG-CAGC--CATGCCGCGTGTA-TGA-AGAAGGCCTT--CGG-GT-TGTAAAG-TACT-TT---CAGCGGGGAGGAAGGGAGTA-AAGT----T---AATA---CCTTTG-CT-C-ATTGACG-TTACC---CGCAGAAGAAGC-ACCGGCTAACT-CCGTGCCAGCAGCCGCGGTAATACG-GAGGGTG-CAAGCGTT-AATC-GGAATTACT-GGGCGTAAAGCG-C-ACGCAGGCGGTTT-GTTAAGTC-AGATGTGAAA-TCCCC-GGGCTCAACCTGGG-A---ACTGCATCTG-ATA-CTGG--CAAGCTTGAGT-C-TCGTA-GAGG-G-G-GGTAGAATTCCA-GGTGTAGCGGTGAAATGCGTAGAGAT-CTGGAGGAA-TACC-GGTGGCGAAGGCG-GC-C-CCCTGG-AC-G-AAGACTGACGCT-CAGG-TGCGAAAGCGTGGGGAGC-AAACAGGATTAGATACCCTGGTAGTCCACGCCGTAAACGATG--TCGACT---TG--GAGG---TTGT--GCCC-TTGAG-GCGTGGCTTCCGGAGCTAACGC-GTTAAGTCGAC-C-GCCTGGGGAGTACGG-CCGCAAG---GTTAAAACTCAAATG-AATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGA-TGCAACGCGAAGAACCTTACC-TGGTCTTGACATCC----ACAGAACTTTCC-AGAGAT-GGA-TTGGTGCC--TTCGGG---A-ACTGTGAGACAGGTG-CTGCATGGCT-GTCGTCAGCTCGTGT-TGTGA-AATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTT-ATCTT-TTGTTGCCAGC-GGT-C-CG--GCCGG-GAACTC-AAAGG-AGACTGCCAG-TGA-TAAAC-TGGAGGAAGGTGGGGATGACGTCAA-GTCATCATGGCCC-TTA-CGACC-AGGGCTACACACGTGCTACAATGG-C-GCATACAAAGAG--AAGCGA--CCTCGCGAGAG--CAAGC-GGA--CCTCA-TAAAGTGC-GT-CGT-AGT-CCGGAT-TG-GAGTCTGCAACTCGACT-C-CATGAAG-TCGGAATCGCTAGTAATCG-TGGATCAG-AATGCC-ACGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCA-TG-GGAGTGGGTTG-CAA-A---AGAAGT-AGGT-AG-CTTAACCTT---CGGGAGGGCGCTTA-CC-AC-TTTG----TG--ATTCA--TGACT-GGGGTGAAGTCGTAACAAGGTA-ACCGTA--GG--GGAACCTGCGG-TTGGATCACCTCCTT---A
""",
        )
        self.assertAlmostEqual(alignment.score, 1286.0)
        self.assertEqual(alignment.shape, (2, 1811))


class TestKeywordArgumentsConstructor(unittest.TestCase):
    def test_confusing_arguments(self):
        aligner = Align.PairwiseAligner(
            mode="local",
            open_gap_score=-0.3,
            extend_gap_score=-0.1,
            target_open_gap_score=-0.2,
        )
        self.assertEqual(
            str(aligner),
            """\
Pairwise sequence aligner with parameters
  wildcard: None
  match_score: 1.000000
  mismatch_score: 0.000000
  target_internal_open_gap_score: -0.200000
  target_internal_extend_gap_score: -0.100000
  target_left_open_gap_score: -0.200000
  target_left_extend_gap_score: -0.100000
  target_right_open_gap_score: -0.200000
  target_right_extend_gap_score: -0.100000
  query_internal_open_gap_score: -0.300000
  query_internal_extend_gap_score: -0.100000
  query_left_open_gap_score: -0.300000
  query_left_extend_gap_score: -0.100000
  query_right_open_gap_score: -0.300000
  query_right_extend_gap_score: -0.100000
  mode: local
""",
        )


class TestUnicodeStrings(unittest.TestCase):
    def test_needlemanwunsch_simple1(self):
        seq1 = "ĞĀĀČŦ"
        seq2 = "ĞĀŦ"
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.alphabet = None
        self.assertEqual(aligner.algorithm, "Needleman-Wunsch")
        score = aligner.score(seq1, seq2)
        self.assertAlmostEqual(score, 3.0)
        alignments = aligner.align(seq1, seq2)
        self.assertEqual(len(alignments), 2)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ĞĀĀČŦ
||--|
ĞĀ--Ŧ
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 2], [4, 5]], [[0, 2], [2, 3]]])
            )
        )
        alignment = alignments[1]
        self.assertAlmostEqual(alignment.score, 3.0)
        self.assertEqual(
            str(alignment),
            """\
ĞĀĀČŦ
|-|-|
Ğ-Ā-Ŧ
""",
        )
        self.assertEqual(alignment.shape, (2, 5))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned,
                numpy.array([[[0, 1], [2, 3], [4, 5]], [[0, 1], [1, 2], [2, 3]]]),
            )
        )

    def test_align_affine1_score(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.alphabet = None
        aligner.match_score = 0
        aligner.mismatch_score = -1
        aligner.open_gap_score = -5
        aligner.extend_gap_score = -1
        self.assertEqual(aligner.algorithm, "Gotoh global alignment algorithm")
        score = aligner.score("いい", "あいいう")
        self.assertAlmostEqual(score, -7.0)

    def test_smithwaterman(self):
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.alphabet = None
        aligner.gap_score = -0.1
        self.assertEqual(aligner.algorithm, "Smith-Waterman")
        score = aligner.score("ℵℷℶℷ", "ℸℵℶℸ")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align("ℵℷℶℷ", "ℸℵℶℸ")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
 ℵℷℶℷ
 |-|
ℸℵ-ℶℸ
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[1, 2], [2, 3]]])
            )
        )

    def test_gotoh_local(self):
        aligner = Align.PairwiseAligner()
        aligner.alphabet = None
        aligner.mode = "local"
        aligner.open_gap_score = -0.1
        aligner.extend_gap_score = 0.0
        self.assertEqual(aligner.algorithm, "Gotoh local alignment algorithm")
        score = aligner.score("生物科物", "学生科学")
        self.assertAlmostEqual(score, 1.9)
        alignments = aligner.align("生物科物", "学生科学")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 1.9)
        self.assertEqual(
            str(alignment),
            """\
 生物科物
 |-|
学生-科学
""",
        )
        self.assertEqual(alignment.shape, (2, 3))
        self.assertTrue(
            numpy.array_equal(
                alignment.aligned, numpy.array([[[0, 1], [2, 3]], [[1, 2], [2, 3]]])
            )
        )


class TestAlignerPickling(unittest.TestCase):
    def test_pickle_aligner_match_mismatch(self):
        import pickle

        aligner = Align.PairwiseAligner()
        aligner.wildcard = "X"
        aligner.match_score = 3
        aligner.mismatch_score = -2
        aligner.target_internal_open_gap_score = -2.5
        aligner.target_internal_extend_gap_score = -3.5
        aligner.target_left_open_gap_score = -2.5
        aligner.target_left_extend_gap_score = -3.5
        aligner.target_right_open_gap_score = -4
        aligner.target_right_extend_gap_score = -4
        aligner.query_internal_open_gap_score = -0.1
        aligner.query_internal_extend_gap_score = -2
        aligner.query_left_open_gap_score = -9
        aligner.query_left_extend_gap_score = +1
        aligner.query_right_open_gap_score = -1
        aligner.query_right_extend_gap_score = -2
        aligner.mode = "local"
        state = pickle.dumps(aligner)
        pickled_aligner = pickle.loads(state)
        self.assertEqual(aligner.wildcard, pickled_aligner.wildcard)
        self.assertAlmostEqual(aligner.match_score, pickled_aligner.match_score)
        self.assertAlmostEqual(aligner.mismatch_score, pickled_aligner.mismatch_score)
        self.assertIsNone(pickled_aligner.substitution_matrix)
        self.assertAlmostEqual(
            aligner.target_internal_open_gap_score,
            pickled_aligner.target_internal_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_internal_extend_gap_score,
            pickled_aligner.target_internal_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_left_open_gap_score,
            pickled_aligner.target_left_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_left_extend_gap_score,
            pickled_aligner.target_left_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_right_open_gap_score,
            pickled_aligner.target_right_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_right_extend_gap_score,
            pickled_aligner.target_right_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_internal_open_gap_score,
            pickled_aligner.query_internal_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_internal_extend_gap_score,
            pickled_aligner.query_internal_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_left_open_gap_score,
            pickled_aligner.query_left_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_left_extend_gap_score,
            pickled_aligner.query_left_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_right_open_gap_score,
            pickled_aligner.query_right_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_right_extend_gap_score,
            pickled_aligner.query_right_extend_gap_score,
        )
        self.assertEqual(aligner.mode, pickled_aligner.mode)

    def test_pickle_aligner_substitution_matrix(self):
        try:
            from Bio.Align import substitution_matrices
        except ImportError:
            return
        import pickle

        aligner = Align.PairwiseAligner()
        aligner.wildcard = "N"
        aligner.substitution_matrix = substitution_matrices.load("BLOSUM80")
        aligner.target_internal_open_gap_score = -5
        aligner.target_internal_extend_gap_score = -3
        aligner.target_left_open_gap_score = -2
        aligner.target_left_extend_gap_score = -3
        aligner.target_right_open_gap_score = -4.5
        aligner.target_right_extend_gap_score = -4.3
        aligner.query_internal_open_gap_score = -2
        aligner.query_internal_extend_gap_score = -2.5
        aligner.query_left_open_gap_score = -9.1
        aligner.query_left_extend_gap_score = +1.7
        aligner.query_right_open_gap_score = -1.9
        aligner.query_right_extend_gap_score = -2.0
        aligner.mode = "global"
        state = pickle.dumps(aligner)
        pickled_aligner = pickle.loads(state)
        self.assertEqual(aligner.wildcard, pickled_aligner.wildcard)
        self.assertIsNone(pickled_aligner.match_score)
        self.assertIsNone(pickled_aligner.mismatch_score)
        self.assertTrue(
            (aligner.substitution_matrix == pickled_aligner.substitution_matrix).all()
        )
        self.assertEqual(
            aligner.substitution_matrix.alphabet,
            pickled_aligner.substitution_matrix.alphabet,
        )
        self.assertAlmostEqual(
            aligner.target_internal_open_gap_score,
            pickled_aligner.target_internal_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_internal_extend_gap_score,
            pickled_aligner.target_internal_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_left_open_gap_score,
            pickled_aligner.target_left_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_left_extend_gap_score,
            pickled_aligner.target_left_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_right_open_gap_score,
            pickled_aligner.target_right_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.target_right_extend_gap_score,
            pickled_aligner.target_right_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_internal_open_gap_score,
            pickled_aligner.query_internal_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_internal_extend_gap_score,
            pickled_aligner.query_internal_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_left_open_gap_score,
            pickled_aligner.query_left_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_left_extend_gap_score,
            pickled_aligner.query_left_extend_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_right_open_gap_score,
            pickled_aligner.query_right_open_gap_score,
        )
        self.assertAlmostEqual(
            aligner.query_right_extend_gap_score,
            pickled_aligner.query_right_extend_gap_score,
        )
        self.assertEqual(aligner.mode, pickled_aligner.mode)


class TestAlignmentFormat(unittest.TestCase):
    def test_alignment_simple(self):
        chromosome = "ACGATCAGCGAGCATNGAGCACTACGACAGCGAGTGACCACTATTCGCGATCAGGAGCAGATACTTTACGAGCATCGGC"
        transcript = "AGCATCGAGCGACTTGAGTACTATTCATACTTTCGAGC"
        aligner = Align.PairwiseAligner()
        aligner.query_extend_gap_score = 0
        aligner.query_open_gap_score = -3
        aligner.target_gap_score = -3
        aligner.end_gap_score = 0
        aligner.mismatch = -1
        alignments = aligner.align(chromosome, transcript)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 19.0)
        self.assertEqual(
            str(alignment),
            """\
ACGATCAGCGAGCATNGAGC-ACTACGACAGCGAGTGACCACTATTCGCGATCAGGAGCAGATACTTTACGAGCATCGGC
----------|||||.||||-|||-----------|||..|||||||--------------|||||||-|||||------
----------AGCATCGAGCGACT-----------TGAGTACTATTC--------------ATACTTT-CGAGC------
""",
        )
        self.assertEqual(alignment.shape, (2, 80))
        self.assertEqual(
            alignment.format("psl"),
            """\
34	2	0	1	1	1	3	26	+	query	38	0	38	target	79	10	73	5	10,3,12,7,5,	0,11,14,26,33,	10,20,34,60,68,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	10	73	query	19.0	+	10	73	0	5	10,3,12,7,5,	0,10,24,50,58,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	11	255	10M1I3M11D12M14D7M1D5M	*	0	0	AGCATCGAGCGACTTGAGTACTATTCATACTTTCGAGC	*	AS:i:19
""",
        )
        alignments = aligner.align(
            chromosome, reverse_complement(transcript), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 19.0)
        self.assertEqual(
            str(alignment),
            """\
ACGATCAGCGAGCATNGAGC-ACTACGACAGCGAGTGACCACTATTCGCGATCAGGAGCAGATACTTTACGAGCATCGGC
----------|||||.||||-|||-----------|||..|||||||--------------|||||||-|||||------
----------AGCATCGAGCGACT-----------TGAGTACTATTC--------------ATACTTT-CGAGC------
""",
        )
        self.assertEqual(alignment.shape, (2, 80))
        self.assertEqual(
            alignment.format("psl"),
            """\
34	2	0	1	1	1	3	26	-	query	38	0	38	target	79	10	73	5	10,3,12,7,5,	0,11,14,26,33,	10,20,34,60,68,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	10	73	query	19.0	-	10	73	0	5	10,3,12,7,5,	0,10,24,50,58,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	11	255	10M1I3M11D12M14D7M1D5M	*	0	0	AGCATCGAGCGACTTGAGTACTATTCATACTTTCGAGC	*	AS:i:19
""",
        )

    def test_alignment_end_gap(self):
        aligner = Align.PairwiseAligner()
        aligner.gap_score = -1
        aligner.end_gap_score = 0
        aligner.mismatch = -10
        alignments = aligner.align("ACGTAGCATCAGC", "CCCCACGTAGCATCAGC")
        self.assertEqual(len(alignments), 1)
        self.assertAlmostEqual(alignments.score, 13.0)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
----ACGTAGCATCAGC
----|||||||||||||
CCCCACGTAGCATCAGC
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	+	query	17	4	17	target	13	0	13	1	13,	4,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	+	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	1	255	4S13M	*	0	0	CCCCACGTAGCATCAGC	*	AS:i:13
""",
        )
        alignments = aligner.align(
            "ACGTAGCATCAGC", reverse_complement("CCCCACGTAGCATCAGC"), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        self.assertAlmostEqual(alignments.score, 13.0)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
----ACGTAGCATCAGC
----|||||||||||||
CCCCACGTAGCATCAGC
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	-	query	17	0	13	target	13	0	13	1	13,	4,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	-	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	1	255	4S13M	*	0	0	CCCCACGTAGCATCAGC	*	AS:i:13
""",
        )
        alignments = aligner.align("CCCCACGTAGCATCAGC", "ACGTAGCATCAGC")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13.0)
        self.assertEqual(
            str(alignment),
            """\
CCCCACGTAGCATCAGC
----|||||||||||||
----ACGTAGCATCAGC
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	+	query	13	0	13	target	17	4	17	1	13,	0,	4,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	4	17	query	13.0	+	4	17	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	5	255	13M	*	0	0	ACGTAGCATCAGC	*	AS:i:13
""",
        )
        alignments = aligner.align(
            "CCCCACGTAGCATCAGC", reverse_complement("ACGTAGCATCAGC"), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13.0)
        self.assertEqual(
            str(alignment),
            """\
CCCCACGTAGCATCAGC
----|||||||||||||
----ACGTAGCATCAGC
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	-	query	13	0	13	target	17	4	17	1	13,	0,	4,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	4	17	query	13.0	-	4	17	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	5	255	13M	*	0	0	ACGTAGCATCAGC	*	AS:i:13
""",
        )
        alignments = aligner.align("ACGTAGCATCAGC", "ACGTAGCATCAGCGGGG")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
ACGTAGCATCAGC----
|||||||||||||----
ACGTAGCATCAGCGGGG
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	+	query	17	0	13	target	13	0	13	1	13,	0,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	+	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	1	255	13M4S	*	0	0	ACGTAGCATCAGCGGGG	*	AS:i:13
""",
        )
        alignments = aligner.align(
            "ACGTAGCATCAGC", reverse_complement("ACGTAGCATCAGCGGGG"), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
ACGTAGCATCAGC----
|||||||||||||----
ACGTAGCATCAGCGGGG
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	-	query	17	4	17	target	13	0	13	1	13,	0,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	-	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	1	255	13M4S	*	0	0	ACGTAGCATCAGCGGGG	*	AS:i:13
""",
        )
        alignments = aligner.align("ACGTAGCATCAGCGGGG", "ACGTAGCATCAGC")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13.0)
        self.assertEqual(
            str(alignment),
            """\
ACGTAGCATCAGCGGGG
|||||||||||||----
ACGTAGCATCAGC----
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	+	query	13	0	13	target	17	0	13	1	13,	0,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	+	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	1	255	13M	*	0	0	ACGTAGCATCAGC	*	AS:i:13
""",
        )
        alignments = aligner.align(
            "ACGTAGCATCAGCGGGG", reverse_complement("ACGTAGCATCAGC"), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertAlmostEqual(alignment.score, 13.0)
        self.assertEqual(
            str(alignment),
            """\
ACGTAGCATCAGCGGGG
|||||||||||||----
ACGTAGCATCAGC----
""",
        )
        self.assertEqual(alignment.shape, (2, 17))
        self.assertEqual(
            alignment.format("psl"),
            """\
13	0	0	0	0	0	0	0	-	query	13	0	13	target	17	0	13	1	13,	0,	0,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	0	13	query	13.0	-	0	13	0	1	13,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	1	255	13M	*	0	0	ACGTAGCATCAGC	*	AS:i:13
""",
        )

    def test_alignment_wildcard(self):
        aligner = Align.PairwiseAligner()
        aligner.gap_score = -10
        aligner.end_gap_score = 0
        aligner.mismatch = -2
        aligner.wildcard = "N"
        target = "TTTTTNACGCTCGAGCAGCTACG"
        query = "ACGATCGAGCNGCTACGCCCNC"
        # use strings for target and query
        alignments = aligner.align(target, query)
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
TTTTTNACGCTCGAGCAGCTACG-----
------|||.||||||.||||||-----
------ACGATCGAGCNGCTACGCCCNC
""",
        )
        self.assertEqual(alignment.shape, (2, 28))
        self.assertEqual(
            alignment.format("psl"),
            """\
15	1	0	1	0	0	0	0	+	query	22	0	17	target	23	6	23	1	17,	0,	6,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	6	23	query	13.0	+	6	23	0	1	17,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	7	255	17M5S	*	0	0	ACGATCGAGCNGCTACGCCCNC	*	AS:i:13
""",
        )
        alignments = aligner.align(target, reverse_complement(query), strand="-")
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
TTTTTNACGCTCGAGCAGCTACG-----
------|||.||||||.||||||-----
------ACGATCGAGCNGCTACGCCCNC
""",
        )
        self.assertEqual(alignment.shape, (2, 28))
        self.assertEqual(
            alignment.format("psl"),
            """\
15	1	0	1	0	0	0	0	-	query	22	5	22	target	23	6	23	1	17,	0,	6,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	6	23	query	13.0	-	6	23	0	1	17,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	7	255	17M5S	*	0	0	ACGATCGAGCNGCTACGCCCNC	*	AS:i:13
""",
        )
        # use Seq objects for target and query
        alignments = aligner.align(Seq(target), Seq(query))
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
TTTTTNACGCTCGAGCAGCTACG-----
------|||.||||||.||||||-----
------ACGATCGAGCNGCTACGCCCNC
""",
        )
        self.assertEqual(alignment.shape, (2, 28))
        self.assertEqual(
            alignment.format("psl"),
            """\
15	1	0	1	0	0	0	0	+	query	22	0	17	target	23	6	23	1	17,	0,	6,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	6	23	query	13.0	+	6	23	0	1	17,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	0	target	7	255	17M5S	*	0	0	ACGATCGAGCNGCTACGCCCNC	*	AS:i:13
""",
        )
        alignments = aligner.align(
            Seq(target), Seq(query).reverse_complement(), strand="-"
        )
        self.assertEqual(len(alignments), 1)
        alignment = alignments[0]
        self.assertEqual(
            str(alignment),
            """\
TTTTTNACGCTCGAGCAGCTACG-----
------|||.||||||.||||||-----
------ACGATCGAGCNGCTACGCCCNC
""",
        )
        self.assertEqual(alignment.shape, (2, 28))
        self.assertEqual(
            alignment.format("psl"),
            """\
15	1	0	1	0	0	0	0	-	query	22	5	22	target	23	6	23	1	17,	0,	6,
""",
        )
        self.assertEqual(
            alignment.format("bed"),
            """\
target	6	23	query	13.0	-	6	23	0	1	17,	0,
""",
        )
        self.assertEqual(
            alignment.format("sam"),
            """\
query	16	target	7	255	17M5S	*	0	0	ACGATCGAGCNGCTACGCCCNC	*	AS:i:13
""",
        )


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
