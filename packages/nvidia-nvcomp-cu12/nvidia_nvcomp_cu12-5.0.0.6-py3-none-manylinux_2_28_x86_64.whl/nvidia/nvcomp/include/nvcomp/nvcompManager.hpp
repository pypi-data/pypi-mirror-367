/*
 * SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES.
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

#include <memory>
#include <vector>
#include <functional>

#include "nvcomp.hpp"

namespace nvcomp {

/**
 * @brief Custom allocator function type that receives a size in bytes to allocate
 * in device-accessible memory.
 */
using AllocFn_t = std::function<void*(size_t)>;

/**
 * @brief Custom deallocation function type that receives a memory pointer and size
 * in bytes to deallocate.
 */
using DeAllocFn_t = std::function<void(void*, size_t)>;

/**
 * @brief Enumeration that defines how a buffer gets compressed by an nvCOMP manager.
 */
enum class BitstreamKind {
  /// Each input buffer is chunked according to manager setting and compressed in parallel.
  /// Allows computation of checksums.
  /// Adds custom header with nvCOMP metadata at the beginning of the compressed data.
  NVCOMP_NATIVE = 0,
  /// Compresses input data as is, just using underlying compression algorithm.
  /// Does not add header with nvCOMP metadata.
  RAW = 1,
  /// Similar to RAW, but adds custom header with just uncompressed size at the beginning of the compressed data.
  WITH_UNCOMPRESSED_SIZE = 2,
};

/**
 * @brief Enumeration that defines the checksum policy used by an nvCOMP manager.
 */
enum ChecksumPolicy {
  /// During compression, do not compute checksums.
  /// During decompression, do not verify checksums.
  NoComputeNoVerify = 0,

  /// During compression, compute checksums.
  /// During decompression, do not attempt to verify checksums.
  ComputeAndNoVerify = 1,

  /// During compression, do not compute checksums.
  /// During decompression, verify checksums if they were included.
  NoComputeAndVerifyIfPresent = 2,

  /// During compression, compute checksums.
  /// During decompression, verify checksums if they were included.
  ComputeAndVerifyIfPresent = 3,

  /// During compression, compute checksums.
  /// During decompression, verify checksums.
  /// A runtime error will be thrown upon configure_decompression if
  /// checksums were not included in the compressed buffer.
  ComputeAndVerify = 4
};

#ifndef DOXYGEN_SHOULD_SKIP_THIS

namespace detail {

/**
 * @brief Internal memory pool used for compression / decompression configurations.
 */
template <typename T>
struct PinnedPtrPool;

} // namespace detail

#endif // DOXYGEN_SHOULD_SKIP_THIS

/**
 * @brief Configuration used to aggregate information about the compression of a particular buffer.
 */
struct CompressionConfig {

  // pimpl
  struct CompressionConfigImpl;
  std::shared_ptr<CompressionConfigImpl> impl;

  // API
  size_t uncompressed_buffer_size;
  size_t max_compressed_buffer_size;
  size_t num_chunks;
  bool compute_checksums;

  /**
   * @brief Default constructor that initializes members with default values.
   *
   * @note CompressionConfig should be retrieved via the \ref configure_compression
   * member function, and shouldn't be constructed directly.
   */
  NVCOMP_EXPORT
  CompressionConfig();

  /**
   * @brief Construct the CompressionConfig using an nvcompStatus_t memory pool and the
   * uncompressed buffer size.
   *
   * @note CompressionConfig should be retrieved via the \ref configure_compression
   * member function, and shouldn't be constructed directly.
   */
  NVCOMP_EXPORT
  CompressionConfig(detail::PinnedPtrPool<nvcompStatus_t>& pool, size_t uncompressed_buffer_size);

  /**
   * @brief Get the status of the overall compression.
   *
   * @note The data resides in pinned host memory.
   */
  NVCOMP_EXPORT
  nvcompStatus_t* get_status() const;

  NVCOMP_EXPORT
  CompressionConfig(CompressionConfig&& other);
  NVCOMP_EXPORT
  CompressionConfig(const CompressionConfig& other);
  NVCOMP_EXPORT
  CompressionConfig& operator=(CompressionConfig&& other);
  NVCOMP_EXPORT
  CompressionConfig& operator=(const CompressionConfig& other);

  NVCOMP_EXPORT
  ~CompressionConfig() noexcept;
};

/**
 * @brief Configuration used to aggregate information about a particular decompression.
 */
struct DecompressionConfig {

  // pimpl
  struct DecompressionConfigImpl;
  std::shared_ptr<DecompressionConfigImpl> impl;

  // API
  size_t decomp_data_size;
  size_t num_chunks;
  bool checksums_present;

  /**
  * @brief Default constructor that initializes members with default values.
  *
  * @note DecompressionConfig should be retrieved via the \ref configure_decompression
  * member function, and shouldn't be constructed directly.
  */
  NVCOMP_EXPORT
  DecompressionConfig();

  /**
   * @brief Construct the config given an nvcompStatus_t memory pool.
   *
   * @note DecompressionConfig should be retrieved via the \ref configure_decompression
   * member function, and shouldn't be constructed directly.
   */
  NVCOMP_EXPORT
  DecompressionConfig(detail::PinnedPtrPool<nvcompStatus_t>& pool);

  /**
   * @brief Get the status of the overall decompression.
   *
   * @note The data resides in pinned host memory.
   */
  NVCOMP_EXPORT
  nvcompStatus_t* get_status() const;

  NVCOMP_EXPORT
  DecompressionConfig(DecompressionConfig&& other);
  NVCOMP_EXPORT
  DecompressionConfig(const DecompressionConfig& other);
  NVCOMP_EXPORT
  DecompressionConfig& operator=(DecompressionConfig&& other);
  NVCOMP_EXPORT
  DecompressionConfig& operator=(const DecompressionConfig& other);

  NVCOMP_EXPORT
  ~DecompressionConfig() noexcept;
};

/**
 * @brief Abstract base class that defines the nvCOMP high-level interface
 *
 * @note This base class should not be directly constructed. One should rely on the
 * explicit manager constructors (e.g., \ref ANSManager), or the \ref create_manager factory function.
 */
struct nvcompManagerBase {
  /**
   * @brief Configure the compression of a single buffer.
   *
   * This routine computes the size of the required result buffer. The result config also
   * contains the nvcompStatus_t* that allows error checking.
   *
   * @param[in] uncomp_buffer_size The uncompressed input data size (in bytes).
   *
   * @return CompressionConfig for the size provided.
   */
  virtual CompressionConfig configure_compression(
    const size_t uncomp_buffer_size) = 0;

  /**
   * @brief Configure the compression of a batch of buffers.
   *
   * This routine computes the size of the required result buffer for each element of the batch.
   * The result config also contains the nvcompStatus_t* that allows error checking.
   *
   * @param[in] uncomp_buffer_sizes The vector of uncompressed input data sizes (in bytes) for each element of the batch.
   *
   * @return A vector with CompressionConfig for each of the size provided.
   */
  virtual std::vector<CompressionConfig> configure_compression(
    const std::vector<size_t>& uncomp_buffer_sizes) = 0;

  /**
   * @brief Perform compression asynchronously for a single buffer.
   *
   * @param[in] uncomp_buffer The uncompressed input data.
   * (a pointer to device continuous memory).
   *
   * @param[out] comp_buffer The location to output the compressed data to.
   * (a pointer to device continuous memory)
   * Size requirement is provided in CompressionConfig.
   *
   * @param[in] comp_config Generated for the current uncomp_buffer with configure_compression.
   *
   * @param[out] comp_size The location to output size in bytes after compression.
   * (a pointer to a single size_t variable on device)
   * Optional when bitstream kind is NVCOMP_NATIVE.
   */
  virtual void compress(
    const uint8_t* uncomp_buffer,
    uint8_t* comp_buffer,
    const CompressionConfig& comp_config,
    size_t* comp_size = nullptr) = 0;

  /**
   * @brief Perform compression asynchronously for a batch of buffers.
   * Batch size is inferred from comp_configs size.
   *
   * @param[in] uncomp_buffers The uncompressed input data.
   * (a pointer to a host array of pointers to device continuous memory)
   *
   * @param[out] comp_buffers The location to output the compressed data to.
   * (a pointer to a host array of pointers to device continuous memory)
   * Size requirement is provided in CompressionConfig.
   *
   * @param[in] comp_configs Generated for the current uncomp_buffers with configure_compression.
   *
   * @param[out] comp_sizes The location to output size in bytes after compression.
   * (a pointer to a device array, with size enough to contain batch_size elements of type size_t)
   * Optional when bitstream kind is NVCOMP_NATIVE.
   */
  virtual void compress(
    const uint8_t * const * uncomp_buffers,
    uint8_t * const * comp_buffers,
    const std::vector<CompressionConfig>& comp_configs,
    size_t* comp_sizes = nullptr) = 0;

  /**
   * @brief Configure the decompression for a single buffer using a compressed buffer.
   *
   * Synchronizes the user stream.
   * - If bitstream kind is NVCOMP_NATIVE, it will parse the header in comp_buffer.
   * - If bitstream kind is RAW, it may be required (e.g for LZ4) to parse the whole comp_buffer,
   *   which could be significantly slower that other options.
   * - If bitstream kind is WITH_UNCOMPRESSED_SIZE, it will read the size from the beginning of the comp_buffer.
   *
   * @param[in] comp_buffer The compressed input data.
   * (a pointer to device continuous memory)
   *
   * @param[in] comp_size Size of the compressed input data. This is required only for RAW format.
   * (a pointer to device variable with compressed size)
   *
   * @return DecompressionConfig for the comp_buffer provided.
   */
  virtual DecompressionConfig configure_decompression(
    const uint8_t* comp_buffer,
    const size_t* comp_size = nullptr) = 0;

  /**
   * @brief Configure the decompression for a batch of buffers using a compressed buffer.
   *
   * Synchronizes the user stream.
   * - If bitstream kind is NVCOMP_NATIVE, it will parse the header in comp_buffers.
   * - If bitstream kind is RAW, it may be required (e.g for LZ4) to parse the whole comp_buffers,
   *   which could be significantly slower that other options.
   * - If bitstream kind is WITH_UNCOMPRESSED_SIZE, it will read the size from the beginning of the comp_buffers.
   *
   * @param[in] comp_buffers The compressed input data.
   * (a pointer to host arrays of pointers to device continuous memory)
   *
   * @param[in] batch_size The size of the batch.
   *
   * @param[in] comp_sizes Size of the compressed input data.
   * (a pointer to device array)
   * This is required only for RAW format.
   *
   * @return A vector of DecompressionConfig for each of the comp_buffer provided.
   */
  virtual std::vector<DecompressionConfig> configure_decompression(
    const uint8_t* const * comp_buffers,
    size_t batch_size,
    const size_t* comp_sizes = nullptr) = 0;

  /**
   * @brief Configure the decompression for a single buffer using a CompressionConfig object.
   *
   * Does not synchronize the user stream.
   *
   * @param[in] comp_config The config used to compress a buffer.
   *
   * @return DecompressionConfig based on compression config provided.
   */
  virtual DecompressionConfig configure_decompression(
    const CompressionConfig& comp_config) = 0;

  /**
   * @brief Configure the decompression for a batch of buffers using a CompressionConfig objects.
   *
   * Does not synchronize the user stream.
   *
   * @param[in] comp_configs A vector of configs used to compress a batch of buffers.
   *
   * @return A vector of DecompressionConfig based on compression configs provided.
   */
  virtual std::vector<DecompressionConfig> configure_decompression(
    const std::vector<CompressionConfig>& comp_configs) = 0;

  /**
   * @brief Perform decompression asynchronously of a single buffer.
   *
   * @param[out] decomp_buffer The location to output the decompressed data to.
   * (a pointer to device continuous memory)
   * Size requirement is provided in DecompressionConfig.
   *
   * @param[in] comp_buffer The compressed input data.
   * (a pointer to device continuous memory)
   *
   * @param[in] decomp_config Resulted from configure_decompression given this comp_buffer.
   * Contains nvcompStatus_t* in host/device-accessible memory to allow error checking.
   *
   * @param[in] comp_size The size of compressed input data passed.
   * (a pointer to a single size_t variable on device)
   * Optional when bitstream kind is NVCOMP_NATIVE.
   */
  virtual void decompress(
    uint8_t* decomp_buffer,
    const uint8_t* comp_buffer,
    const DecompressionConfig& decomp_config,
    size_t* comp_size = nullptr) = 0;

  /**
   * @brief Perform decompression asynchronously of a batch of buffers.
   *
   * @param[out] decomp_buffers The location to output the decompressed data to.
   * (a pointer to a host array of pointers to device continuous memory)
   * Size requirement is provided in DecompressionConfig.
   *
   * @param[in] comp_buffers The compressed input data.
   * (a pointer to a host array of pointers to device continuous memory with uncompressed data)
   *
   * @param[in] decomp_configs Resulted from configure_decompression given this comp_buffers.
   * Contains nvcompStatus_t* in host/device-accessible memory to allow error checking.
   *
   * @param[in] comp_sizes The size of compressed input data passed.
   * (a pointer to a device array, with size enough to contain batch_size elements of type size_t)
   * Optional when bitstream kind is NVCOMP_NATIVE.
   */
  virtual void decompress(
    uint8_t * const * decomp_buffers,
    const uint8_t * const * comp_buffers,
    const std::vector<DecompressionConfig>& decomp_configs,
    const size_t* comp_sizes = nullptr) = 0;

  /**
   * @brief Allows the user to provide a function for allocating / deallocating memory
   *
   * The manager requires scratch memory to perform its operations.
   * By default, it will use internal allocators which make use of
   * cudaMallocAsync / cudaFreeAsync
   * The user can override the allocation functions with this API.
   * The required signatures are
   *   void* alloc_fn(size_t alloc_size)
   * and
   *   void dealloc_fn(void* buffer, size_t alloc_size)
   *
   * This API copies the allocation functions. The copied functions must be valid until
   * either
   *  1) deallocate_gpu_mem() is called or
   *  2) the nvcompManager instance is destroyed
   *
   * If a scratch buffer was previously allocated, it is first deallocated using the prior
   * dealloc_fn (or cudaFreeAsync if one wasn't previously provided)
   *
   * @param[in] alloc_fn The host function to use to alloc a new scratch result buffer.
   * @param[in] dealloc_fn The host function to use to dealloc a scratch result buffer.
   *
   */
  virtual void set_scratch_allocators(
    const AllocFn_t& alloc_fn,
    const DeAllocFn_t& dealloc_fn) = 0;

  /**
   * @brief Computes the compressed output size (in bytes) of a given buffer.
   *
   * Synchronously copies the size of the compressed buffer to a host variable for return.
   *
   * Can only be used with NVCOMP_NATIVE bitstream kind.
   *
   * To obtain compressed sizes one can also cudaMemcpy sizes from comp_sizes passed to compress function.
   *
   * @param[in] comp_buffer The compressed input data.
   * (a pointer to device continuous memory)
   *
   * @return Size of the compressed buffer.
   */
  virtual size_t get_compressed_output_size(
    const uint8_t* comp_buffer) = 0;

  /**
   * @brief Computes the compressed output size (in bytes) of a given batch of buffers.
   *
   * Synchronously copies the size of the compressed buffer to a host variable for return.
   *
   * Can only be used with NVCOMP_NATIVE bitstream kind.
   *
   * To obtain compressed sizes one can also cudaMemcpy sizes from comp_sizes passed to compress function.
   *
   * @param[in] comp_buffers The compressed input data.
   * (a pointer host array of pointers to device continuous memory)
   *
   * @return A vector with sizes of each compressed buffer in the batch.
   */
  virtual std::vector<size_t> get_compressed_output_size(
    const uint8_t * const * comp_buffers,
    size_t batch_size) = 0;

  /**
   * @brief Frees any internal GPU memory used by the nvCOMP HLIF
   *
   * Returns this memory back through the deallocator if one was specified through set_scratch_allocators()
  */
  virtual void deallocate_gpu_mem() = 0;

  /**
   * @brief Destructor of the base classs.
   */
  virtual ~nvcompManagerBase() noexcept = default;
};

#ifndef DOXYGEN_SHOULD_SKIP_THIS

namespace detail {

/**
 * @brief Internal nvcompManager base class for the high-level interface.
 */
struct nvcompManagerInternalBase;

/**
 * @brief Interface class between nvcompManagerBase and the algorithm-specific implementation class.
 *
 * @note This base class should not be directly constructed.
 */
struct
#if !defined(_WIN32)
NVCOMP_EXPORT
#endif
PimplManager : nvcompManagerBase {

  // pimpl
  std::unique_ptr<nvcompManagerInternalBase> impl;

  PimplManager() noexcept = default;

  PimplManager(const PimplManager&) = delete;

  virtual ~PimplManager() noexcept = default;

  PimplManager& operator=(const PimplManager&) = delete;

  NVCOMP_EXPORT
  CompressionConfig configure_compression(
    const size_t uncomp_buffer_size) override;

  NVCOMP_EXPORT
  std::vector<CompressionConfig> configure_compression(
    const std::vector<size_t>& uncomp_buffer_sizes) override;

  NVCOMP_EXPORT
  void compress(
    const uint8_t* uncomp_buffer,
    uint8_t* comp_buffer,
    const CompressionConfig& comp_config,
    size_t* comp_size = nullptr) override;

  NVCOMP_EXPORT
  void compress(
    const uint8_t * const * uncomp_buffers,
    uint8_t * const * comp_buffers,
    const std::vector<CompressionConfig>& comp_configs,
    size_t* comp_sizes = nullptr) override;

  NVCOMP_EXPORT
  DecompressionConfig configure_decompression(
    const uint8_t* comp_buffer,
    const size_t* comp_size = nullptr) override;

  NVCOMP_EXPORT
  std::vector<DecompressionConfig> configure_decompression(
    const uint8_t* const * comp_buffers,
    size_t batch_size,
    const size_t* comp_sizes = nullptr) override;

  NVCOMP_EXPORT
  DecompressionConfig configure_decompression(
    const CompressionConfig& comp_config) override;

  NVCOMP_EXPORT
  std::vector<DecompressionConfig> configure_decompression(
    const std::vector<CompressionConfig>& comp_configs) override;

  NVCOMP_EXPORT
  void decompress(
    uint8_t* decomp_buffer,
    const uint8_t* comp_buffer,
    const DecompressionConfig& decomp_config,
    size_t* comp_size = nullptr) override;

  NVCOMP_EXPORT
  void decompress(
    uint8_t * const * decomp_buffers,
    const uint8_t * const * comp_buffers,
    const std::vector<DecompressionConfig>& decomp_configs,
    const size_t* comp_sizes = nullptr) override;

  NVCOMP_EXPORT
  void set_scratch_allocators(
    const AllocFn_t& alloc_fn,
    const DeAllocFn_t& dealloc_fn) override;

  NVCOMP_EXPORT
  size_t get_compressed_output_size(
    const uint8_t* comp_buffer) override;

  NVCOMP_EXPORT
  std::vector<size_t> get_compressed_output_size(
    const uint8_t * const * comp_buffers,
    size_t batch_size) override;

  NVCOMP_EXPORT
  void deallocate_gpu_mem() override;
};

} // namespace detail

#endif // DOXYGEN_SHOULD_SKIP_THIS

} // namespace nvcomp
