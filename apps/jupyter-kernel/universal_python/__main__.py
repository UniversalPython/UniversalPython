from ipykernel.kernelapp import IPKernelApp
from . import UniversalPythonKernel

IPKernelApp.launch_instance(kernel_class=UniversalPythonKernel)
