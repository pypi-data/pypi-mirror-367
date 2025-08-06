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
#include "snappy.h"

namespace nvcomp {

/**
 * @brief Format specification for Snappy compression
 */
struct SnappyFormatSpecHeader {
  // Empty for now
};

/**
 * @brief High-level interface class for the Snappy compressor.
 *
 * @note If user_stream is specified, the lifetime of the SnappyManager instance must not
 * extend beyond that of the user_stream.
 */
struct SnappyManager : detail::PimplManager {
  /**
   * @brief Constructor of SnappyManager.
   *
   * @param[in] uncomp_chunk_size Internal chunk size used to partition the input data.
   * @param[in] compress_opts Compression options to use.
   * @param[in] decompress_opts Decompression options to use.
   * @param[in] user_stream The CUDA stream to operate on.
   * @param[in] checksum_policy The checksum policy to use during compression and decompression.
   * @param[in] bitstream_kind Setting to configure how the manager compresses the input.
   */
  NVCOMP_EXPORT
  SnappyManager(
    size_t uncomp_chunk_size,
    const nvcompBatchedSnappyCompressOpts_t& compress_opts = nvcompBatchedSnappyCompressDefaultOpts,
    const nvcompBatchedSnappyDecompressOpts_t& decompress_opts = nvcompBatchedSnappyDecompressDefaultOpts,
    cudaStream_t user_stream = 0,
    ChecksumPolicy checksum_policy = NoComputeNoVerify,
    BitstreamKind bitstream_kind = BitstreamKind::NVCOMP_NATIVE);

  /**
   * @brief Destructor of SnappyManager.
   */
  NVCOMP_EXPORT
  ~SnappyManager() noexcept;
};

} // namespace nvcomp
