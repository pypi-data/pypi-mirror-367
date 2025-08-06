/*
 * SPDX-FileCopyrightText: Copyright (c) 2017-2025 NVIDIA CORPORATION & AFFILIATES.
 * All rights reserved. SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
*/

#ifndef NVCOMP_DEFLATE_H
#define NVCOMP_DEFLATE_H

#include "nvcomp.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Deflate compression options for the low-level API
 */
typedef struct
{
  /**
   * @brief Deflate algorithm options.
   *
   * - 0: highest-throughput, entropy-only compression (use for symmetric compression/decompression performance)
   * - 1: high-throughput, low compression ratio (default)
   * - 2: medium-througput, medium compression ratio, beat Zlib level 1 on the compression ratio
   * - 3: placeholder for further compression level support, will fall into MEDIUM_COMPRESSION at this point
   * - 4: lower-throughput, higher compression ratio, beat Zlib level 6 on the compression ratio
   * - 5: lowest-throughput, highest compression ratio
   */
  int algorithm;
  /**
   * @brief These bytes are unused and must be zeroed. This ensures
   *        compatibility if additional fields are added in the future.
   */
  char reserved[60];
} nvcompBatchedDeflateCompressOpts_t;

/**
 * @brief Deflate decompression options for the low-level API
 */
typedef struct {
  /**
   * @brief Decompression backend to use.
   */
  nvcompDecompressBackend_t backend;
  /**
   * @brief Whether to sort chunks before hardware decompression for better load balancing.
   *        Only used when the backend is the hardware decompression engine.
   */
  int sort_before_hw_decompress;
  /**
   * @brief These bytes are unused and must be zeroed. This ensures
   *        compatibility if additional fields are added in the future.
   */
  char reserved[56];
} nvcompBatchedDeflateDecompressOpts_t;

/**
 * @brief Default Deflate compression options
 */
static const nvcompBatchedDeflateCompressOpts_t nvcompBatchedDeflateCompressDefaultOpts = {1, {0}};

/**
 * @brief Default Deflate decompression options
 */
static const nvcompBatchedDeflateDecompressOpts_t nvcompBatchedDeflateDecompressDefaultOpts =
    {NVCOMP_DECOMPRESS_BACKEND_DEFAULT, 0 /* sort_before_hw_decompress */, {0}};

/**
 * @brief The maximum supported uncompressed chunk size in bytes for the Deflate compressor.
 *
 * @note Although chunk sizes up to 2GB are theoretically possible, compression
 * with large chunks may be very slow or use large amounts of temporary memory,
 * so caution is advised when using chunk sizes above 64KB.
 */
static const size_t nvcompDeflateCompressionMaxAllowedChunkSize = 1u << 31;

/**
 * @brief The most restrictive of the minimum alignment requirements for void-type CUDA memory buffers
 * used for input, output, or temporary memory, passed to compression functions.
 *
 * @note In all cases, typed memory buffers must still be aligned to their type's size,
 * e.g., 4 bytes for `int`.
 */
static const size_t nvcompDeflateRequiredCompressionAlignment = 8;

/**
 * @brief Get the minimum buffer alignment requirements for compression.
 *
 * @note Providing buffers with alignments above the minimum requirements
 * (e.g., 16- or 32-byte alignment) may help improve performance.
 *
 * @param[in] compress_opts Compression options.
 * @param[out] alignment_requirements The minimum buffer alignment requirements
 * for compression.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateCompressGetRequiredAlignments(
    nvcompBatchedDeflateCompressOpts_t compress_opts,
    nvcompAlignmentRequirements_t* alignment_requirements);

/**
 * @brief Get the amount of temporary memory required on the GPU for compression
 * asynchronously.
 *
 * @param[in] num_chunks The number of chunks of memory in the batch.
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk in the
 * batch.
 * @param[in] compress_opts Compression options.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily
 * required during compression. The value is returned on the host side.
 * @param[in] max_total_uncompressed_bytes Upper bound on the total uncompressed
 * size of all chunks
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateCompressGetTempSizeAsync(
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedDeflateCompressOpts_t compress_opts,
    size_t* temp_bytes,
    size_t max_total_uncompressed_bytes);

/**
 * @brief Get the amount of temporary memory required on the GPU for compression.
 * synchronously.
 *
 * @param[in] device_uncompressed_chunk_ptrs Array with size \p num_chunks of pointers
 * to the uncompressed data chunks. Both the pointers and the uncompressed data
 * should reside in device-accessible memory.
 * Each chunk must be aligned to the value in the `input` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateCompressGetRequiredAlignments` when called with the same
 * \p compress_opts.
 * @param[in] device_uncompressed_chunk_bytes Array with size \p num_chunks of
 * sizes of the uncompressed chunks in bytes.
 * The sizes should reside in device-accessible memory.
 * @param[in] num_chunks The number of chunks of memory in the batch.
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk in the
 * batch.
 * @param[in] compress_opts Compression options.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily
 * required during compression. The value is returned on the host side.
 * @param[in] max_total_uncompressed_bytes Upper bound on the total uncompressed
 * size of all chunks
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateCompressGetTempSizeSync(
    const void* const* const device_uncompressed_chunk_ptrs,
    const size_t* const device_uncompressed_chunk_bytes,
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedDeflateCompressOpts_t compress_opts,
    size_t* temp_bytes,
    size_t max_total_uncompressed_bytes,
    cudaStream_t stream);

/**
 * @brief Get the maximum size that a chunk of size at most max_uncompressed_chunk_bytes
 * could compress to. That is, the minimum amount of output memory required to be given
 * \ref nvcompBatchedDeflateCompressAsync for each chunk.
 *
 * @note For best performance, a chunk size of 65536 bytes is recommended.
 *
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk before compression.
 * @param[in] compress_opts The Deflate compression options to use.
 * @param[out] max_compressed_chunk_bytes The maximum possible compressed size of the chunk.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateCompressGetMaxOutputChunkSize(
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedDeflateCompressOpts_t compress_opts,
    size_t* max_compressed_chunk_bytes);

/**
 * @brief Perform batched asynchronous compression.
 *
 * @note For best performance, a chunk size of 65536 bytes is recommended.
 * Violating any of the conditions listed in the parameter descriptions
 * below may result in undefined behaviour.
 *
 * @param[in] device_uncompressed_chunk_ptrs Array with size \p num_chunks of pointers
 * to the uncompressed data chunks. Both the pointers and the uncompressed data
 * should reside in device-accessible memory.
 * Each chunk must be aligned to the value in the `input` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateCompressGetRequiredAlignments` when called with the same
 * \p compress_opts.
 * @param[in] device_uncompressed_chunk_bytes Array with size \p num_chunks of
 * sizes of the uncompressed chunks in bytes.
 * The sizes should reside in device-accessible memory.
 * Chunk sizes must not exceed 65536 bytes. For best performance, a chunk size
 * of 65536 bytes is recommended.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest uncompressed chunk.
 * @param[in] num_chunks Number of chunks of data to compress.
 * @param[in] device_temp_ptr The temporary GPU workspace.
 * Must be aligned to the value in the `temp` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateCompressGetRequiredAlignments` when called with the same
 * \p compress_opts.
 * @param[in] temp_bytes The size of the temporary GPU memory pointed to by
 * `device_temp_ptr`.
 * @param[out] device_compressed_chunk_ptrs Array with size \p num_chunks of pointers
 * to the output compressed buffers. Both the pointers and the compressed
 * buffers should reside in device-accessible memory. Each compressed buffer
 * should be preallocated with the size given by
 * `nvcompBatchedDeflateCompressGetMaxOutputChunkSize`.
 * Each compressed buffer must be aligned to the value in the `output` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateCompressGetRequiredAlignments` when called with the same
 * \p compress_opts.
 * @param[out] device_compressed_chunk_bytes Array with size \p num_chunks,
 * to be filled with the compressed sizes of each chunk.
 * The buffer should be preallocated in device-accessible memory.
 * @param[in] compress_opts The Deflate compression options to use.
 * @param[out] device_statuses Array with size \p num_chunks of statuses in
 * device-accessible memory. This argument needs to be preallocated. For each
 * chunk, if the compression is successful, the status will be set to
 * `nvcompSuccess`, and an error code otherwise.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successfully launched, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateCompressAsync(
    const void* const* device_uncompressed_chunk_ptrs,
    const size_t* device_uncompressed_chunk_bytes,
    size_t max_uncompressed_chunk_bytes,
    size_t num_chunks,
    void* device_temp_ptr,
    size_t temp_bytes,
    void* const* device_compressed_chunk_ptrs,
    size_t* device_compressed_chunk_bytes,
    nvcompBatchedDeflateCompressOpts_t compress_opts,
    nvcompStatus_t* device_statuses,
    cudaStream_t stream);

/**
 * @brief The most restrictive of the minimum alignment requirements for void-type CUDA memory buffers
 * used for input, output, or temporary memory, passed to decompression functions.
 *
 * @note In all cases, typed memory buffers must still be aligned to their type's size,
 * e.g., 4 bytes for `int`.
 */
static const size_t nvcompDeflateRequiredDecompressionAlignment = 4;

/**
 * @brief Get the minimum buffer alignment requirements for decompression.
 *
 * @note Providing buffers with alignments above the minimum requirements
 * (e.g., 16- or 32-byte alignment) may help improve performance.
 *
 * @param[in] decompress_opts Decompression options.
 * @param[out] alignment_requirements The minimum buffer alignment requirements
 * for decompression.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateDecompressGetRequiredAlignments(
    nvcompBatchedDeflateDecompressOpts_t decompress_opts,
    nvcompAlignmentRequirements_t* alignment_requirements);

/**
 * @brief Get the amount of temporary memory required on the GPU for decompression
 * asynchronously.
 *
 * @param[in] num_chunks Number of chunks of data to be decompressed.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest chunk in bytes
 * when uncompressed.
 * @param[in] decompress_opts Decompression options.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily required
 * during decompression. The value is returned on the host side.
 * @param[in] max_total_uncompressed_bytes The total decompressed size of all the chunks.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateDecompressGetTempSizeAsync(
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedDeflateDecompressOpts_t decompress_opts,
    size_t* temp_bytes,
    size_t max_total_uncompressed_bytes);

/**
 * @brief Get the amount of temporary memory required on the GPU for decompression
 * synchronously.
 *
 * @param[in] device_compressed_chunk_ptrs Array with size \p num_chunks of pointers
 * in device-accessible memory to device-accessible compressed buffers.
 * Each chunk must be aligned to the value in the `input` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateDecompressGetRequiredAlignments`.
 * @param[in] device_compressed_chunk_bytes Array with size \p num_chunks of sizes of
 * the compressed buffers in bytes. The sizes should reside in device-accessible memory.
 * @param[in] num_chunks Number of chunks of data to be decompressed.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest chunk in bytes
 * when uncompressed.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily required
 * during decompression. The value is returned on the host side.
 * @param[in] max_total_uncompressed_bytes  The total decompressed size of all the chunks.
 * @param[in] decompress_opts Decompression options.
 * @param[out] device_statuses Array with size \p num_chunks of statuses in
 * device-accessible memory. This argument needs to be preallocated. For each
 * chunk, if the data can be parsed successfully, the status will be set to
 * `nvcompSuccess`, and an error code otherwise.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateDecompressGetTempSizeSync(
    const void* const* const device_compressed_chunk_ptrs,
    const size_t* const device_compressed_chunk_bytes,
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    size_t* temp_bytes,
    size_t max_total_uncompressed_bytes,
    nvcompBatchedDeflateDecompressOpts_t decompress_opts,
    nvcompStatus_t* device_statuses,
    cudaStream_t stream);

/**
 * @brief Asynchronously compute the number of bytes of uncompressed data for
 * each compressed chunk.
 *
 * This is needed when we do not know the expected output size.
 *
 * @note If the stream is corrupt, the calculated sizes will be invalid.
 *
 * @note Violating any of the conditions listed in the parameter descriptions
 * below may result in undefined behaviour.
 *
 * @param[in] device_compressed_chunk_ptrs Array with size \p num_chunks of
 * pointers in device-accessible memory to compressed buffers.
 * Each chunk must be aligned to the value in the `input` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateDecompressGetRequiredAlignments`.
 * @param[in] device_compressed_chunk_bytes Array with size \p num_chunks of sizes
 * of the compressed buffers in bytes. The sizes should reside in device-accessible memory.
 * @param[out] device_uncompressed_chunk_bytes Array with size \p num_chunks
 * to be filled with the sizes, in bytes, of each uncompressed data chunk.
 * @param[in] num_chunks Number of data chunks to compute sizes of.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateGetDecompressSizeAsync(
    const void* const* device_compressed_chunk_ptrs,
    const size_t* device_compressed_chunk_bytes,
    size_t* device_uncompressed_chunk_bytes,
    size_t num_chunks,
    cudaStream_t stream);

/**
 * @brief Perform batched asynchronous decompression.
 *
 * @note Violating any of the conditions listed in the parameter descriptions
 * below may result in undefined behaviour.
 *
 * @param[in] device_compressed_chunk_ptrs Array with size \p num_chunks of pointers
 * in device-accessible memory to device-accessible compressed buffers.
 * Each chunk must be aligned to the value in the `input` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateDecompressGetRequiredAlignments`.
 * @param[in] device_compressed_chunk_bytes Array with size \p num_chunks of sizes of
 * the compressed buffers in bytes. The sizes should reside in device-accessible memory.
 * @param[in] device_uncompressed_buffer_bytes Array with size \p num_chunks of sizes,
 * in bytes, of the output buffers to be filled with uncompressed data for each chunk.
 * The sizes should reside in device-accessible memory. If a
 * size is not large enough to hold all decompressed data, the decompressor
 * will set the status in \p device_statuses corresponding to the
 * overflow chunk to `nvcompErrorCannotDecompress`.
 * @param[out] device_uncompressed_chunk_bytes Array with size \p num_chunks to
 * be filled with the actual number of bytes decompressed for every chunk.
 * This argument needs to be preallocated.
 * When `NVCOMP_DECOMPRESS_BACKEND_HARDWARE` is specified in \p decompress_opts.backend,
 * this parameter is required. For `NVCOMP_DECOMPRESS_BACKEND_CUDA`, it is optional
 * and may be set to NULL if reporting the actual sizes is not necessary.
 * @param[in] num_chunks Number of chunks of data to decompress.
 * @param[in] device_temp_ptr The temporary GPU space.
 * Must be aligned to the value in the `temp` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateDecompressGetRequiredAlignments`.
 * @param[in] temp_bytes The size of the temporary GPU space.
 * @param[out] device_uncompressed_chunk_ptrs Array with size \p num_chunks of
 * pointers in device-accessible memory to decompressed data. Each uncompressed
 * buffer needs to be preallocated in device-accessible memory, have the size
 * specified by the corresponding entry in \p device_uncompressed_buffer_bytes,
 * and be aligned to the value in the `output` member of the
 * \ref nvcompAlignmentRequirements_t object output by
 * `nvcompBatchedDeflateDecompressGetRequiredAlignments`.
 * @param[in] decompress_opts Decompression options.
 * @param[out] device_statuses Array with size \p num_chunks of statuses in
 * device-accessible memory. This argument needs to be preallocated. For each
 * chunk, if the decompression is successful, the status will be set to
 * `nvcompSuccess`. If the decompression is not successful, for example due to
 * the corrupted input or out-of-bound errors, the status will be set to
 * `nvcompErrorCannotDecompress`.
 * Can be NULL if desired, in which case error status is not reported.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successfully launched, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedDeflateDecompressAsync(
    const void* const* device_compressed_chunk_ptrs,
    const size_t* device_compressed_chunk_bytes,
    const size_t* device_uncompressed_buffer_bytes,
    size_t* device_uncompressed_chunk_bytes,
    size_t num_chunks,
    void* const device_temp_ptr,
    size_t temp_bytes,
    void* const* device_uncompressed_chunk_ptrs,
    nvcompBatchedDeflateDecompressOpts_t decompress_opts,
    nvcompStatus_t* device_statuses,
    cudaStream_t stream);

#ifdef __cplusplus
}
#endif

#endif // NVCOMP_DEFLATE_H
