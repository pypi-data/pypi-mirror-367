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
#include "ans.hpp"
#include "gdeflate.hpp"
#include "lz4.hpp"
#include "snappy.hpp"
#include "bitcomp.hpp"
#include "cascaded.hpp"
#include "zstd.hpp"
#include "deflate.hpp"
#include "gzip.hpp"

namespace nvcomp {

/**
 * @brief Construct a ManagerBase from a given compressed buffer.
 *
 * @note This operation synchronizes the host with the stream.
 *
 * @param[in] comp_buffer The HLIF compressed buffer from which we intend to create the manager.
 * @param[in] stream The CUDA stream to perform the operation on.
 * @param[in] checksum_policy The checksum policy to use.
 * @param[in] backend The backend (CUDA / hardware decompress engine) to use.
 * @param[in] use_de_sort Whether to sort before hardware decompression for load balancing (for LZ4, Snappy, Deflate, and Gzip).
 *
 * @return The constructed manager instance.
 */
NVCOMP_EXPORT
std::shared_ptr<nvcompManagerBase> create_manager(
    const uint8_t* comp_buffer,
    cudaStream_t stream = 0,
    ChecksumPolicy checksum_policy = NoComputeNoVerify,
    nvcompDecompressBackend_t backend = NVCOMP_DECOMPRESS_BACKEND_DEFAULT,
    bool use_de_sort = false);

} // namespace nvcomp
