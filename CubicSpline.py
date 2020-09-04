#!/usr/bin/env python3
import numpy as np

class CubicSpline:
    '''
    Used to perform a cubic interpolation. Assumes equally spaced points.
    
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
        - 'natural' (default): The second derivatives are zero at the endpoints.
        - 'd_equal' : The third derivatives of the first and second curves are equal.
    
    Methods
    -------
    fn(t):
        The interpolation function.
    interpolate(n):
        Returns an array with an interpolation of n points.
    '''
    
    def __init__(self, points, bc_type='natural'):
        '''
        Constructs the interpolation function.
        
        Parameters
        ----------
        points : (N, M) or (N) array
            The points to interpolate between.
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
        
        # Find the cubic polynomial coefficients
        self.coef = np.zeros((self.N-1, self.M, 4))
        for i_d, dim in enumerate(points.T):
            mat = np.zeros((self.N, self.N))
            row = np.zeros((self.N))
            
            # Endpoint constraints
            if (self.bc_type == "natural"):
                mat[0,0:2]  = [2, 1]
                mat[-1,-2:] = [1, 2]
                row[0] = 3*dim[1] - 3*dim[0]
                row[-1] = 3*dim[-1] - 3*dim[-2]
            elif (self.bc_type == "d_equal"):
                mat[0,0:3]  = [1, 0, -1]
                mat[-1,-3:] = [-1, 0, 1]
                row[0]  = 4*dim[1]  - 2*dim[0]  - 2*dim[2]
                row[-1] = 2*dim[-1] + 2*dim[-3] - 4*dim[-2]
            else:
                raise ValueError('Unknown boundary condition type.')
            
            # Other constraints
            for i in np.arange(1, self.N-1):
                mat[i,i-1:i+2] = [1, 4, 1]
                row[i] = 3*dim[i+1] - 3*dim[i-1]
            
            derivs = np.matmul(np.linalg.inv(mat), row)
            
            self.coef[:,i_d,0] = dim[:-1]
            self.coef[:,i_d,1] = derivs[:-1]
            self.coef[:,i_d,2] = 3*(dim[1:] - dim[:-1]) - 2*derivs[:-1] - derivs[1:]
            self.coef[:,i_d,3] = 2*(dim[:-1] - dim[1:]) + derivs[:-1] + derivs[1:]
    
    
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
        
        if (isinstance(t, (float,int))):
            t_copy = np.array([t]) * (self.N-1)
        else:
            t_copy = np.array(t) * (self.N-1)
        i = t_copy.astype(int)
        t_copy = t_copy % 1
        t_copy = t_copy[:,np.newaxis]
        
        final_point = (i == self.N-1)
        i[final_point] = self.N - 2
        t_copy[final_point] = 1        
        
        interpolation = self.coef[i,:,0] + self.coef[i,:,1]*t_copy + self.coef[i,:,2]*t_copy**2 + self.coef[i,:,3]*t_copy**3
        
        if (self.M == 1): interpolation = interpolation[:,0]
        if (t_copy.size == 1): interpolation = interpolation[0]
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