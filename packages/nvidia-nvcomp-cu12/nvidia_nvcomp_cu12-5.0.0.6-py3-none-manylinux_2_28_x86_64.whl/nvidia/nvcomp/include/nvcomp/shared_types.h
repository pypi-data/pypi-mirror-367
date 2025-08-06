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

#ifndef NVCOMP_SHARED_TYPES_H
#define NVCOMP_SHARED_TYPES_H

#ifdef __cplusplus
#include <cstddef>
#include <cstdint>
#else
#include <stddef.h>
#include <stdint.h>
#endif // __cplusplus

/**
 * @brief nvCOMP return statuses.
 */
typedef enum nvcompStatus_t
{
  nvcompSuccess = 0,
  nvcompErrorInvalidValue = 10,
  nvcompErrorNotSupported = 11,
  nvcompErrorCannotDecompress = 12,
  nvcompErrorBadChecksum = 13,
  nvcompErrorCannotVerifyChecksums = 14,
  nvcompErrorOutputBufferTooSmall = 15,
  nvcompErrorWrongHeaderLength = 16,
  nvcompErrorAlignment = 17,
  nvcompErrorChunkSizeTooLarge = 18,
  nvcompErrorCannotCompress = 19,
  nvcompErrorWrongInputLength = 20,
  nvcompErrorCudaError = 1000,
  nvcompErrorInternal = 10000,
} nvcompStatus_t;

/**
 * @brief Supported data types.
 */
typedef enum nvcompType_t
{
  NVCOMP_TYPE_CHAR = 0,      // 1B
  NVCOMP_TYPE_UCHAR = 1,     // 1B
  NVCOMP_TYPE_SHORT = 2,     // 2B
  NVCOMP_TYPE_USHORT = 3,    // 2B
  NVCOMP_TYPE_INT = 4,       // 4B
  NVCOMP_TYPE_UINT = 5,      // 4B
  NVCOMP_TYPE_LONGLONG = 6,  // 8B
  NVCOMP_TYPE_ULONGLONG = 7, // 8B
  NVCOMP_TYPE_FLOAT16 = 9,   // 2B
  NVCOMP_TYPE_BITS = 0xff    // 1b
} nvcompType_t;

/**
 * @brief Available decompression backend options
*/
typedef enum nvcompDecompressBackend_t
{
  /// Let nvCOMP decide the best decompression backend internally, either
  /// hardware decompression or one of the CUDA implementations.
  NVCOMP_DECOMPRESS_BACKEND_DEFAULT = 0,

  /// Decompress using the dedicated hardware decompression engine.
  NVCOMP_DECOMPRESS_BACKEND_HARDWARE = 1,

  /// Decompress using the CUDA implementation.
  NVCOMP_DECOMPRESS_BACKEND_CUDA = 2,
} nvcompDecompressBackend_t;

/**
 * @brief nvCOMP properties.
 */
typedef struct
{
    /// nvCOMP library version.
    uint32_t version;
    /// Version of CUDA Runtime with which the nvCOMP library was built.
    uint32_t cudart_version;
} nvcompProperties_t;

/**
 * @brief Per-algorithm buffer alignment requirements.
 */
typedef struct
{
    /// Minimum alignment requirement of each input buffer.
    size_t input;
    /// Minimum alignment requirement of each output buffer.
    size_t output;
    /// Minimum alignment requirement of temporary-storage buffer, if any. For
    /// algorithms that do not use temporary storage, this field is always equal
    /// to 1.
    size_t temp;
} nvcompAlignmentRequirements_t;

#endif // NVCOMP_SHARED_TYPES_H
