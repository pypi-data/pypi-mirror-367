"""
Vectorized Operations Module for PyMBO
High-performance numerical computations using vectorization and GPU acceleration
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import scipy.spatial.distance as dist
from scipy.linalg import cholesky, solve_triangular, LinAlgError
import warnings

# Optional numba import for acceleration
try:
    from numba import jit, njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Create dummy decorators if numba is not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def prange(*args, **kwargs):
        return range(*args, **kwargs)

logger = logging.getLogger(__name__)

class VectorizedBayesianOps:
    """Vectorized operations for Bayesian optimization"""
    
    def __init__(self, device: torch.device = None, use_gpu: bool = True):
        """
        Initialize vectorized operations
        
        Args:
            device: PyTorch device to use
            use_gpu: Whether to use GPU acceleration when available
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
        self.use_gpu = torch.cuda.is_available() and use_gpu
        
        logger.info(f"VectorizedBayesianOps initialized on {self.device}")
    
    def batch_distance_matrix(
        self, 
        X1: torch.Tensor, 
        X2: Optional[torch.Tensor] = None,
        distance_type: str = "euclidean"
    ) -> torch.Tensor:
        """
        Compute distance matrix between two sets of points efficiently
        
        Args:
            X1: First set of points [n1, d]
            X2: Second set of points [n2, d], if None uses X1
            distance_type: Type of distance ("euclidean", "manhattan", "cosine")
            
        Returns:
            Distance matrix [n1, n2]
        """
        if X2 is None:
            X2 = X1
        
        X1 = X1.to(self.device)
        X2 = X2.to(self.device)
        
        if distance_type == "euclidean":
            # Efficient euclidean distance using broadcasting
            diff = X1.unsqueeze(1) - X2.unsqueeze(0)  # [n1, n2, d]
            distances = torch.norm(diff, dim=2)  # [n1, n2]
        elif distance_type == "manhattan":
            diff = X1.unsqueeze(1) - X2.unsqueeze(0)
            distances = torch.sum(torch.abs(diff), dim=2)
        elif distance_type == "cosine":
            X1_norm = F.normalize(X1, p=2, dim=1)
            X2_norm = F.normalize(X2, p=2, dim=1)
            distances = 1 - torch.mm(X1_norm, X2_norm.t())
        else:
            raise ValueError(f"Unknown distance type: {distance_type}")
        
        return distances
    
    def batch_kernel_matrix(
        self,
        X1: torch.Tensor,
        X2: Optional[torch.Tensor] = None,
        kernel_type: str = "rbf",
        length_scale: float = 1.0,
        output_scale: float = 1.0,
        noise_level: float = 1e-6
    ) -> torch.Tensor:
        """
        Compute kernel matrix efficiently
        
        Args:
            X1: First set of points [n1, d]
            X2: Second set of points [n2, d]
            kernel_type: Type of kernel ("rbf", "matern")
            length_scale: Kernel length scale
            output_scale: Kernel output scale
            noise_level: Noise level for diagonal (when X1 == X2)
            
        Returns:
            Kernel matrix [n1, n2]
        """
        X1 = X1.to(self.device)
        if X2 is not None:
            X2 = X2.to(self.device)
        else:
            X2 = X1
        
        # Compute squared distances efficiently
        if kernel_type in ["rbf", "matern"]:
            # Use the squared distance formula: ||x-y||^2 = ||x||^2 + ||y||^2 - 2<x,y>
            X1_sqnorms = torch.sum(X1**2, dim=1, keepdim=True)  # [n1, 1]
            X2_sqnorms = torch.sum(X2**2, dim=1, keepdim=True)  # [n2, 1]
            
            # Compute cross terms efficiently using matrix multiplication
            cross_terms = torch.mm(X1, X2.t())  # [n1, n2]
            
            # Broadcast and compute squared distances
            sq_distances = X1_sqnorms + X2_sqnorms.t() - 2 * cross_terms  # [n1, n2]
            sq_distances = torch.clamp(sq_distances, min=0)  # Numerical stability
            
            if kernel_type == "rbf":
                # RBF kernel: exp(-0.5 * r^2 / l^2)
                K = output_scale * torch.exp(-0.5 * sq_distances / (length_scale**2))
            elif kernel_type == "matern":
                # Matern 3/2 kernel
                distances = torch.sqrt(sq_distances)
                scaled_distances = np.sqrt(3) * distances / length_scale
                K = output_scale * (1 + scaled_distances) * torch.exp(-scaled_distances)
        else:
            raise ValueError(f"Unknown kernel type: {kernel_type}")
        
        # Add noise to diagonal if X1 == X2
        if X2 is X1 and noise_level > 0:
            K = K + noise_level * torch.eye(K.shape[0], device=self.device)
        
        return K
    
    def batch_cholesky_solve(
        self,
        A: torch.Tensor,
        B: torch.Tensor,
        jitter: float = 1e-6,
        max_tries: int = 3
    ) -> torch.Tensor:
        """
        Solve linear system using Cholesky decomposition with automatic jitter
        
        Args:
            A: Positive definite matrix [n, n]
            B: Right-hand side [n, m]
            jitter: Initial jitter value
            max_tries: Maximum number of attempts with increasing jitter
            
        Returns:
            Solution X such that AX = B
        """
        A = A.to(self.device)
        B = B.to(self.device)
        
        current_jitter = jitter
        
        for attempt in range(max_tries):
            try:
                # Add jitter to diagonal for numerical stability
                A_jitter = A + current_jitter * torch.eye(A.shape[0], device=self.device)
                
                # Cholesky decomposition
                L = torch.linalg.cholesky(A_jitter)
                
                # Solve using forward and backward substitution
                # First solve Ly = B
                y = torch.triangular_solve(B, L, upper=False)[0]
                
                # Then solve L^T x = y
                x = torch.triangular_solve(y, L.t(), upper=True)[0]
                
                return x
                
            except RuntimeError as e:
                if "not positive definite" in str(e) and attempt < max_tries - 1:
                    current_jitter *= 10
                    logger.warning(f"Cholesky failed, increasing jitter to {current_jitter}")
                    continue
                else:
                    raise
        
        raise RuntimeError(f"Cholesky solve failed after {max_tries} attempts")
    
    def batch_gp_prediction(
        self,
        X_train: torch.Tensor,
        y_train: torch.Tensor,
        X_test: torch.Tensor,
        kernel_params: Dict[str, float],
        return_var: bool = True
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Vectorized GP prediction
        
        Args:
            X_train: Training inputs [n_train, d]
            y_train: Training outputs [n_train, 1]
            X_test: Test inputs [n_test, d]
            kernel_params: Kernel parameters
            return_var: Whether to return predictive variance
            
        Returns:
            Tuple of (mean, variance) predictions
        """
        # Compute kernel matrices
        K_train = self.batch_kernel_matrix(X_train, X_train, **kernel_params)
        K_test_train = self.batch_kernel_matrix(X_test, X_train, **kernel_params)
        
        # Solve for alpha = K_train^{-1} y_train
        alpha = self.batch_cholesky_solve(K_train, y_train.unsqueeze(-1))
        
        # Compute mean prediction
        mean = torch.mm(K_test_train, alpha).squeeze(-1)
        
        if return_var:
            # Compute variance
            K_test = self.batch_kernel_matrix(X_test, X_test, **kernel_params)
            
            # Solve K_train v = K_test_train^T
            v = self.batch_cholesky_solve(K_train, K_test_train.t())
            
            # Variance = K_test - K_test_train K_train^{-1} K_test_train^T
            var = torch.diag(K_test) - torch.sum(K_test_train * v.t(), dim=1)
            var = torch.clamp(var, min=0)  # Ensure non-negative
            
            return mean, var
        
        return mean, None
    
    def batch_acquisition_optimization(
        self,
        acquisition_func: callable,
        bounds: torch.Tensor,
        num_restarts: int = 10,
        num_samples: int = 1000
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Vectorized acquisition function optimization
        
        Args:
            acquisition_func: Acquisition function to optimize
            bounds: Parameter bounds [2, d] (min, max)
            num_restarts: Number of optimization restarts
            num_samples: Number of samples for multi-start optimization
            
        Returns:
            Tuple of (best_candidates, best_values)
        """
        bounds = bounds.to(self.device)
        d = bounds.shape[1]
        
        # Generate initial candidates using Latin Hypercube-like sampling
        candidates = torch.rand(num_samples, d, device=self.device)
        candidates = bounds[0] + candidates * (bounds[1] - bounds[0])
        
        # Evaluate acquisition function for all candidates
        with torch.no_grad():
            values = acquisition_func(candidates.unsqueeze(1))
            if values.dim() > 1:
                values = values.squeeze()
        
        # Select top candidates for refinement
        _, top_indices = torch.topk(values, min(num_restarts, len(values)))
        best_candidates = candidates[top_indices]
        
        # Local optimization using gradient ascent
        best_candidates.requires_grad_(True)
        optimizer = torch.optim.LBFGS([best_candidates], max_iter=50)
        
        def closure():
            optimizer.zero_grad()
            # Clamp candidates to bounds
            with torch.no_grad():
                best_candidates.clamp_(bounds[0], bounds[1])
            
            obj = -acquisition_func(best_candidates.unsqueeze(1)).sum()  # Negative for maximization
            obj.backward()
            return obj
        
        try:
            optimizer.step(closure)
        except RuntimeError as e:
            logger.warning(f"LBFGS optimization failed: {e}")
        
        # Final evaluation
        with torch.no_grad():
            best_candidates.clamp_(bounds[0], bounds[1])
            final_values = acquisition_func(best_candidates.unsqueeze(1))
            if final_values.dim() > 1:
                final_values = final_values.squeeze()
            
            # Return best candidate
            best_idx = torch.argmax(final_values)
            return best_candidates[best_idx].unsqueeze(0), final_values[best_idx].unsqueeze(0)

@njit(parallel=True)
def fast_pdist_numba(X: np.ndarray) -> np.ndarray:
    """Fast pairwise distance computation using Numba"""
    n, d = X.shape
    distances = np.zeros((n, n))
    
    for i in prange(n):
        for j in prange(i + 1, n):
            dist = 0.0
            for k in range(d):
                diff = X[i, k] - X[j, k]
                dist += diff * diff
            distances[i, j] = distances[j, i] = np.sqrt(dist)
    
    return distances

@njit(parallel=True)
def fast_kernel_matrix_numba(
    X1: np.ndarray, 
    X2: np.ndarray, 
    length_scale: float,
    output_scale: float
) -> np.ndarray:
    """Fast RBF kernel matrix computation using Numba"""
    n1, d = X1.shape
    n2 = X2.shape[0]
    K = np.zeros((n1, n2))
    
    for i in prange(n1):
        for j in prange(n2):
            sq_dist = 0.0
            for k in range(d):
                diff = X1[i, k] - X2[j, k]
                sq_dist += diff * diff
            
            K[i, j] = output_scale * np.exp(-0.5 * sq_dist / (length_scale * length_scale))
    
    return K

class NumbaAccelerated:
    """Numba-accelerated operations for CPU computations"""
    
    @staticmethod
    def pairwise_distances(X: np.ndarray) -> np.ndarray:
        """Compute pairwise distances using Numba acceleration"""
        if NUMBA_AVAILABLE:
            return fast_pdist_numba(X)
        else:
            # Fallback to scipy when numba is not available
            from scipy.spatial.distance import pdist, squareform
            return squareform(pdist(X))
    
    @staticmethod
    def rbf_kernel_matrix(
        X1: np.ndarray,
        X2: np.ndarray,
        length_scale: float = 1.0,
        output_scale: float = 1.0
    ) -> np.ndarray:
        """Compute RBF kernel matrix using Numba acceleration"""
        if NUMBA_AVAILABLE:
            return fast_kernel_matrix_numba(X1, X2, length_scale, output_scale)
        else:
            # Fallback to numpy when numba is not available
            from scipy.spatial.distance import cdist
            distances = cdist(X1, X2, 'sqeuclidean')
            return output_scale * np.exp(-0.5 * distances / (length_scale ** 2))

class BatchedGPOperations:
    """Batched operations for multiple GP models"""
    
    def __init__(self, device: torch.device = None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def batch_model_fitting(
        self,
        X_list: List[torch.Tensor],
        y_list: List[torch.Tensor],
        kernel_params_list: List[Dict[str, float]]
    ) -> List[Dict[str, torch.Tensor]]:
        """
        Fit multiple GP models in parallel
        
        Args:
            X_list: List of training inputs
            y_list: List of training outputs
            kernel_params_list: List of kernel parameters
            
        Returns:
            List of fitted model parameters
        """
        fitted_models = []
        
        # Process models in batches to manage memory
        batch_size = min(4, len(X_list))
        
        for i in range(0, len(X_list), batch_size):
            batch_X = X_list[i:i+batch_size]
            batch_y = y_list[i:i+batch_size]
            batch_params = kernel_params_list[i:i+batch_size]
            
            batch_results = []
            for X, y, params in zip(batch_X, batch_y, batch_params):
                X = X.to(self.device)
                y = y.to(self.device)
                
                # Compute kernel matrix
                K = self._compute_kernel_matrix(X, params)
                
                # Fit model (compute alpha and log marginal likelihood)
                try:
                    alpha = torch.linalg.solve(K, y.unsqueeze(-1))
                    L = torch.linalg.cholesky(K)
                    log_det = 2 * torch.sum(torch.log(torch.diag(L)))
                    
                    model_params = {
                        'alpha': alpha,
                        'K_inv': torch.cholesky_inverse(L),
                        'log_det': log_det,
                        'X_train': X,
                        'y_train': y,
                        'kernel_params': params
                    }
                    batch_results.append(model_params)
                    
                except Exception as e:
                    logger.error(f"Error fitting GP model: {e}")
                    batch_results.append(None)
            
            fitted_models.extend(batch_results)
        
        return fitted_models
    
    def _compute_kernel_matrix(
        self, 
        X: torch.Tensor, 
        params: Dict[str, float]
    ) -> torch.Tensor:
        """Compute kernel matrix for given inputs and parameters"""
        # Simple RBF kernel implementation
        length_scale = params.get('length_scale', 1.0)
        output_scale = params.get('output_scale', 1.0)
        noise_level = params.get('noise_level', 1e-6)
        
        # Compute squared distances
        sq_dists = torch.cdist(X, X, p=2) ** 2
        
        # RBF kernel
        K = output_scale * torch.exp(-0.5 * sq_dists / (length_scale ** 2))
        
        # Add noise to diagonal
        K = K + noise_level * torch.eye(K.shape[0], device=self.device)
        
        return K

class OptimizedMatrixOps:
    """Optimized matrix operations for numerical stability and speed"""
    
    @staticmethod
    def stable_cholesky(A: torch.Tensor, max_tries: int = 5) -> torch.Tensor:
        """Numerically stable Cholesky decomposition"""
        jitter = 1e-6
        
        for i in range(max_tries):
            try:
                # Add jitter to diagonal
                A_jitter = A + jitter * torch.eye(A.shape[0], device=A.device, dtype=A.dtype)
                L = torch.linalg.cholesky(A_jitter)
                return L
            except RuntimeError:
                jitter *= 10
                if i == max_tries - 1:
                    raise
                continue
    
    @staticmethod
    def stable_inverse(A: torch.Tensor) -> torch.Tensor:
        """Numerically stable matrix inversion using SVD"""
        try:
            # Try Cholesky first (faster for positive definite matrices)
            L = OptimizedMatrixOps.stable_cholesky(A)
            return torch.cholesky_inverse(L)
        except RuntimeError:
            # Fallback to SVD-based pseudoinverse
            return torch.linalg.pinv(A)
    
    @staticmethod
    def batch_solve(A_batch: torch.Tensor, B_batch: torch.Tensor) -> torch.Tensor:
        """Solve batch of linear systems efficiently"""
        try:
            return torch.linalg.solve(A_batch, B_batch)
        except RuntimeError:
            # Fallback to individual solutions
            solutions = []
            for A, B in zip(A_batch, B_batch):
                try:
                    sol = torch.linalg.solve(A, B)
                    solutions.append(sol)
                except RuntimeError:
                    # Use pseudoinverse as last resort
                    sol = torch.mm(torch.linalg.pinv(A), B)
                    solutions.append(sol)
            return torch.stack(solutions)

# Global instances for easy access
vectorized_ops = VectorizedBayesianOps()
numba_ops = NumbaAccelerated()
batched_gp_ops = BatchedGPOperations()

__all__ = [
    'VectorizedBayesianOps', 'NumbaAccelerated', 'BatchedGPOperations',
    'OptimizedMatrixOps', 'vectorized_ops', 'numba_ops', 'batched_gp_ops'
]