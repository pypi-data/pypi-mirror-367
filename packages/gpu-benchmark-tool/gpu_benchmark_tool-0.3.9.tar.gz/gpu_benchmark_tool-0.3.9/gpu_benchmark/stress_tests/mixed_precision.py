"""Mixed precision stress tests.

This module provides tests for mixed precision (FP16, BF16) and tensor core performance on GPUs.
"""

import torch
import time
from typing import Dict
import numpy as np


class MixedPrecisionTest:
    """Test mixed precision capabilities and tensor core performance.

    Args:
        device (torch.device): The device (CPU or GPU) to run tests on.
    """
    
    def __init__(self, device: torch.device):
        self.device = device
        
    def run_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests FP32, FP16, BF16, and INT8 performance and speedup."""
        size = 2048 if self.device.type == "cuda" else 256
        results = {}
        
        # Check hardware support first
        fp16_hardware_supported = self._check_fp16_hardware_support()
        bf16_hardware_supported = self._check_bf16_hardware_support()
        int8_hardware_supported = self._check_int8_hardware_support()
        
        # FP32 test (always supported)
        results["fp32"] = self._test_precision(
            torch.float32, size, duration / 4
        )
        
        # FP16 test
        if fp16_hardware_supported:
            fp16_result = self._test_precision(torch.float16, size, duration / 4)
            fp16_result["hardware_supported"] = True
            fp16_result["runtime_supported"] = fp16_result.get("supported", False)
            results["fp16"] = fp16_result
        else:
            results["fp16"] = {
                "hardware_supported": False,
                "runtime_supported": False,
                "supported": False
            }
            
        # BF16 test (for newer GPUs)
        if bf16_hardware_supported:
            bf16_result = self._test_precision(torch.bfloat16, size, duration / 4)
            bf16_result["hardware_supported"] = True
            bf16_result["runtime_supported"] = bf16_result.get("supported", False)
            results["bf16"] = bf16_result
        else:
            results["bf16"] = {
                "hardware_supported": False,
                "runtime_supported": False,
                "supported": False
            }
            
        # INT8 test with TensorRT
        if int8_hardware_supported:
            int8_result = self._test_int8_with_tensorrt(size, duration / 4)
            int8_result["hardware_supported"] = True
            
            # If TensorRT fails, try PyTorch INT8 as fallback
            if not int8_result.get("runtime_supported", False):
                error_msg = int8_result.get("error", "Unknown TensorRT error")
                print(f"TensorRT INT8 failed ({error_msg}), trying PyTorch INT8 fallback...")
                pytorch_int8_result = self._test_precision(torch.int8, size, duration / 4)
                if pytorch_int8_result.get("supported", False):
                    int8_result = pytorch_int8_result
                    int8_result["hardware_supported"] = True
                    int8_result["runtime_supported"] = True
                    int8_result["method"] = "pytorch_fallback"
                    int8_result["note"] = f"TensorRT failed ({error_msg}), using PyTorch INT8"
                else:
                    int8_result["note"] = f"Both TensorRT and PyTorch INT8 failed. TensorRT error: {error_msg}"
            
            results["int8"] = int8_result
        else:
            results["int8"] = {
                "hardware_supported": False,
                "runtime_supported": False,
                "supported": False
            }
        
        # Calculate speedups
        if results["fp32"].get("iterations", 0) > 0:
            if results.get("fp16", {}).get("runtime_supported"):
                results["fp16_speedup"] = (
                    results["fp16"]["iterations"] / results["fp32"]["iterations"]
                )
            if results.get("bf16", {}).get("runtime_supported"):
                results["bf16_speedup"] = (
                    results["bf16"]["iterations"] / results["fp32"]["iterations"]
                )
            if results.get("int8", {}).get("runtime_supported"):
                results["int8_speedup"] = (
                    results["int8"]["iterations"] / results["fp32"]["iterations"]
                )
        
        # Determine mixed precision capability
        results["mixed_precision_ready"] = (
            results.get("fp16", {}).get("runtime_supported", False) or
            results.get("bf16", {}).get("runtime_supported", False) or
            results.get("int8", {}).get("runtime_supported", False)
        )
        return results
    
    def _test_precision(self, dtype: torch.dtype, size: int, duration: float) -> Dict[str, any]:
        """Tests performance for a specific precision.

        Args:
            dtype (torch.dtype): Data type to test (e.g., torch.float16).
            size (int): Matrix dimension.
            duration (float): Duration of the test in seconds.

        Returns:
            Dict[str, any]: Dictionary with support, iterations, average time, and dtype.
        """
        try:
            # Handle INT8 differently - use quantized tensors
            if dtype == torch.int8:
                # Create float tensors first, then quantize
                a_float = torch.randn((size, size), device=self.device, dtype=torch.float32)
                b_float = torch.randn((size, size), device=self.device, dtype=torch.float32)
                
                # Quantize to INT8
                a = torch.quantize_per_tensor(a_float, scale=0.1, zero_point=0, dtype=torch.qint8)
                b = torch.quantize_per_tensor(b_float, scale=0.1, zero_point=0, dtype=torch.qint8)
            else:
                # Regular tensor creation for other dtypes
                a = torch.randn((size, size), device=self.device, dtype=dtype)
                b = torch.randn((size, size), device=self.device, dtype=dtype)
            
            start_time = time.time()
            iterations = 0
            
            while time.time() - start_time < duration:
                c = torch.matmul(a, b)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                iterations += 1
            
            elapsed = time.time() - start_time
            
            # Calculate FLOPs for this precision
            flops_per_iter = 2 * size**3  # Matrix multiply FLOPs
            total_flops = flops_per_iter * iterations
            tflops = (total_flops / elapsed) / 1e12 if elapsed > 0 else 0
            
            return {
                "supported": True,
                "iterations": iterations,
                "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
                "dtype": str(dtype),
                "tflops": tflops,
                "matrix_size": size
            }
            
        except Exception as e:
            return {
                "supported": False,
                "error": str(e)
            }
    
    def _check_fp16_hardware_support(self):
        """Checks if FP16 (half precision) hardware is supported on this device.
        
        FP16 support is typically available on NVIDIA GPUs with compute capability 5.3+.
        
        Returns:
            bool: True if FP16 hardware is supported, False otherwise.
        """
        if self.device.type == "cpu":
            return False
        try:
            import torch
            device_index = self.device.index if hasattr(self.device, 'index') else self.device
            cc = torch.cuda.get_device_capability(device_index)
            return cc[0] >= 5
        except Exception:
            pass
        return False
    
    def _check_bf16_hardware_support(self):
        """Checks if BF16 (bfloat16) hardware is supported on this device.
        
        BF16 support is typically available on newer GPUs (Ampere, Ada Lovelace, etc.).
        
        Returns:
            bool: True if BF16 hardware is supported, False otherwise.
        """
        if self.device.type == "cpu":
            return False
        try:
            import torch
            device_index = self.device.index if hasattr(self.device, 'index') else self.device
            cc = torch.cuda.get_device_capability(device_index)
            return cc[0] >= 8
        except Exception:
            pass
        return False
    
    def _check_int8_hardware_support(self):
        """Check if INT8 quantization hardware is supported on this device.
        
        INT8 support varies by GPU architecture and is generally available on 
        compute capability 6.1+ (Pascal and newer).
        
        Returns:
            bool: True if INT8 hardware is supported, False otherwise.
        """
        if self.device.type == "cpu":
            return False
        try:
            import torch
            device_index = self.device.index if hasattr(self.device, 'index') else self.device
            cc = torch.cuda.get_device_capability(device_index)
            # INT8 support varies by GPU architecture
            # Generally available on compute capability 6.1+ (Pascal and newer)
            return cc[0] >= 6 and cc[1] >= 1
        except Exception:
            pass
        return False
    
    def _test_int8_with_tensorrt(self, size: int, duration: float) -> Dict[str, any]:
        """Tests INT8 performance using TensorRT.
        
        Args:
            size (int): Matrix dimension.
            duration (float): Duration of the test in seconds.
            
        Returns:
            Dict[str, any]: Dictionary with INT8 support and performance metrics.
        """
        try:
            import tensorrt as trt
            import numpy as np
            import pycuda.driver as cuda
            
            # Check TensorRT version for compatibility
            trt_version = trt.__version__
            print(f"TensorRT version: {trt_version}")
            
            # Create TensorRT builder and network
            builder = trt.Builder(trt.Logger(trt.Logger.WARNING))
            
            # Handle different TensorRT versions for network creation
            try:
                network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
            except AttributeError:
                # Newer TensorRT versions
                network = builder.create_network()
            
            # Create input tensors with dynamic range
            input_a = network.add_input("input_a", trt.DataType.INT8, (size, size))
            input_b = network.add_input("input_b", trt.DataType.INT8, (size, size))
            
            # Set dynamic range for INT8 inputs (required for TensorRT 10+)
            try:
                input_a.set_dynamic_range(-128, 127)
                input_b.set_dynamic_range(-128, 127)
            except AttributeError:
                # Older TensorRT versions don't have set_dynamic_range
                pass
            
            # Add matrix multiplication layer
            matmul = network.add_matrix_multiply(
                input_a, trt.MatrixOperation.NONE,
                input_b, trt.MatrixOperation.NONE
            )
            output = matmul.get_output(0)
            try:
                output.set_dynamic_range(-32768, 32767)  # INT32 output range
            except AttributeError:
                # Older TensorRT versions don't have set_dynamic_range
                pass
            network.mark_output(output)
            
            # Build engine
            config = builder.create_builder_config()
            # Handle different TensorRT versions
            try:
                config.max_workspace_size = 1 << 30  # 1GB (older versions)
            except AttributeError:
                config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB (newer versions)
            
            # Handle different TensorRT versions for build_engine
            try:
                engine = builder.build_engine(network, config)
            except AttributeError:
                # Newer TensorRT versions use build_serialized_network
                serialized_engine = builder.build_serialized_network(network, config)
                runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
                engine = runtime.deserialize_cuda_engine(serialized_engine)
            
            if engine is None:
                return {
                    "hardware_supported": True,
                    "runtime_supported": False,
                    "supported": False,
                    "error": "TensorRT engine build failed",
                    "method": "tensorrt"
                }
            
            # Create execution context
            context = engine.create_execution_context()
            
            # Allocate memory
            input_a_host = np.random.randint(-128, 128, (size, size), dtype=np.int8)
            input_b_host = np.random.randint(-128, 128, (size, size), dtype=np.int8)
            output_host = np.empty((size, size), dtype=np.int32)
            
            # Allocate GPU memory
            input_a_gpu = cuda.mem_alloc(input_a_host.nbytes)
            input_b_gpu = cuda.mem_alloc(input_b_host.nbytes)
            output_gpu = cuda.mem_alloc(output_host.nbytes)
            
            # Copy data to GPU
            cuda.memcpy_htod(input_a_gpu, input_a_host)
            cuda.memcpy_htod(input_b_gpu, input_b_host)
            
            # Run inference
            start_time = time.time()
            iterations = 0
            
            while time.time() - start_time < duration:
                context.execute_v2(bindings=[int(input_a_gpu), int(input_b_gpu), int(output_gpu)])
                iterations += 1
            
            elapsed = time.time() - start_time
            
            # Calculate TFLOPS
            flops_per_iter = 2 * size**3  # Matrix multiply FLOPs
            total_flops = flops_per_iter * iterations
            tflops = (total_flops / elapsed) / 1e12 if elapsed > 0 else 0
            
            return {
                "hardware_supported": True,
                "runtime_supported": True,
                "supported": True,
                "iterations": iterations,
                "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
                "dtype": "torch.int8",
                "tflops": tflops,
                "matrix_size": size,
                "method": "tensorrt"
            }
            
        except ImportError:
            return {
                "hardware_supported": True,
                "runtime_supported": False,
                "supported": False,
                "error": "TensorRT not installed. Install with: pip install gpu-benchmark-tool[nvidia]",
                "method": "tensorrt_missing",
                "solution": "Run: pip install gpu-benchmark-tool[nvidia]"
            }
        except Exception as e:
            error_msg = str(e)
            if "incompatible function arguments" in error_msg:
                error_msg = "TensorRT API version mismatch. Try updating TensorRT."
                solution = "Update TensorRT: pip install --upgrade tensorrt"
            elif "max_workspace_size" in error_msg:
                error_msg = "TensorRT version compatibility issue (workspace size API changed)."
                solution = "Update TensorRT: pip install --upgrade tensorrt"
            elif "build_engine" in error_msg:
                error_msg = "TensorRT version compatibility issue (build_engine API changed)."
                solution = "Update TensorRT: pip install --upgrade tensorrt"
            elif "dynamic range" in error_msg or "Q/DQ layers" in error_msg:
                error_msg = "TensorRT INT8 configuration issue (dynamic range not set)."
                solution = "This is a code issue - should be fixed in next version"
            elif "CUDA" in error_msg:
                error_msg = "CUDA/TensorRT compatibility issue."
                solution = "Check CUDA version compatibility with TensorRT"
            else:
                solution = "Check TensorRT installation and CUDA compatibility"
            
            return {
                "hardware_supported": True,
                "runtime_supported": False,
                "supported": False,
                "error": error_msg,
                "method": "tensorrt_failed",
                "solution": solution,
                "raw_error": str(e)
            }
    
    def tensor_core_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests Tensor Core performance if available.

        Args:
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, any]: Dictionary with tensor core availability, iterations, TFLOPS, and matrix size.
        """
        if self.device.type == "cpu":
            return {"tensor_cores_available": False}
            
        # Tensor cores require specific dimensions (multiples of 8)
        size = 4096
        
        # Check if tensor cores are available
        device_id = self.device.index if self.device.index is not None else 0
        major, _ = torch.cuda.get_device_capability(device_id)
        
        if major < 7:  # Tensor cores introduced in Volta (7.0)
            return {"tensor_cores_available": False}
        
        # Run with tensor core friendly dimensions
        torch.backends.cuda.matmul.allow_tf32 = True
        
        a = torch.randn((size, size), device=self.device, dtype=torch.float32)
        b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < duration:
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            iterations += 1
        
        elapsed = time.time() - start_time
        
        return {
            "tensor_cores_available": True,
            "iterations": iterations,
            "tflops": (2 * size**3 * iterations / elapsed) / 1e12,
            "matrix_size": size
        }
    
    def int8_quantization_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests INT8 quantization performance and accuracy.

        Args:
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, any]: Dictionary with INT8 support, performance metrics, and accuracy.
        """
        if self.device.type == "cpu":
            return {"int8_available": False}
            
        # Check INT8 support
        if not self._check_int8_support():
            return {"int8_available": False}
        
        size = 2048
        results = {}
        
        try:
            # Create FP32 tensors
            a_fp32 = torch.randn((size, size), device=self.device, dtype=torch.float32)
            b_fp32 = torch.randn((size, size), device=self.device, dtype=torch.float32)
            
            # Quantize to INT8
            scale_a = torch.max(torch.abs(a_fp32)) / 127.0
            scale_b = torch.max(torch.abs(b_fp32)) / 127.0
            
            a_int8 = torch.quantize_per_tensor(a_fp32, scale=scale_a, zero_point=0, dtype=torch.qint8)
            b_int8 = torch.quantize_per_tensor(b_fp32, scale=scale_b, zero_point=0, dtype=torch.qint8)
            
            # FP32 reference computation
            start_time = time.time()
            c_fp32 = torch.matmul(a_fp32, b_fp32)
            torch.cuda.synchronize()
            fp32_time = time.time() - start_time
            
            # INT8 computation
            start_time = time.time()
            c_int8 = torch.matmul(a_int8, b_int8)
            torch.cuda.synchronize()
            int8_time = time.time() - start_time
            
            # Dequantize INT8 result for comparison
            c_int8_dequant = c_int8.dequantize()
            
            # Calculate accuracy (relative error)
            relative_error = torch.mean(torch.abs(c_fp32 - c_int8_dequant) / torch.abs(c_fp32))
            
            # Calculate speedup
            speedup = fp32_time / int8_time if int8_time > 0 else 0
            
            # Calculate TFLOPS
            flops = 2 * size**3
            int8_tflops = (flops / int8_time) / 1e12 if int8_time > 0 else 0
            
            results = {
                "int8_available": True,
                "speedup_vs_fp32": speedup,
                "int8_tflops": int8_tflops,
                "relative_error": relative_error.item(),
                "matrix_size": size,
                "fp32_time": fp32_time,
                "int8_time": int8_time
            }
            
        except Exception as e:
            results = {
                "int8_available": False,
                "error": str(e)
            }
        
        return results
