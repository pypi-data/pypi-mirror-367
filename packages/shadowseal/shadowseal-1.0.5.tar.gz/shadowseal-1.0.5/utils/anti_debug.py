import os
import sys
import ctypes
import platform
import subprocess
import time
import threading
import random

# Optional psutil import - handle gracefully if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

def is_android():
    """Check if running on Android/Termux environment"""
    try:
        # Check for Android-specific indicators
        if os.path.exists("/system/build.prop") or os.path.exists("/system/bin/getprop"):
            return True
        if "TERMUX" in os.environ.get("PREFIX", ""):
            return True
        if "android" in platform.platform().lower():
            return True
        # Check for Android in uname
        try:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'android' in result.stdout.lower():
                return True
        except:
            pass
        return False
    except:
        return False

def check_ptrace():
    """Check for ptrace debugging - cross-platform compatible"""
    # Skip ptrace checks on Android/Termux to prevent false positives
    if is_android():
        return False
        
    system = platform.system()
    
    if system == "Linux" or system == "Darwin":  # Linux and macOS
        try:
            # Check if /proc/self/status exists (Linux only)
            if system == "Linux" and os.path.exists("/proc/self/status"):
                with open("/proc/self/status", "r") as f:
                    for line in f:
                        if line.startswith("TracerPid:"):
                            tracerpid = int(line.split()[1])
                            # On Android/Termux, ignore tracerpid as it may be misleading
                            return tracerpid != 0
            
            # macOS doesn't have /proc, so use alternative methods
            if system == "Darwin":
                # Use psutil to check for debuggers on macOS
                return check_debugger_processes()
                
        except (IOError, OSError, ValueError):
            pass
    
    elif system == "Windows":
        # Windows doesn't use ptrace, use process checking
        return check_debugger_processes()
    
    return False

def check_debugger_processes():
    """Check for known debugger processes"""
    # Skip aggressive process checking on Android/Termux
    if is_android():
        return False
    
    # Skip if psutil not available
    if not HAS_PSUTIL:
        return False
        
    debuggers = [
        'gdb', 'lldb', 'strace', 'ltrace', 'ida', 'ollydbg',
        'x64dbg', 'windbg', 'radare2', 'hopper', 'binaryninja',
        'frida', 'mitmproxy', 'burpsuite', 'wireshark'
    ]
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                for dbg in debuggers:
                    if dbg.lower() in proc_name or dbg.lower() in cmdline:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return False

def check_debugger_env():
    """Check for debugging environment variables"""
    # Allow common Termux/Android environment variables
    if is_android():
        debugger_vars = [
            'PYTHONBREAKPOINT', 'PYTHONINSPECT',
            'PYDEVD_LOAD_VALUES_ASYNC', 'PYDEVD_USE_FRAME_EVAL',
            'PYDEVD_USE_CYTHON', 'PYDEVD_DEBUG_FILE'
        ]
        # Allow LD_PRELOAD on Android as it's commonly used legitimately
    else:
        debugger_vars = [
            'LD_PRELOAD', 'PYTHONBREAKPOINT', 'PYTHONINSPECT',
            'PYDEVD_LOAD_VALUES_ASYNC', 'PYDEVD_USE_FRAME_EVAL',
            'PYDEVD_USE_CYTHON', 'PYDEVD_DEBUG_FILE'
        ]
    
    for var in debugger_vars:
        if os.environ.get(var):
            return True
    
    # Check for common debugging tools
    suspicious_env = any(
        'debug' in key.lower() or 'trace' in key.lower()
        for key in os.environ.keys()
    )
    return suspicious_env

def check_tracerpid():
    """Enhanced tracer PID check - cross-platform compatible"""
    # Skip tracerpid checks on Android/Termux
    if is_android():
        return False
        
    system = platform.system()
    
    if system == "Linux":
        try:
            # Check /proc/self/status (Linux only)
            if os.path.exists("/proc/self/status"):
                with open("/proc/self/status", "r") as f:
                    for line in f:
                        if line.startswith("TracerPid:"):
                            tracerpid = int(line.split()[1])
                            # On Android/Termux, ignore tracerpid as it may be misleading
                            if tracerpid != 0:
                                return True
            
            # Check /proc/self/stat (Linux only)
            if os.path.exists("/proc/self/stat"):
                with open("/proc/self/stat", "r") as f:
                    stat_fields = f.read().split()
                    # Check process state for tracing
                    if len(stat_fields) > 2 and stat_fields[2] == 't':
                        return True
                    
        except Exception:
            pass
    
    # For non-Linux systems, use alternative detection methods
    return check_debugger_processes()

def check_parent_process():
    """Check if parent process is a debugger"""
    # Skip parent process checks on Android/Termux
    if is_android():
        return False
    
    # Skip if psutil not available
    if not HAS_PSUTIL:
        return False
        
    try:
        parent = psutil.Process().parent()
        if parent:
            parent_name = parent.name().lower()
            debuggers = ['gdb', 'lldb', 'python', 'pycharm', 'vscode']
            return any(dbg in parent_name for dbg in debuggers)
    except Exception:
        pass
    return False

def check_sys_trace():
    """Check Python's tracing mechanism"""
    # Allow tracing on Android/Termux as it might be normal
    if is_android():
        return False
    return sys.gettrace() is not None

def check_time_anomaly():
    """Detect time-based debugging detection"""
    # Skip time anomaly checks on Android/Termux due to system variability
    if is_android():
        return False
        
    start = time.perf_counter()
    time.sleep(0.001)  # Small delay
    end = time.perf_counter()
    
    # If the delay is significantly longer, debugging might be present
    actual_delay = end - start
    expected_delay = 0.001
    
    return actual_delay > expected_delay * 10

def check_memory_anomaly():
    """Check for memory debugging patterns"""
    # Skip memory checks on Android/Termux
    if is_android():
        return False
        
    try:
        import gc
        gc.collect()
        objects = gc.get_objects()
        
        # Look for debugging-related objects
        debug_patterns = ['trace', 'debug', 'pdb', 'breakpoint']
        for obj in objects:
            obj_str = str(type(obj)).lower()
            if any(pattern in obj_str for pattern in debug_patterns):
                return True
    except Exception:
        pass
    return False

def check_cpu_anomaly():
    """Check CPU usage patterns for debugging"""
    # Skip CPU checks on Android/Termux due to system variability
    if is_android():
        return False
    
    # Skip if psutil not available
    if not HAS_PSUTIL:
        return False
        
    try:
        cpu_percent = psutil.Process().cpu_percent(interval=0.1)
        # Debuggers often cause higher CPU usage
        return cpu_percent > 50  # Arbitrary threshold
    except Exception:
        return False

def anti_debug():
    """Comprehensive anti-debugging detection"""
    # Completely skip anti-debug on Android/Termux to prevent false positives
    if is_android():
        return False
        
    # Simplified checks for non-Android platforms
    checks = [
        check_ptrace,
        check_debugger_env,
        check_sys_trace,
    ]
    
    for check in checks:
        try:
            if check():
                return True
        except Exception:
            continue
    
    return False

def anti_debug_with_delay():
    """Anti-debug with random delays to frustrate analysis"""
    if anti_debug():
        # Add random delay to frustrate timing attacks
        delay = random.uniform(1, 5)
        time.sleep(delay)
        return True
    
    return False

class AntiDebugContext:
    """Context manager for anti-debug protection"""
    def __enter__(self):
        if anti_debug():
            raise RuntimeError("Debugging detected")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Example usage
if __name__ == "__main__":
    if anti_debug():
        print("Debugging detected!")
        sys.exit(1)
    else:
        print("No debugging detected")
