import generic as g


class TransformTest(g.unittest.TestCase):

    def test_doctest(self):
        '''
        Run doctests on transformations, which checks docstrings for
        interactive sessions and then verifies they execute correctly.

        This is how the upstream transformations unit tests.
        '''
        import trimesh
        import random
        import doctest

        # make sure formatting is the same as their docstrings
        g.np.set_printoptions(suppress=True, precision=5)

        # monkey patch import transformations with random for the examples
        trimesh.transformations.random = random

        # search for interactive sessions in docstrings and verify they work
        # they are super unreliable and depend on janky string formatting
        results = doctest.testmod(trimesh.transformations,
                                  verbose=False,
                                  raise_on_error=False)
        g.log.info('transformations {}'.format(str(results)))

    def test_downstream(self):
        '''
        Run tests on functions that were added downstream of the original
        transformations.py
        '''
        tr = g.trimesh.transformations

        assert not tr.is_rigid(g.np.ones((4, 4)))

        planar = tr.planar_matrix(offset=[10, -10], theta=0.0)
        assert g.np.allclose(planar[:2, 2], [10, -10])

        planar = tr.planar_matrix(offset=[0, -0], theta=g.np.pi)
        assert g.np.allclose(planar[:2, 2], [0, 0])

        planar = tr.planar_matrix(offset=[0, 0], theta=0.0)
        assert g.np.allclose(planar, g.np.eye(3))

        as_3D = tr.planar_matrix_to_3D(g.np.eye(3))
        assert g.np.allclose(as_3D, g.np.eye(4))

        spherical = tr.spherical_matrix(theta=0.0, phi=0.0)
        assert g.np.allclose(spherical, g.np.eye(4))

        points = g.np.arange(60, dtype=g.np.float64).reshape((-1, 3))
        assert g.np.allclose(tr.transform_points(points, g.np.eye(4)), points)

        points = g.np.arange(60, dtype=g.np.float64).reshape((-1, 2))
        assert g.np.allclose(tr.transform_points(points, g.np.eye(3)), points)

    def test_around(self):
        # check transform_around on 2D points
        points = g.np.random.random((100, 2))
        for i, p in enumerate(points):
            offset = g.np.random.random(2)
            matrix = g.trimesh.transformations.planar_matrix(
                theta=g.np.random.random() + .1,
                offset=offset,
                point=p)

            # apply the matrix
            check = g.trimesh.transform_points(points, matrix)
            compare = g.np.isclose(check, points + offset)
            # the point we rotated around shouldn't move
            assert compare[i].all()
            # all other points should move
            assert compare.all(axis=1).sum() == 1

        # check transform_around on 3D points
        points = g.np.random.random((100, 3))
        for i, p in enumerate(points):
            matrix = g.trimesh.transformations.random_rotation_matrix()
            matrix = g.trimesh.transformations.transform_around(matrix, p)

            # apply the matrix
            check = g.trimesh.transform_points(points, matrix)
            compare = g.np.isclose(check, points)
            # the point we rotated around shouldn't move
            assert compare[i].all()
            # all other points should move
            assert compare.all(axis=1).sum() == 1


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
