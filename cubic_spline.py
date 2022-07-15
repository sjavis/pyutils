#!/usr/bin/env python3
import numpy as np

class CubicSpline:
    '''
    Used to perform a cubic interpolation.

    Attributes
    ----------
    N : int
        Number of points to interpolate.
    M : int
        Number of dimensions for each point.
    coef : (N-1, M, 4) array
        Coefficients for the piecewise cubic functions.
    bc_type : str
        The endpoint boundary condition.
        - 'natural' : The second derivatives are zero at the endpoints.
        - 'd_equal' : The third derivatives of the first and second curves are equal.

    Methods
    -------
    fn(t):
        The interpolation function.
    interpolate(n):
        Returns an array with an interpolation of n points.
    '''

    def __init__(self, points, distances=None, bc_type='natural'):
        '''
        Constructs the interpolation function.

        Parameters
        ----------
        points : (N, M) or (N) array
            The points to interpolate between.
        distances : (N-1) array (optional)
            The distances between each pair of points.
        bc_type : str (optional)
            The endpoint boundary condition.
            - 'natural' (default): The second derivatives are zero at the endpoints.
            - 'd_equal' : The third derivatives of the first and second curves are equal.
        '''

        points = np.array(points)
        if(len(points.shape) == 1):
            points = points[:,np.newaxis]
        self.N = points.shape[0]
        self.M = points.shape[1]
        self.bc_type = bc_type
        if (distances is None):
            distances = np.ones(self.N-1)
            self.uniform = True
        else:
            assert(len(distances) == self.N-1)
            self.uniform = False
        self.dt = np.array(distances) / np.sum(distances)
        self.t0 = np.insert(np.cumsum(self.dt[:-1]), 0, 0)

        self.coef = np.zeros((self.N-1, self.M, 4))
        for i_d, dim in enumerate(points.T):
            mat = np.zeros((self.N, self.N))
            row = np.zeros((self.N))

            # Endpoint constraints
            if (self.bc_type == "natural"):
                if (self.uniform):
                    mat[0,0:2]  = [2, 1]
                    mat[-1,-2:] = [1, 2]
                    row[0] = 3 * (dim[1] - dim[0])
                    row[-1] = 3 * (dim[-1] - dim[-2])
                else:
                    mat[0,0:2]  = [2/self.dt[0], 1/self.dt[0]]
                    mat[-1,-2:] = [1/self.dt[-1], 2/self.dt[-1]]
                    row[0] = 3 * (dim[1] - dim[0]) / self.dt[0]**2
                    row[-1] = 3 * (dim[-1] - dim[-2]) / self.dt[-1]**2
            elif (self.bc_type == "d_equal"):
                assert(self.N > 3)
                assert(self.uniform)
                mat[0,0:3]  = [1, 0, -1]
                mat[-1,-3:] = [-1, 0, 1]
                row[0]  = 4*dim[1]  - 2*dim[0]  - 2*dim[2]
                row[-1] = 2*dim[-1] + 2*dim[-3] - 4*dim[-2]
            else:
                raise ValueError('Unknown boundary condition type.')

            # Other constraints
            for i in np.arange(1, self.N-1):
                if (self.uniform):
                    mat[i,i-1:i+2] = [1, 4, 1]
                    row[i] = 3 * (dim[i+1] - dim[i-1])
                else:
                    h0 = 1 / self.dt[i-1]
                    h1 = 1 / self.dt[i]
                    mat[i,i-1:i+2] = [h0, 2*(h0+h1), h1]
                    row[i] = 3*(dim[i] - dim[i-1])*h0**2 + 3*(dim[i+1] - dim[i])*h1**2

            derivs = np.matmul(np.linalg.inv(mat), row)

            # Find the cubic polynomial coefficients
            if (self.uniform):
                self.coef[:,i_d,0] = dim[:-1]
                self.coef[:,i_d,1] = derivs[:-1]
                self.coef[:,i_d,2] = 3*(dim[1:] - dim[:-1]) - 2*derivs[:-1] - derivs[1:]
                self.coef[:,i_d,3] = 2*(dim[:-1] - dim[1:]) + derivs[:-1] + derivs[1:]
            else:
                self.coef[:,i_d,0] = dim[:-1]
                self.coef[:,i_d,1] = derivs[:-1] * self.dt
                self.coef[:,i_d,2] = 3*(dim[1:] - dim[:-1]) - (2*derivs[:-1] + derivs[1:]) * self.dt
                self.coef[:,i_d,3] = 2*(dim[:-1] - dim[1:]) + (derivs[:-1] + derivs[1:]) * self.dt


    def fn(self, t):
        '''
        The interpolation function.

        Parameters
        ----------
        t : float or (n) array
            The pathlength(s) at which to evaluate the interpolation. Between 0 and 1.

        Returns
        -------
        interpolation : (n,M) array (or reduced)
            The interpolated point(s).
        '''

        if (isinstance(t, (float,int))): t = [t]
        t = np.array(t)
        i = np.array([np.squeeze(np.argwhere(t_val >= self.t0)[-1]) for t_val in t])
        ti = (t - self.t0[i]) / self.dt[i]
        ti = ti[:,np.newaxis]

        interpolation = self.coef[i,:,0] + self.coef[i,:,1]*ti + self.coef[i,:,2]*ti**2 + self.coef[i,:,3]*ti**3

        if (self.M == 1): interpolation = interpolation[:,0]
        if (t.size == 1): interpolation = interpolation[0]
        return interpolation


    def interpolate(self, n):
        '''
        Returns an array with an interpolation of n points.

        Parameters
        ----------
        n : int
            The number of points to interpolate.

        Returns
        -------
        interpolation : (n,M) array
            The interpolated points.
        t : (n) array
            The pathlengths at which the interpolation is evaluated.
        '''

        t = np.linspace(0, 1, n)
        interpolation = self.fn(t)
        return interpolation, t



if (__name__ == "__main__"):
    from matplotlib import pyplot as plt

    points = np.array([[0,1], [4,5], [8,4], [6,1], [10,5]])
    cspline = CubicSpline(points, bc_type='d_equal')
    interpolation, t = cspline.interpolate(100)

    plt.plot(interpolation[:,0], interpolation[:,1])
    plt.plot(points[:,0], points[:,1], 'ko')

    print('At t = 0.0: ', cspline.fn(0))
    print('At t = 0.5: ', cspline.fn(0.5))
    print('At t = 1.0: ', cspline.fn(1))

    spline2 = CubicSpline([0,1,3])
    print(spline2.fn(0))

    print('Non-uniform:')
    spline3 = CubicSpline([[0,0],[1,10],[3,30]], distances=[1,2])
    print('At t = 0.0: ', spline3.fn(0))
    print('At t = 0.5: ', spline3.fn(0.5))
    print('At t = 1.0: ', spline3.fn(1))
