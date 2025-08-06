/*
 * SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES.
 * All rights reserved. SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
*/

#ifndef DOXYGEN_SHOULD_SKIP_THIS
#pragma once

#include <limits>
#include <type_traits>
#include <cassert>

#ifndef __NVCC__
#define NVCOMP_HOST_DEVICE_FUNCTION
#else
#define NVCOMP_HOST_DEVICE_FUNCTION __host__ __device__
#endif // __NVCC__

namespace nvcomp {

/**
 * @brief Return the ceiling of the ratio of input num and input chunk.
 *
 * @tparam U The type of the argument num.
 * @tparam T The type of the argument chunk.
 * @param[in] num The dividend.
 * @param[in] chunk The divisor.
 *
 * @return The rounded quotient of the division.
 */
template <typename U, typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION U roundUpDiv(U const num, T const chunk) noexcept
{
  return (num + chunk - 1) / chunk;
}

/**
 * @brief Round down the input num to an integer multiple of the input chunk.
 *
 * @tparam U The type of the argument num.
 * @tparam T The type of the argument chunk.
 * @param[in] num The original amount to be rounded down.
 * @param[in] chunk The rounding multiple.
 *
 * @return The rounded-down input.
 */
template <typename U, typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION U roundDownTo(U const num, T const chunk) noexcept
{
  return (num / chunk) * chunk;
}

/**
 * @brief Round up the input num to an integer multiple of the input chunk.
 *
 * @tparam U The type of the argument num.
 * @tparam T The type of the argument chunk.
 * @param[in] num The original amount to be rounded up.
 * @param[in] chunk The rounding multiple.
 *
 * @return The rounded-up input.
 */
template <typename U, typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION U roundUpTo(U const num, T const chunk) noexcept
{
  return roundUpDiv(num, chunk) * chunk;
}

/**
 * @brief Return the smallest power of two larger or equal to the input x.
 *
 * @tparam T The type of the argument x.
 * @param[in] x The original amount to be rounded up.
 *
 * @return The rounded-up input.
 */
template<typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION T roundUpPow2(const T x) noexcept
{
  size_t res = 1;
  while(res < x) {
    res *= 2;
  }
  return res;
}

/**
 * @brief Calculate the first aligned location after `ptr`.
 *
 * @tparam T Type such that the alignment requirement is satisfied.
 * @param[in] ptr Input pointer.
 *
 * @return The first pointer after `ptr` that satisfies the alignment requirement.
 */
template <typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION T* roundUpToAlignment(void* ptr) noexcept
{
  constexpr auto alignment = alignof(T);
  const auto address = reinterpret_cast<uintptr_t>(ptr);
  return reinterpret_cast<T*>((address + alignment - 1) & ~(alignment - 1));
}

/**
 * @brief Calculate the first aligned location after `ptr`.
 *
 * @tparam T Type such that the alignment requirement is satisfied.
 * @param[in] ptr Input pointer pointing to constant data.
 *
 * @return The first pointer after `ptr` that satisfies the alignment requirement.
 */
template <typename T>
constexpr NVCOMP_HOST_DEVICE_FUNCTION const T* roundUpToAlignment(const void* ptr) noexcept
{
  constexpr auto alignment = alignof(T);
  const auto address = reinterpret_cast<uintptr_t>(ptr);
  return reinterpret_cast<const T*>((address + alignment - 1) & ~(alignment - 1));
}

/**
 * @brief Verifies whether a given cast from InputT type to OutputT type is valid.
 *
 * @tparam OutputT The output type we intend to cast to.
 * @tparam InputT The input type we intend to cast from.
 *
 * @return Boolean indicating whether the cast is valid.
 */
template <typename OutputT, typename InputT>
constexpr NVCOMP_HOST_DEVICE_FUNCTION bool is_cast_valid(const InputT i) noexcept
{
  static_assert(
      std::numeric_limits<OutputT>::is_integer && std::numeric_limits<InputT>::is_integer,
      "Types for is_cast_valid must both be integers");
  if (std::is_unsigned<InputT>::value) {
      // The minimum bound is always satisfied, so just check the maximum bound.
      // Use larger type, breaking tie with InputT, which is already known unsigned.
      using largerT = typename std::conditional<(sizeof(OutputT) > sizeof(InputT)), OutputT, InputT>::type;
      return static_cast<largerT>(i) <= static_cast<largerT>((std::numeric_limits<OutputT>::max)());
  }

  // At this point, InputT is signed, but because this code will still be compiled
  // for unsigned InputT, force InputT to be signed, to avoid warnings about signed
  // vs. unsigned comparison.
  using signedInputT = typename std::make_signed<InputT>::type;
  using signedOutputT = typename std::make_signed<OutputT>::type;

  // Check whether the input is less than the minimum value of OutputT.
  // I.e. a negative signed integer is casting to an unsigned
  // Note, if OutputT is unsigned, the minimum is zero, which is safe to cast to
  // a signed type.
  if (static_cast<signedInputT>(i)
      < static_cast<signedOutputT>((std::numeric_limits<OutputT>::min)())) {
    return false;
  }

  // Because we've already checked whether the inputT is "too negative", if it's
  // negative at all this is valid
  // InputT is signed and larger than the minimum value of OutputT.
  if (static_cast<signedInputT>(i) <= static_cast<signedInputT>(0)) {
    return true;
  }

  // InputT is signed, but larger than zero, so can be cast to unsigned.
  using unsignedInputT = typename std::make_unsigned<InputT>::type;
  using unsignedOutputT = typename std::make_unsigned<OutputT>::type;

  return static_cast<unsignedInputT>(i)
         <= static_cast<unsignedOutputT>((std::numeric_limits<OutputT>::max)());
}

/**
 * @brief Cast to uint, with debug-only range check, for CUDA kernel launch grid
 * or block dimensions.
 *
 * @tparam T The input type we intend to cast from.
 * @param[in] i Input dimension to cast.
 *
 * @return The input casted to unsigned integer.
 */
template <typename T>
constexpr unsigned int cuda_dim_cast(const T i) noexcept
{
  static_assert(
      std::numeric_limits<T>::is_integer,
      "Type for cuda_dim_cast must be integer");

  assert(is_cast_valid<unsigned int>(i));

  return static_cast<unsigned int>(i);
}

} // namespace nvcomp

#endif /* DOXYGEN_SHOULD_SKIP_THIS */
