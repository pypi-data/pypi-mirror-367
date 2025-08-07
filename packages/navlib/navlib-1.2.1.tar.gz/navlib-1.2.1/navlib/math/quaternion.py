"""
This module provides functions to work in the quaternion representation of rotations, as the double cover of the
special orthogonal group SO(3).

Functions:
    left_qmatrix(quat): Compute the left quaternion product matrix for a quaternion.
    right_qmatrix(quat): Compute the right quaternion product matrix for a quaternion.
    quat_conj(q): Compute the conjugate of a quaternion.
    quat_inv(q): Compute the inverse of a quaternion.
    quat_normalize(q): Normalize a quaternion to unit norm.
    quat_positive_scalar(q): Ensure a quaternion has a positive scalar component.

Authors: Sebastián Rodríguez-Martínez
Contact: srodriguez@mbari.org
"""

from typing import Iterable, Union

import numpy as np


def left_qmatrix(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the left quaternion product matrix for a given quaternion, such that
    q * p = L(q) * p. For a quaternion q = (x, y, z, w)  under the JPL convention,
    the left quaternion product matrix is defined as:

    $$
    L(q) =
    \\begin{bmatrix}
        w & -z & y & x \\\\
        z & w & -x & y \\\\
        -y & x & w & z \\\\
        -x & -y & -z & w
    \\end{bmatrix}
    $$

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
            (x, y, z, w).

    Returns:
        left_quat_product_matrix (np.ndarray): The left quaternion product matrix as a (4, 4) numpy array.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.
        TypeError: If the input quaternion is not a numpy array or list.
    """
    # Convert to numpy array if input is a list
    if isinstance(quat, list):
        quat = np.array(quat)

    # Check if the input is a numpy array
    if not isinstance(quat, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or a list.")

    # Check if the input quaternion has 4 elements
    quat = quat.squeeze()
    if quat.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if quat.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional numpy array or list.")

    # Check if the quaternion is normalized
    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("The quaternion must be normalized.")

    # Extract quaternion components
    x, y, z, w = quat[0], quat[1], quat[2], quat[3]

    # Construct the left quaternion product matrix
    left_quat_product_matrix = np.array(
        [
            [w, -z, y, x],
            [z, w, -x, y],
            [-y, x, w, z],
            [-x, -y, -z, w],
        ]
    )
    return left_quat_product_matrix


def right_qmatrix(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the right quaternion product matrix for a given quaternion, such that
    q * p = R(p) * q For a quaternion q = (x, y, z, w) under the JPL convention,
    the right quaternion product matrix is defined as:

    $$
    R(q) =
    \\begin{bmatrix}
        w & z & -y & x \\\\
        -z & w & x & y \\\\
        y & -x & w & z \\\\
        -x & -y & -z & w
    \\end{bmatrix}
    $$

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
            (x, y, z, w).

    Returns:
        right_quat_product_matrix (np.ndarray): The right quaternion product matrix as a (4, 4) numpy array.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.
        TypeError: If the input quaternion is not a numpy array or list.
    """
    # Convert to numpy array if input is a list
    if isinstance(quat, list):
        quat = np.array(quat)

    # Check if the input is a numpy array
    if not isinstance(quat, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or a list.")

    # Check if the input quaternion has 4 elements
    quat = quat.squeeze()
    if quat.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if quat.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional numpy array or list.")

    # Check if the quaternion is normalized
    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("The quaternion must be normalized.")

    # Extract quaternion components
    x, y, z, w = quat[0], quat[1], quat[2], quat[3]

    # Construct the right quaternion product matrix
    right_quat_product_matrix = np.array(
        [
            [w, z, -y, x],
            [-z, w, x, y],
            [y, -x, w, z],
            [-x, -y, -z, w],
        ]
    )
    return right_quat_product_matrix


def quat_conj(q: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the conjugate of a quaternion under the JPL convention (x, y, z, w).

    Args:
        q (Union[np.ndarray, Iterable[float]]): Input quaternion as a list or numpy array (x, y, z, w).

    Returns:
        np.ndarray: The conjugated quaternion.
    """
    if isinstance(q, list):
        q = np.array(q)
    if not isinstance(q, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or list.")
    q = q.squeeze()
    if q.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if q.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional array.")

    return np.array([-q[0], -q[1], -q[2], q[3]])


def quat_inv(q: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the inverse of a quaternion under the JPL convention (x, y, z, w).

    Args:
        q (Union[np.ndarray, Iterable[float]]): Input quaternion as a list or numpy array (x, y, z, w).

    Returns:
        np.ndarray: The inverted quaternion.
    """
    if isinstance(q, list):
        q = np.array(q)
    if not isinstance(q, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or list.")
    q = q.squeeze()
    if q.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if q.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional array.")

    return quat_conj(q) / np.dot(q, q)


def quat_normalize(q: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Normalize a quaternion to unit norm under the JPL convention (x, y, z, w).

    Args:
        q (Union[np.ndarray, Iterable[float]]): Input quaternion as a list or numpy array (x, y, z, w).

    Returns:
        np.ndarray: The normalized quaternion.
    """
    if isinstance(q, list):
        q = np.array(q)
    if not isinstance(q, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or list.")
    q = q.squeeze()
    if q.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if q.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional array.")

    norm_q = np.linalg.norm(q)
    if norm_q < 1e-8:
        raise ValueError("The quaternion norm is too close to zero to normalize.")
    return q / norm_q


def quat_positive_scalar(q: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Ensure that a quaternion has a positive scalar component (w > 0),
    flipping its sign if needed. This removes ambiguity from double coverage.

    Args:
        q (Union[np.ndarray, Iterable[float]]): Input quaternion (x, y, z, w).

    Returns:
        np.ndarray: Quaternion with positive scalar part.
    """
    if isinstance(q, list):
        q = np.array(q)
    if not isinstance(q, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or list.")
    q = q.squeeze()
    if q.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if q.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional array.")

    return q if q[3] >= 0.0 else -q
