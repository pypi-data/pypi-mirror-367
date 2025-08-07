"""
This module provides functions to estimate the attitude of a vehicle using different algorithms and sensors.

Functions:
    so3_integrator: Integrate the orientation of a frame using the exponential coordinate representation of rotations.
    ahrs_raw_rp: Compute the pitch and roll angles from raw accelerometer measurements.
    ahrs_raw_hdg: Compute the heading angle from raw magnetic field measurements.
    ahrs_raw_rph: Compute the roll, pitch, and heading angles from raw accelerometer and magnetic field measurements.
    ahrs_complementary_filter: Estimate the attitude of a vehicle using a complementary filter.
    ahrs_mahony_filter: Estimate the attitude of a vehicle using the Mahony filter.
    ahrs_hua_filter: Estimate the attitude of a vehicle using the Hua filter.
    ahrs_madgwick_filter: Estimate the attitude of a vehicle using the Madgwick filter.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import Dict, List, Tuple, Union

import imufusion
import numpy as np
import scipy

from navlib.math import (
    difference,
    matrix_log3,
    median,
    norm,
    normalize,
    remove_offset,
    rot2rph,
    rph2rot,
    unwrap1pi,
    vec_to_so3,
    wrap1pi,
)

GRAVITY = 9.80665  # Standard gravity in m/s^2


def so3_integrator(
    Rold: Union[np.ndarray, List[float]],
    Rdot: Union[np.ndarray, List[float]],
    dt: float,
) -> np.ndarray:
    """
    so3_integrator integrates the final orientation R from a frame
    that was initially coincident with Rold followed a rotation described
    by Rdot by a time dt. This computation is based in the exponential
    coordinate representation of rotations.

    The Rodrigues' formula states that R = exp(skew(w)*dt). If we define
    the world frame w and the vehicle frame v, we have a initiall pose R_{wv}
    that we will denote as Rold. If we know the rotation w in the frame v and
    then the skew-symmetric matrix [w] we can compute Rdot as: R_dot = Rold @ [w]
    and equivalentlly: [w] = Rold.T @ Rdot, both inputs of the function. Then:

                Rnew = Rold @ exp((Rold.T @ Rdot) * dt)

    Source: Modern Robotics - Chapter 3.2.3 Exponential Coordinate Representation
    of Rotation (Linch & Park, 2017)

    Note: scipy.linalg.expm compute the matrix exponential using Pade approximation

    Args:
        Rold (Union[np.ndarray, List[float]]): Initial Rotation Matrix
        Rdot (Union[np.ndarray, List[float]]): Rotation Derivative computed from
            angular velocity skew-symmetric matrix
        dt (float): Time step between frames

    Returns:
        Rnew (Union[np.ndarray, List[float]]): New frame rotation matrix

    Raises:
        ValueError: If Rold or Rdot are not numpy arrays or lists
        ValueError: If Rold or Rdot are not 3x3 matrices
    """
    # Convert to numpy arrays
    if isinstance(Rold, list):
        Rold = np.array(Rold)
    if isinstance(Rdot, list):
        Rdot = np.array(Rdot)

    # Check inputs
    if not isinstance(Rold, np.ndarray):
        raise TypeError("Rold must be a numpy array or list")
    if not isinstance(Rdot, np.ndarray):
        raise TypeError("Rdot must be a numpy array or list")
    if not isinstance(dt, (float, int)):
        raise TypeError("dt must be a float or integer")
    dt = float(dt)
    if dt <= 0:
        raise ValueError("dt must be a positive value")

    # Check if Rold and Rdot are 3x3 matrices
    if Rold.shape != (3, 3):
        raise ValueError("Rold must be a 3x3 matrix")
    if Rdot.shape != (3, 3):
        raise ValueError("Rdot must be a 3x3 matrix")

    # Convert to numpy array
    Rold = np.asanyarray(Rold)
    Rdot = np.asanyarray(Rdot)

    # Check if Rold and Rdot are 3x3 matrices
    if Rold.shape != (3, 3):
        raise ValueError("Rold must be a 3x3 matrix")
    if Rdot.shape != (3, 3):
        raise ValueError("Rdot must be a 3x3 matrix")

    return np.dot(Rold, scipy.linalg.expm(np.dot(Rold.T, Rdot) * dt))


def ahrs_correct_magfield(
    magnetic_field: Union[np.ndarray, List[float]],
    hard_iron: Union[np.ndarray, List[float]],
    soft_iron: Union[np.ndarray, List[float]] = np.eye(3, dtype=np.float64),
):
    """
    Corrects the magnetic field measurements for hard-iron and soft-iron distortions.

    The magnetic field measurements are corrected using the following formula:
    magnetic_field_corrected = (soft_iron^-1 @ (magnetic_field - hard_iron)).T

    Args:
        magnetic_field (Union[np.ndarray, List[float]]): Magnetic field measurements.
        hard_iron (Union[np.ndarray, List[float]]): Hard-iron distortion vector.
        soft_iron (Union[np.ndarray, List[float]], optional): Soft-iron distortion matrix.

    Returns:
        corrected_magfield (np.ndarray): Corrected magnetic field measurements.
    """
    # Convert to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(hard_iron, list):
        hard_iron = np.array(hard_iron)
    if isinstance(soft_iron, list):
        soft_iron = np.array(soft_iron)

    # Check inputs
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or list.")
    if not isinstance(hard_iron, np.ndarray):
        raise TypeError("The hard iron must be a numpy array or list.")
    if not isinstance(soft_iron, np.ndarray):
        raise TypeError("The soft iron must be a numpy array or list.")

    # Check shape
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    hard_iron = hard_iron.squeeze()
    if hard_iron.ndim != 1 or hard_iron.shape[0] != 3:
        raise ValueError("The hard iron must be a 1x3 numpy array.")
    if soft_iron.ndim != 2 or (soft_iron.shape[0] != 3 and soft_iron.shape[1] != 3):
        raise ValueError("The soft iron must be a 3x3 numpy array.")

    # Check if the magnetic field and hard iron are 3xN or Nx3 matrices
    if magnetic_field.shape[0] == 3 and magnetic_field.shape[1] != 3:
        magnetic_field = magnetic_field.T

    # Check if the soft iron is a symmetric matrix
    if not np.allclose(soft_iron, soft_iron.T, atol=1e-8):
        raise ValueError("The soft iron matrix must be symmetric.")

    # Check if the soft-iron is a positive definite matrix
    try:
        np.linalg.cholesky(soft_iron)
    except np.linalg.LinAlgError:
        raise ValueError("The soft iron matrix must be positive definite.")

    # Correct the magnetic field
    magnetic_field_corrected = magnetic_field.copy()[..., np.newaxis]
    N = magnetic_field.shape[0]
    magnetic_field_corrected = magnetic_field_corrected - np.tile(
        hard_iron.reshape(3, 1), (N, 1, 1)
    )
    magnetic_field_corrected = (
        np.tile(np.linalg.inv(soft_iron), (N, 1, 1)) @ magnetic_field_corrected
    ).squeeze()

    return magnetic_field_corrected


def ahrs_raw_rp(acceleration: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    ahrs_raw_rp computes pitch and roll from raw accelerometer measurements.

    The computations is based in the following formulas:
    * roll  = np.arctan2(-ay, -az)
    * pitch = np.arctan2(ax, np.sqrt(ay^2 + az^2))

    Args:
        acceleration (Union[np.ndarray, List[float]]): Accelerometer raw data in three
            dimensions.

    Returns:
        rph_rad (np.ndarray): Roll and pitch angles in radians

    Raises:
        ValueError: If acceleration is not a numpy array or list
    """
    # Convert to numpy array
    if isinstance(acceleration, list):
        acceleration = np.array(acceleration)

    # Check inputs
    if not isinstance(acceleration, np.ndarray):
        raise TypeError("Acceleration must be a numpy array or list")
    if acceleration.ndim != 2 or (
        acceleration.shape[0] != 3 and acceleration.shape[1] != 3
    ):
        raise ValueError("Acceleration must be a 3xN or Nx3 numpy array")

    # Check if acceleration is a 3xN or Nx3 matrix
    if acceleration.shape[0] == 3 and acceleration.shape[1] != 3:
        acceleration = acceleration.T

    # Normalize Accelerations
    acc = normalize(acceleration)

    # Calculating Roll and Pitch (base on gravity vector)
    roll = np.arctan2(-acc[:, 1], -acc[:, 2]).reshape(-1, 1)
    pitch = np.arctan2(acc[:, 0], np.sqrt(acc[:, 1] ** 2 + acc[:, 2] ** 2)).reshape(
        -1, 1
    )

    return np.concatenate([roll, pitch], axis=1)


def ahrs_raw_hdg(
    magnetic_field: Union[np.ndarray, List[float]],
    rph: Union[np.ndarray, List[float]] = None,
) -> np.ndarray:
    """
    raw_hdg computes the heading from magnetic field measurements and rph data.

    If rph is a parameter, the using roll and pitch the corresponding rotation
    matrices are computed and the magnetic field measuremnts are transformated
    to measurements in the xy plane. With the planar magnetic field measuremnts,
    the heading is computed as: heading = np.arcant2(-my, mx)

    Args:
        magnetic_field (Union[np.ndarray, List[float]]): Magnetic field raw data
        rph (Union[np.ndarray, List[float]], optional): Roll, pitch and heading data

    Returns:
        heading_rad (np.ndarray): Heading angle in radians

    Raises:
        ValueError: If mag_field is not a numpy array or list
        ValueError: If rph is not a numpy array or list
    """
    # Convert to numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if rph is not None and isinstance(rph, list):
        rph = np.array(rph)
    # Check inputs
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("mag_field must be a numpy array or list")
    if rph is not None and not isinstance(rph, np.ndarray):
        raise TypeError("rph must be a numpy array or list")
    # Check shape
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("mag_field must be a 3xN or Nx3 numpy array")
    if rph is not None and (rph.ndim != 2 or (rph.shape[0] != 3 and rph.shape[1] != 3)):
        raise ValueError("rph must be a 3xN or Nx3 numpy array")

    # Check if mag_field and rph are 3xN or Nx3 matrices
    if magnetic_field.shape[0] == 3 and magnetic_field.shape[1] != 3:
        magnetic_field = magnetic_field.T
    if rph is not None and rph.shape[0] == 3 and rph.shape[1] != 3:
        rph = rph.T

    # Flatten Magnetic Field if the RPH is provided
    if rph is not None:
        rot_mat_flat = np.apply_along_axis(
            rph2rot, 1, np.concatenate([rph[:, [0, 1]], rph[:, [2]] * 0], axis=1)
        )
        mf = np.einsum(
            "ijk->ikj", rot_mat_flat @ magnetic_field.reshape(-1, 3, 1)
        ).squeeze()
    else:
        mf = magnetic_field

    # Calculate HDG
    heading = np.arctan2(-mf[:, 1], mf[:, 0]).reshape(-1, 1)

    return heading


def ahrs_raw_rph(
    magnetic_field: Union[np.ndarray, List[float]],
    accelerometer: Union[np.ndarray, List[float]],
) -> np.ndarray:
    """
    ahrs_raw_rph computes the roll, pitch and heading from magnetic field
    measurements and accelerometer raw data.

    The computations is based in the following formulas:
    * roll  = np.arctan2(-ay, -az)
    * pitch = np.arctan2(ax, np.sqrt(ay^2 + az^2))
    * heading = np.arctan2(-my, mx)

    Args:
        magnetic_field (Union[np.ndarray, List[float]]): Magnetic field raw data
        accelerometer (Union[np.ndarray, List[float]]): Accelerometer raw data

    Returns:
        np.ndarray: Roll, pitch and heading angles in radians
    """
    # Roll and Pitch
    roll_pitch = ahrs_raw_rp(accelerometer)

    # Heading
    heading = ahrs_raw_hdg(
        magnetic_field, np.concatenate([roll_pitch, roll_pitch[:, [0]] * 0], axis=1)
    )

    # RPH
    rph = np.concatenate([roll_pitch, heading], axis=1)

    return rph


def ahrs_complementary_filter(
    angular_rate: Union[np.ndarray, List[float]],
    acceleration: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]],
    magnetic_field: Union[np.ndarray, List[float]] = None,
    gain: Union[float, int] = 0.1,
    rph0: Union[np.ndarray, List[float]] = None,
) -> np.ndarray:
    """
    Estimates the attitude of a vehicle using a complementary filter. The filter fuses accelerometer and gyroscope,
    and optionally magnetometer data to estimate the roll, pitch, and heading angles.

    For the pitch and roll estimation, we use the accelerometer data, which is assumed to be aligned with the
    gravity vector:

    $$ \\text{roll} = \\arctan2(-a_y, -a_z) \\quad\\quad\\quad \\text{pitch} = \\arctan2(a_x, \\sqrt{a_y^2 + a_z^2}) $$

    The gyroscope integration is performed in the lie algebra of the special orthogonal group SO(3) using the
    Rodrigues' formula:

    $$ R_{new} = R_{old} \\cdot \\exp([\\omega]_\\times \\cdot dt) $$

    Args:
        angular_rate (Union[np.ndarray, List[float]]): Angular rate measurements (gyroscope data) in rad/s.
            Should be a 3xN or Nx3 array where N is the number of samples.
        acceleration (Union[np.ndarray, List[float]]): Acceleration measurements in m/s^2.
            Should be a 3xN or Nx3 array where N is the number of samples.
        time (Union[np.ndarray, List[float]]): Time vector in seconds. Should be a 1D array of length N.
        magnetic_field (Union[np.ndarray, List[float]], optional): Magnetic field measurements in microteslas.
            Should be a 3xN or Nx3 array where N is the number of samples. Defaults to None.
        gain (Union[float, int], optional): Gain for the complementary filter. Should be between 0 and 1. With 1 meaning
            only accelerometer and magnetometer (if available) data is used, and 0 meaning only gyroscope data is used.
            Defaults to 0.9.
        rph0 (Union[np.ndarray, List[float]], optional): Initial roll, pitch, and heading angles in radians.

    Returns:
        rph_rad (np.ndarray): Estimated roll, pitch, and heading (yaw) angles in radians.
            The output is an Nx3 array where N is the number of samples.

    Raises:
        TypeError: If any of the inputs are not of the expected type.
        ValueError: If any of the inputs do not have the expected dimensions.
    """
    # Convert lists to numpy arrays if necessary
    if isinstance(acceleration, list):
        acceleration = np.array(acceleration)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)
    if magnetic_field is not None and isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if rph0 is not None and isinstance(rph0, list):
        rph0 = np.array(rph0)

    # Validate inputs
    if not isinstance(acceleration, np.ndarray):
        raise TypeError("The acceleration must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")
    if magnetic_field is not None and not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if rph0 is not None and not isinstance(rph0, np.ndarray):
        raise TypeError(
            "The initial roll, pitch, and heading must be a numpy array or a list."
        )

    # Validate dimensions
    if acceleration.ndim != 2 or (
        acceleration.shape[0] != 3 and acceleration.shape[1] != 3
    ):
        raise ValueError("The acceleration must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")
    if magnetic_field is not None:
        if magnetic_field.ndim != 2 or (
            magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
        ):
            raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if rph0 is not None:
        if rph0.ndim != 1 or rph0.shape[0] != 3:
            raise ValueError(
                "The initial roll, pitch, and heading must be a 1D numpy array with 3 elements."
            )

    # Ensure time is a 1D array
    time = time.squeeze()
    if time.ndim >= 2:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force Nx3 shape for acceleration, angular_rate, and magnetic_field
    if acceleration.shape[0] == 3 and acceleration.shape[1] != 3:
        acceleration = acceleration.T
    if angular_rate.shape[0] == 3 and angular_rate.shape[1] != 3:
        angular_rate = angular_rate.T
    if (
        magnetic_field is not None
        and magnetic_field.shape[0] == 3
        and magnetic_field.shape[1] != 3
    ):
        magnetic_field = magnetic_field.T

    # Validate initial_heading and gain
    if not isinstance(gain, (float, int)):
        raise TypeError("The gain must be a float or integer.")
    if gain < 0 or gain > 1:
        raise ValueError("The gain must be between 0 and 1.")
    gain = float(gain)

    # Compute the attitude from accelerometer and magnetic field, if available
    if magnetic_field is None:
        rph = np.zeros_like(acceleration)
        rph[:, :2] = ahrs_raw_rp(acceleration)
    else:
        rph = ahrs_raw_rph(magnetic_field, acceleration)

    # If an initial attitude is provided, remove the offset from the computed attitude
    # and add it to the initial attitude.
    if rph0 is not None:
        rph = wrap1pi(remove_offset(unwrap1pi(rph), rph[0] - rph0))

    # If the gain is 0, return the computed attitude
    if gain == 1:
        return rph

    # Complementary Filter - In the SO(3) manifold
    estimated_rph = np.apply_along_axis(rph2rot, 1, rph)
    for ix in range(1, angular_rate.shape[0]):
        # Measurements
        w = angular_rate[ix, :]
        dt = time[ix] - time[ix - 1]

        # Angular rates so(3) Integration based on Rodrigues' formula
        rot_mat_old = estimated_rph[ix - 1]
        rot_mat_new = rot_mat_old @ scipy.linalg.expm(vec_to_so3(w) * dt)

        # Fuse with the accelerometer and magnetometer RPH estimation
        if magnetic_field is None:
            estimated_rph[ix] = rot_mat_new
        else:
            rot_mat_error = rot_mat_new.T @ estimated_rph[ix]
            rot_mat_delta = scipy.linalg.expm(gain * matrix_log3(rot_mat_error))
            estimated_rph[ix] = rot_mat_new @ rot_mat_delta

    return np.array([rot2rph(rot) for rot in estimated_rph])


def ahrs_mahony_filter(
    angular_rate: Union[np.ndarray, List[float]],
    acceleration: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]],
    magnetic_field: Union[np.ndarray, List[float]] = None,
    reference_magnetic_field: Union[np.ndarray, List[float]] = None,
    rph0: Union[np.ndarray, List[float]] = None,
    k1: Union[float, int] = 50.0,
    k2: Union[float, int] = 1.0,
    kp: Union[float, int] = 1.0,
    ki: Union[float, int] = 0.01,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimates the attitude of a vehicle using the Mahony filter.

    This estimator proposed by Robert Mahony et al. [Mahony2008] is formulated as a deterministic kinematic observer
    on the Special Orthogonal group SO(3) driven by an instantaneous attitude and angular velocity measurements.

    k1 and k2 tunning: The weights k1 and k2 are introduced to weight the confidence in each measure. In situations where
    the IMU is subject to high magnitude accelerations (such as during takeoff or landing manoeuvres) it may be wise to
    reduce the relative weighting of the accelerometer data (k1 << k2) compared to the magnetometer data. Conversely, in
    many applications the IMU is mounted in the proximity to powerful electric motors and their power supply busses
    leading to low confidence in the magnetometer readings (choose k1 >> k2). This is a very common situation in the case
    of mini aerial vehicles with electric motors. In extreme cases the magnetometer data is unusable and provides
    motivation for a filter based solely on accelerometer data.

    Args:
        angular_rate (Union[np.ndarray, List[float]]): Angular rate measurements (gyroscope data) in rad/s.
            Should be a 3xN or Nx3 array where N is the number of samples.
        acceleration (Union[np.ndarray, List[float]]): Acceleration measurements in m/s^2.
            Should be a 3xN or Nx3 array where N is the number of samples.
        time (Union[np.ndarray, List[float]]): Time vector in seconds. Should be a 1D array of length N.
        magnetic_field (Union[np.ndarray, List[float]], optional): Magnetic field measurements in microteslas.
            Should be a 3xN or Nx3 array where N is the number of samples. Defaults to None.
        reference_magnetic_field (Union[np.ndarray, List[float]], optional): Reference magnetic field vector in any units.
            Should be a 1D array with 3 elements. Defaults to None.
        rph0 (Union[np.ndarray, List[float]], optional): Initial roll, pitch, and heading angles in radians.
        k1 (Union[float, int], optional): Gain for the accelerometer measurements. Defaults to 50.0.
        k2 (Union[float, int], optional): Gain for the magnetic field measurements. Defaults to 1.0.
        kp (Union[float, int], optional): Proportional gain. Defaults to 1.0.
        ki (Union[float, int], optional): Integral gain. Defaults to 0.01.

    Returns:
        rph_filtered (np.ndarray): Estimated roll, pitch, and heading (yaw) angles in radians. The output is an
            Nx3 array.
        angrate_filtered (np.ndarray): Bias compensated angular rates in rad/s. The output is an Nx3 array.

    Raises:
        TypeError: If any of the inputs are not of the expected type.
        ValueError: If any of the inputs do not have the expected dimensions.

    References:
        Mahony, R., Hamel, T., & Pflimlin, J. M. (2008). Nonlinear complementary filters on the special orthogonal group.
        IEEE Transactions on automatic control, 53(5), 1203-1218.
    """
    # Convert lists to numpy arrays if necessary
    if isinstance(acceleration, list):
        acceleration = np.array(acceleration)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)
    if magnetic_field is not None and isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if reference_magnetic_field is not None and isinstance(
        reference_magnetic_field, list
    ):
        reference_magnetic_field = np.array(reference_magnetic_field)
    if rph0 is not None and isinstance(rph0, list):
        rph0 = np.array(rph0)

    # Validate inputs
    if not isinstance(acceleration, np.ndarray):
        raise TypeError("The acceleration must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")
    if magnetic_field is not None and not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if reference_magnetic_field is not None and not isinstance(
        reference_magnetic_field, np.ndarray
    ):
        raise TypeError("The reference magnetic field must be a numpy array or a list.")
    if rph0 is not None and not isinstance(rph0, np.ndarray):
        raise TypeError(
            "The initial roll, pitch, and heading must be a numpy array or a list."
        )

    # Validate dimensions
    if acceleration.ndim != 2 or (
        acceleration.shape[0] != 3 and acceleration.shape[1] != 3
    ):
        raise ValueError("The acceleration must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")
    if magnetic_field is not None:
        if magnetic_field.ndim != 2 or (
            magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
        ):
            raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if reference_magnetic_field is not None:
        reference_magnetic_field = reference_magnetic_field.squeeze()
        if reference_magnetic_field.ndim >= 2 or reference_magnetic_field.shape[0] != 3:
            raise ValueError(
                "The reference magnetic field must be a 1D numpy array with 3 elements."
            )
    if rph0 is not None:
        if rph0.ndim != 1 or rph0.shape[0] != 3:
            raise ValueError(
                "The initial roll, pitch, and heading must be a 1D numpy array with 3 elements."
            )

    # Ensure time is a 1D array
    time = time.squeeze()
    if time.ndim >= 2:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force Nx3 shape for acceleration, angular_rate, and magnetic_field
    if acceleration.shape[0] == 3 and acceleration.shape[1] != 3:
        acceleration = acceleration.T
    if angular_rate.shape[0] == 3 and angular_rate.shape[1] != 3:
        angular_rate = angular_rate.T
    if (
        magnetic_field is not None
        and magnetic_field.shape[0] == 3
        and magnetic_field.shape[1] != 3
    ):
        magnetic_field = magnetic_field.T

    # If magnetic field is provided, a reference magnetic field is required
    if magnetic_field is not None and reference_magnetic_field is None:
        raise ValueError(
            "If magnetic field is provided, a reference magnetic field is required."
        )

    # Validate gains
    if not isinstance(k1, (float, int)):
        raise TypeError("The k1 gain must be a float or integer.")
    k1 = float(k1)
    if not isinstance(k2, (float, int)):
        raise TypeError("The k2 gain must be a float or integer.")
    k2 = float(k2)
    if not isinstance(kp, (float, int)):
        raise TypeError("The kp gain must be a float or integer.")
    kp = float(kp)
    if not isinstance(ki, (float, int)):
        raise TypeError("The ki gain must be a float or integer.")
    ki = float(ki)

    # Create arrays to store the results
    samples = time.shape[0]
    rot_mat_filtered = np.tile(np.eye(3), (samples, 1, 1))
    gyro_biases = np.zeros([samples, 3])

    # Initialize the attitude if an initial attitude is provided
    rot_mat_filtered[0] = (
        rph2rot(rph0) if rph0 is not None else np.eye(3, dtype=np.float64)
    )

    # Reference gravity vector
    g_vec = np.array([0.0, 0.0, -1.0])
    g_vec = (g_vec / norm(g_vec)).reshape(3, 1)

    # Reference magnetic field vector
    if reference_magnetic_field is not None:
        m_vec = reference_magnetic_field
        m_vec = (m_vec / norm(m_vec)).reshape(3, 1)

    # Run the filter
    for ix in range(1, samples):
        # Gyroscope, accelerometer, and magnetic field measurements
        w = angular_rate[ix]
        a = acceleration[ix] / norm(acceleration[ix])
        if magnetic_field is not None:
            m = magnetic_field[ix] / norm(magnetic_field[ix])

        rot_mat_old = rot_mat_filtered[ix - 1]

        # Innovation term computation (Eq. 32c in [Mahony2008])
        wmes = k1 * (vec_to_so3(a) @ (rot_mat_old.T @ g_vec)).flatten()
        if magnetic_field is not None:
            wmes += k2 * (vec_to_so3(m) @ (rot_mat_old.T @ m_vec)).flatten()

        # Rotation change in time and gyroscope bias change in time (Eq. 32a and 32b in [Mahony2008])
        rot_mat_dot = rot_mat_old @ (
            vec_to_so3(w - gyro_biases[ix - 1]) + kp * vec_to_so3(wmes)
        )
        gyro_biases_dot = -ki * wmes

        # Time step
        dt = time[ix] - time[ix - 1]

        # Update the gyro bias and the filtered roll, pitch, and heading
        gyro_biases[ix] = gyro_biases[ix - 1] + dt * gyro_biases_dot
        rot_mat_filtered[ix] = so3_integrator(rot_mat_old, rot_mat_dot, dt)

    return (
        np.array([rot2rph(matrix) for matrix in rot_mat_filtered]),
        angular_rate - gyro_biases,
    )


def ahrs_hua_filter(
    angular_rate: Union[np.ndarray, List[float]],
    acceleration: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]],
    magnetic_field: Union[np.ndarray, List[float]] = None,
    reference_magnetic_field: Union[np.ndarray, List[float]] = None,
    rph0: Union[np.ndarray, List[float]] = None,
    k1: Union[float, int] = 1.0,
    k2: Union[float, int] = 0.2,
    k3: Union[float, int] = 0.03,
    k4: Union[float, int] = 0.006,
    kb: Union[float, int] = 16.0,
    delta: Union[float, int] = 0.03,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimates the attitude of a vehicle using the Hua filter.

    This estimator proposed by Robert Mahony et al. [Mahony2008] is formulated as a deterministic kinematic observer
    on the Special Orthogonal group SO(3) driven by an instantaneous attitude and angular velocity measurements.
    The implementation includes modifications by Hua et al. [Hua2014] for measurement decoupling and anti-windup
    gyro-bias compensation.

    k1, k2, k3, k4, and kb tuning: Obtained from values proposed in [Hua2014].

    Args:
        angular_rate (Union[np.ndarray, List[float]]): Angular rate measurements (gyroscope data) in rad/s.
            Should be a 3xN or Nx3 array where N is the number of samples.
        acceleration (Union[np.ndarray, List[float]]): Acceleration measurements in m/s^2.
            Should be a 3xN or Nx3 array where N is the number of samples.
        time (Union[np.ndarray, List[float]]): Time vector in seconds. Should be a 1D array of length N.
        magnetic_field (Union[np.ndarray, List[float]], optional): Magnetic field measurements in microteslas.
            Should be a 3xN or Nx3 array where N is the number of samples. Defaults to None.
        reference_magnetic_field (Union[np.ndarray, List[float]], optional): Reference magnetic field vector in any units.
            Should be a 1D array with 3 elements. Defaults to None.
        rph0 (Union[np.ndarray, List[float]], optional): Initial roll, pitch, and heading angles in radians.
        k1 (Union[float, int], optional): Gain for the accelerometer measurements on the rotation estimation. As recommended
            in [Hua2014], defaults to 1.0.
        k2 (Union[float, int], optional): Gain for the magnetic field measurements on the rotation estimation. As recommended
            in [Hua2014], defaults to 1/5 of k1, which is 0.2. However, if the magnetic field is is highly affected by
            external disturbances, it is recommended to increase the ratio to 1/10 or 1/20.
        k3 (Union[float, int], optional): Gain for the accelerometer measurements on the gyroscope bias estimation. As recommended
            in [Hua2014], defaults to k1/32, which is 0.03.
        k4 (Union[float, int], optional): Gain for the magnetic field measurements on the gyroscope bias estimation. As recommended
            in [Hua2014], defaults to k2/32, which is 0.006. If k2 is increased for robustness against disturbances,
            this value should be updated accordingly.
        kb (Union[float, int], optional): Anti-windup gain. As recommended in [Hua2014], defaults to 16.0.
        delta (Union[float, int], optional): Saturation limit for the gyro biases. As recommended in [Hua2014], to bound
            the gyro biases to 1 deg/s, defaults to 0.003.

    Returns:
        rph_filtered (np.ndarray): Estimated roll, pitch, and heading (yaw) angles in radians. The output is an
            Nx3 array.
        angrate_filtered (np.ndarray): Bias compensated angular rates in rad/s. The output is an Nx3 array.

    Raises:
        TypeError: If any of the inputs are not of the expected type.
        ValueError: If any of the inputs do not have the expected dimensions.

    References:
        Mahony, R., Hamel, T., & Pflimlin, J. M. (2008). Nonlinear complementary filters on the special orthogonal group.
        IEEE Transactions on automatic control, 53(5), 1203-1218.
        Hua, M. D., Ducard, G., Hamel, T., Mahony, R., & Rudin, K. (2014). Implementation of Nonlinear attitude estimator
        for Aerial Robotic Vehicles. IEEE Transactions on Control Systems Technology, Volumes, 22(1), 2972-2978. January
        2014.
    """
    # Convert lists to numpy arrays if necessary
    if isinstance(acceleration, list):
        acceleration = np.array(acceleration)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)
    if magnetic_field is not None and isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if reference_magnetic_field is not None and isinstance(
        reference_magnetic_field, list
    ):
        reference_magnetic_field = np.array(reference_magnetic_field)
    if rph0 is not None and isinstance(rph0, list):
        rph0 = np.array(rph0)

    # Validate inputs
    if not isinstance(acceleration, np.ndarray):
        raise TypeError("The acceleration must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")
    if magnetic_field is not None and not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if reference_magnetic_field is not None and not isinstance(
        reference_magnetic_field, np.ndarray
    ):
        raise TypeError("The reference magnetic field must be a numpy array or a list.")
    if rph0 is not None and not isinstance(rph0, np.ndarray):
        raise TypeError(
            "The initial roll, pitch, and heading must be a numpy array or a list."
        )

    # Validate dimensions
    if acceleration.ndim != 2 or (
        acceleration.shape[0] != 3 and acceleration.shape[1] != 3
    ):
        raise ValueError("The acceleration must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")
    if magnetic_field is not None:
        if magnetic_field.ndim != 2 or (
            magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
        ):
            raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if reference_magnetic_field is not None:
        reference_magnetic_field = reference_magnetic_field.squeeze()
        if reference_magnetic_field.ndim >= 2 or reference_magnetic_field.size != 3:
            raise ValueError(
                "The reference magnetic field must be a 1D numpy array with 3 elements."
            )
    if rph0 is not None:
        if rph0.ndim != 1 or rph0.shape[0] != 3:
            raise ValueError(
                "The initial roll, pitch, and heading must be a 1D numpy array with 3 elements."
            )

    # Ensure time is a 1D array
    time = time.squeeze()
    if time.ndim >= 2:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force Nx3 shape for acceleration, angular_rate, and magnetic_field
    if acceleration.shape[0] == 3 and acceleration.shape[1] != 3:
        acceleration = acceleration.T
    if angular_rate.shape[0] == 3 and angular_rate.shape[1] != 3:
        angular_rate = angular_rate.T
    if (
        magnetic_field is not None
        and magnetic_field.shape[0] == 3
        and magnetic_field.shape[1] != 3
    ):
        magnetic_field = magnetic_field.T

    # If magnetic field is provided, a reference magnetic field is required
    if magnetic_field is not None and reference_magnetic_field is None:
        raise ValueError(
            "If magnetic field is provided, a reference magnetic field is required."
        )

    # Validate gains
    if not isinstance(k1, (float, int)):
        raise TypeError("The k1 gain must be a float or integer.")
    k1 = float(k1)
    if not isinstance(k2, (float, int)):
        raise TypeError("The k2 gain must be a float or integer.")
    k2 = float(k2)
    if not isinstance(k3, (float, int)):
        raise TypeError("The k3 gain must be a float or integer.")
    k3 = float(k3)
    if not isinstance(k4, (float, int)):
        raise TypeError("The k4 gain must be a float or integer.")
    k4 = float(k4)
    if not isinstance(kb, (float, int)):
        raise TypeError("The kb gain must be a float or integer.")
    kb = float(kb)
    if not isinstance(delta, (float, int)):
        raise TypeError("The delta gain must be a float or integer.")
    delta = float(delta)

    # Create arrays to store the results
    samples = time.shape[0]
    rot_mat_filtered = np.tile(np.eye(3), (samples, 1, 1))
    gyro_biases = np.zeros([samples, 3])

    # Initialize the attitude if an initial attitude is provided
    rot_mat_filtered[0] = (
        rph2rot(rph0) if rph0 is not None else np.eye(3, dtype=np.float64)
    )

    # Reference gravity vector [Eq. 8 in [Hua2014]]
    u_i = np.array([0.0, 0.0, 1.0], dtype=np.float64).reshape(3, 1)

    # Reference magnetic field vector [Eq. 8 in [Hua2014]]. It includes the decoupling of the magnetic field
    # from the gravity vector, as proposed by Hua et al. [Hua2014], to avoid the influence of the magnetic field
    # perturbations on the roll and pitch estimation.
    if reference_magnetic_field is not None:
        v_i = _ahrs_hua_orthogonal_projection(u_i) @ reference_magnetic_field.reshape(
            3, 1
        )
        v_i /= np.linalg.norm(v_i)

    # Run the filter
    for ix in range(1, samples):
        # Get attitude from previous step
        rot_mat_old = rot_mat_filtered[ix - 1]

        # Get angular rate
        w = angular_rate[ix - 1].reshape(3, 1)

        # Compute u_b and v_b [Eq. 8 in [Hua2014]]
        u_b = -1 * normalize(acceleration[ix].reshape(3, 1))
        u_b_hat = rot_mat_old.T @ u_i
        if magnetic_field is not None:
            v_b_numerator = _ahrs_hua_orthogonal_projection(u_b) @ magnetic_field[
                ix
            ].reshape(3, 1)
            v_b_denominator = np.linalg.norm(
                _ahrs_hua_orthogonal_projection(u_i)
                * reference_magnetic_field.reshape(3, 1)
            )
            v_b = v_b_numerator / v_b_denominator
            v_b_hat = rot_mat_old.T @ v_i

        # sigma_r [Eq. 12 in [Hua2014]]
        sigma_r = k1 * (vec_to_so3(u_b) @ (u_b_hat))
        if magnetic_field is not None:
            sigma_r += k2 * (u_b_hat @ u_b_hat.T) @ (vec_to_so3(v_b) @ v_b_hat)

        # sigma_b [Eq. 12 in [Hua2014]]
        sigma_b = -k3 * (vec_to_so3(u_b) @ (u_b_hat))
        if magnetic_field is not None:
            sigma_b += -k4 * (vec_to_so3(v_b) @ v_b_hat)

        # Corrected angular rate [Eq. 12 in [Hua2014]]
        gyro_bias_old = gyro_biases[ix - 1].reshape(3, 1)
        w_corrected = w - gyro_bias_old

        # Gyros bias dot [Eq. 12 in [Hua2014]]
        gyro_bias_dot = -kb * gyro_bias_old
        gyro_bias_dot += kb * _ahrs_hua_saturation(gyro_bias_old, delta)
        gyro_bias_dot += sigma_b

        # Rotation dot [Eq. 12 in [Hua2014]]
        rot_mat_dot = rot_mat_old @ vec_to_so3(w_corrected + sigma_r)

        # Time step
        dt = time[ix] - time[ix - 1]

        # Updated gyro bias and attitude
        gyro_biases[ix] = (gyro_bias_old + dt * gyro_bias_dot).flatten()
        rot_mat_filtered[ix] = so3_integrator(rot_mat_old, rot_mat_dot, dt)

    return (
        np.array([rot2rph(matrix) for matrix in rot_mat_filtered]),
        angular_rate - gyro_biases,
    )


def ahrs_madgwick_filter(
    angular_rate: Union[np.ndarray, List[float]],
    acceleration: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]],
    magnetic_field: Union[np.ndarray, List[float]] = None,
    rph0: Union[np.ndarray, List[float]] = None,
    gain: Union[float, int] = 0.5,
    gyro_range: Union[float, int] = 2000.0,
    accel_rejection: Union[float, int] = 10.0,
    magnetic_rejection: Union[float, int] = 10.0,
    recovery_trigger: Union[float, int] = 5.0,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
    """
    Estimates the attitude of a vehicle using the Madgwick filter.

    Madgwick Filter: The complemenetary filter proposed by Sebastian Madgwick. The algorithm calculates the orientation
    as the integration of the gyroscope summed with a feedback term. The feedback term is equal to the error in the
    current measurement of orientation as determined by the other sensors, multiplied by a gain. The algorithm therefore
    functions as a complementary filter that combines high-pass filtered gyroscope measurements with low-pass
    filtered measurements from other sensors with a corner frequency determined by the gain. A low gain will 'trust' the
    gyroscope more and so be more susceptible to drift. A high gain will increase the influence of other sensors and the
    errors that result from accelerations and magnetic distortions. A gain of zero will ignore the other sensors so that
    the measurement of orientation is determined by only the gyroscope.

    Args:
        angular_rate (Union[np.ndarray, List[float]]): Angular rate measurements (gyroscope data) in rad/s.
            Should be a 3xN or Nx3 array where N is the number of samples.
        acceleration (Union[np.ndarray, List[float]]): Acceleration measurements in m/s^2.
            Should be a 3xN or Nx3 array where N is the number of samples.
        time (Union[np.ndarray, List[float]]): Time vector in seconds. Should be a 1D array of length N.
        magnetic_field (Union[np.ndarray, List[float]], optional): Magnetic field measurements in microteslas.
            Should be a 3xN or Nx3 array where N is the number of samples. Defaults to None.
        rph0 (Union[np.ndarray, List[float]], optional): Initial roll, pitch, and heading angles in radians.
        gain (Union[float, int], optional): Determines the influence of the gyroscope relative to other sensors. A value
            of zero will disable initialisation and the acceleration and magnetic rejection features. A value of 0.5 is
            appropriate for most applications. Defaults to 0.5.
        gyro_range (Union[float, int], optional): Gyroscope range (in degrees per second). Angular rate recovery will
            activate if the gyroscope measurement exceeds 98% of this value. A value of zero will disable this feature.
            The value should be set to the range specified in the gyroscope datasheet. Defaults to 2000.0.
        accel_rejection (Union[float, int], optional): Acceleration Rejection: Threshold (in degrees) used by the
            acceleration rejection feature. A value of zero will disable this feature. A value of 10 degrees is
            appropriate for most applications. Defaults to 10.0.
        magnetic_rejection (Union[float, int], optional): Magnetic Rejection: Threshold (in degrees) used by the
            magnetic rejection feature. A value of zero will disable the feature. A value of 10 degrees is appropriate
            for most applications. Defaults to 10.0.
        recovery_trigger (Union[float, int], optional): Acceleration and magnetic recovery trigger period (in seconds).
            A value of zero will disable the acceleration and magnetic rejection features. A period of 5 seconds is
            appropriate for most applications. Defaults to 5.0.

    Returns:
        rph_filtered (np.ndarray): Estimated roll, pitch, and heading angles in radians. The output is an Nx3 array.
        angrate_filtered (np.ndarray): Offset-corrected angular rate measurements in rad/s (not the original input). The output is an Nx3 array.
        flags (np.ndarray): Flags indicating the status of the filter. The output is a dictionary with the following
            keys:
            - "initializing": Indicates if the filter is initializing.
            - "angular_rate_recovery": Indicates if the angular rate recovery feature is active.
            - "acceleration_recovery": Indicates if the acceleration recovery feature is active.
            - "magnetic_recovery": Indicates if the magnetic recovery feature is active.

    Raises:
        TypeError: If any of the inputs are not of the expected type.
        ValueError: If any of the inputs do not have the expected dimensions.

    References:
        Madgwick, S. O. (2010). An efficient orientation filter for inertial and inertial/magnetic sensor arrays.
    """
    # Convert lists to numpy arrays if necessary
    if isinstance(acceleration, list):
        acceleration = np.array(acceleration)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)
    if magnetic_field is not None and isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if rph0 is not None and isinstance(rph0, list):
        rph0 = np.array(rph0)

    # Validate inputs
    if not isinstance(acceleration, np.ndarray):
        raise TypeError("The acceleration must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")
    if magnetic_field is not None and not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if rph0 is not None and not isinstance(rph0, np.ndarray):
        raise TypeError(
            "The initial roll, pitch, and heading must be a numpy array or a list."
        )

    # Validate dimensions
    if acceleration.ndim != 2 or (
        acceleration.shape[0] != 3 and acceleration.shape[1] != 3
    ):
        raise ValueError("The acceleration must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")
    if magnetic_field is not None:
        if magnetic_field.ndim != 2 or (
            magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
        ):
            raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if rph0 is not None:
        if rph0.ndim != 1 or rph0.shape[0] != 3:
            raise ValueError(
                "The initial roll, pitch, and heading must be a 1D numpy array with 3 elements."
            )

    # Ensure time is a 1D array
    time = time.squeeze()
    if time.ndim >= 2:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force Nx3 shape for acceleration, angular_rate, and magnetic_field
    if acceleration.shape[0] == 3 and acceleration.shape[1] != 3:
        acceleration = acceleration.T
    if angular_rate.shape[0] == 3 and angular_rate.shape[1] != 3:
        angular_rate = angular_rate.T
    if (
        magnetic_field is not None
        and magnetic_field.shape[0] == 3
        and magnetic_field.shape[1] != 3
    ):
        magnetic_field = magnetic_field.T

    # Validate Madgwick filter parameters
    if not isinstance(gain, (float, int)):
        raise TypeError("The gain must be a float or integer.")
    if gain < 0 or gain > 1:
        raise ValueError("The gain must be between 0 and 1.")
    gain = float(gain)
    if not isinstance(gyro_range, (float, int)):
        raise TypeError("The gyro range must be a float or integer.")
    if gyro_range <= 0:
        raise ValueError("The gyro range must be greater than 0.")
    gyro_range = float(gyro_range)
    if not isinstance(accel_rejection, (float, int)):
        raise TypeError("The accel rejection must be a float or integer.")
    if accel_rejection < 0:
        raise ValueError("The accel rejection must be greater than or equal to 0.")
    accel_rejection = float(accel_rejection)
    if not isinstance(magnetic_rejection, (float, int)):
        raise TypeError("The magnetic rejection must be a float or integer.")
    if magnetic_rejection < 0:
        raise ValueError("The magnetic rejection must be greater than or equal to 0.")
    magnetic_rejection = float(magnetic_rejection)
    if not isinstance(recovery_trigger, (float, int)):
        raise TypeError("The recovery trigger must be a float or integer.")
    if recovery_trigger < 0:
        raise ValueError("The recovery trigger must be greater than or equal to 0.")
    recovery_trigger = float(recovery_trigger)

    # Compute sample rate
    sample_rate = int(1.0 / median(difference(time)))

    # Match units required by the imufusion library
    # Acceleration in g and angular rate in degrees per second
    acceleration = acceleration / GRAVITY
    angular_rate = np.rad2deg(angular_rate)

    # Instantiate algorithms
    offset = imufusion.Offset(sample_rate)
    ahrs = imufusion.Ahrs()

    ahrs.settings = imufusion.Settings(
        imufusion.CONVENTION_NED,
        gain,
        gyro_range,
        accel_rejection,
        magnetic_rejection,
        int(
            recovery_trigger * sample_rate,
        ),
    )

    # Process sensor data
    delta_time = np.concatenate([np.zeros((1,)), difference(time)], axis=0)
    rph_filtered = np.empty((time.shape[0], 3))
    flags = {
        "initializing": [],
        "angular_rate_recovery": [],
        "acceleration_recovery": [],
        "magnetic_recovery": [],
        "acceleration_error": [],
        "accelerometer_ignored": [],
        "magnetic_error": [],
        "magnetometer_ignored": [],
    }

    for idx in range(time.shape[0]):
        # Apply gyroscope bias compensation
        angular_rate[idx] = offset.update(angular_rate[idx])

        # Update the Madgwick filter
        if magnetic_field is None:
            ahrs.update_no_magnetometer(
                angular_rate[idx], acceleration[idx], delta_time[idx]
            )
        else:
            ahrs.update(
                angular_rate[idx],
                acceleration[idx],
                magnetic_field[idx],
                delta_time[idx],
            )

        if ahrs.flags.initialising and rph0 is not None:
            rph_filtered[idx] = rph0
        else:
            rph_filtered[idx] = np.deg2rad(ahrs.quaternion.to_euler())

        # Flags for initialization or recovery trigger
        ahrs_flags = ahrs.flags
        flags["initializing"].append(ahrs_flags.initialising)
        flags["angular_rate_recovery"].append(ahrs_flags.angular_rate_recovery)
        flags["acceleration_recovery"].append(ahrs_flags.acceleration_recovery)
        flags["magnetic_recovery"].append(ahrs_flags.magnetic_recovery)

        ahrs_internal_state = ahrs.internal_states
        flags["acceleration_error"].append(ahrs_internal_state.acceleration_error)
        flags["accelerometer_ignored"].append(ahrs_internal_state.accelerometer_ignored)
        flags["magnetic_error"].append(ahrs_internal_state.magnetic_error)
        flags["magnetometer_ignored"].append(ahrs_internal_state.magnetometer_ignored)

    # Convert flags to numpy arrays
    for key in flags:
        flags[key] = np.array(flags[key])

    # Wrap angles to [-pi, pi]
    rph_filtered = wrap1pi(rph_filtered)

    return rph_filtered, np.deg2rad(angular_rate), flags


def _ahrs_hua_orthogonal_projection(vector: np.ndarray) -> np.ndarray:
    """
    Orthogonal projection of a vector x on the plane orthogonal to it.

    Args:
        vector (np.ndarray): The vector to project. Should be a 1D array with 3 elements.

    Returns:
        np.ndarray: The orthogonal projection of the vector on the plane orthogonal to it.
            The output is a 3x3 numpy array.
    """
    if (vector.ndim == 1 and vector.shape[0] != 3) or (
        vector.ndim == 2 and vector.shape != (3, 1)
    ):
        raise ValueError(
            "The vector must be a 1D numpy array with 3 elements or a 3x1 numpy array."
        )

    return (np.linalg.norm(vector) ** 2) * np.eye(
        3, dtype=np.float64
    ) - vector @ vector.T


def _ahrs_hua_saturation(vector: np.ndarray, delta: float) -> np.ndarray:
    """
    Saturation of a vector to a given limit.

    Args:
        vector (np.ndarray): The vector to saturate. Should be a 1D array with 3 elements.
        delta (float): The saturation limit.

    Returns:
        np.ndarray: The saturated vector. The output is a 3x1 numpy array.
    """
    if (vector.ndim == 1 and vector.shape[0] != 3) or (
        vector.ndim == 2 and vector.shape != (3, 1)
    ):
        raise ValueError(
            "The vector must be a 1D numpy array with 3 elements or a 3x1 numpy array."
        )
    if not isinstance(delta, (float, int)):
        raise TypeError("The delta must be a float or integer.")
    delta = float(delta)

    vector = vector.reshape(3, 1)

    if np.isclose(np.linalg.norm(vector), 0.0, rtol=1e-6):
        return vector
    else:
        return vector * np.min([1, delta / np.linalg.norm(vector)])
