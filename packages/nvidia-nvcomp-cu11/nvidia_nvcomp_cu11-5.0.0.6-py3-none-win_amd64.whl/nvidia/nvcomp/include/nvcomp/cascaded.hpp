/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES.
 * All rights reserved. SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
*/

#pragma once

#include "nvcompManager.hpp"
#include "cascaded.h"

namespace nvcomp {

/**
 * @brief Format specification for Cascased compression
 */
struct CascadedFormatSpecHeader {
  /**
   * @brief The size of each internal chunk of data to decompress independently with
   *
   * Cascaded compression. The value should be in the range of [512, 16384]
   * depending on the datatype of the input and the shared memory size of
   * the GPU being used.  This is not the size of chunks passed into the API.
   * Recommended size is 4096.
   *
   * @note Not currently used and a default of 4096 is just used.
   */
  size_t internal_chunk_bytes;
  /**
   * @brief The datatype used to define the bit-width for compression
   */
  nvcompType_t type;
  /**
   * @brief The number of Run Length Encodings to perform.
   */
  int num_RLEs;
  /**
   * @brief The number of Delta Encodings to perform.
   */
  int num_deltas;
  /**
   * @brief Whether or not to bitpack the final layers.
   */
  int use_bp;
};

/**
 * @brief High-level interface class for the Cascaded compressor.
 *
 * @note Any uncompressed data buffer to be compressed MUST be a size that is a
 * multiple of the data type size, else compression may crash or result in
 * invalid output.
 *
 * @note If user_stream is specified, the lifetime of the CascadedManager instance must not
 * extend beyond that of the user_stream.
 */
struct CascadedManager : detail::PimplManager {
  /**
   * @brief Constructor of CascadedManager.
   *
   * @param[in] uncomp_chunk_size Internal chunk size used to partition the input data.
   * @param[in] compress_opts Compression options to use.
   * @param[in] decompress_opts Decompression options to use.
   * @param[in] user_stream The CUDA stream to operate on.
   * @param[in] checksum_policy The checksum policy to use during compression and decompression.
   * @param[in] bitstream_kind Setting to configure how the manager compresses the input.
   */
  NVCOMP_EXPORT
  CascadedManager(
    size_t uncomp_chunk_size,
    const nvcompBatchedCascadedCompressOpts_t& compress_opts = nvcompBatchedCascadedCompressDefaultOpts,
    const nvcompBatchedCascadedDecompressOpts_t& decompress_opts = nvcompBatchedCascadedDecompressDefaultOpts,
    cudaStream_t user_stream = 0,
    ChecksumPolicy checksum_policy = NoComputeNoVerify,
    BitstreamKind bitstream_kind = BitstreamKind::NVCOMP_NATIVE);

  /**
   * @brief Destructor of CascadedManager.
   */
  NVCOMP_EXPORT
  ~CascadedManager() noexcept;
};

} // namespace nvcomp
