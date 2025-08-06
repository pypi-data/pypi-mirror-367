from os import listdir

class AmbtEnv:
    KERNEL_FILES: set[str] = {"vmlinux", "vmlinux.bin", "vmlinuz", "bzImage"}
    BROWSER_FILES: set[str] = {"d8", "snapshot_blob.bin", "jsc"}

    USERSPACE: str = "linux_userspace"
    KERNEL: str = "linux_kernel"
    BROWSER: str = "browser"

def detect_environment(binary: str = "") -> str:
    dir_files = (binary,) if binary else listdir() 

    if AmbtEnv.KERNEL_FILES.intersection(dir_files):
        return AmbtEnv.KERNEL
    elif AmbtEnv.BROWSER_FILES.intersection(dir_files):
        return AmbtEnv.BROWSER
    else:
        return AmbtEnv.USERSPACE

def detect_architecture(binary: str):
	arch_byte = open(binary,"rb").read(0x13)[0x12]
	if arch_byte == 0x3e:
		return "amd64"
	elif arch_byte == 0x3:
		return "i386"
	else:
	    raise Exception("[AmbtRuntime] Unknown architecture")	
