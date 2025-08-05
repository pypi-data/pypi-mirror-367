import pyghidra

import typing
if typing.TYPE_CHECKING:
    from ghidra.ghidra_builtins import *
    from ghidra import *


def setup_decomplier(program: "ghidra.program.model.listing.Program") -> "ghidra.app.decompiler.DecompInterface":

    from ghidra.app.decompiler import DecompInterface
    from ghidra.app.decompiler import DecompileOptions

    prog_options = DecompileOptions()

    decomp = DecompInterface()

    # grab default options from program
    prog_options.grabFromProgram(program)

    # increase maxpayload size to 100MB (default 50MB)
    prog_options.setMaxPayloadMBytes(100)

    decomp.setOptions(prog_options)
    decomp.openProgram(program)

    return decomp


def get_filename(func: 'ghidra.program.model.listing.Function'):
    MAX_PATH_LEN = 12
    return f'{func.getName()[:MAX_PATH_LEN]}-{func.entryPoint}'


def decompile_func(func: 'ghidra.program.model.listing.Function',
                   decompiler: dict,
                   timeout: int = 0,
                   monitor=None) -> list:
    """
    Decompile function and return [funcname, decompilation]
    Ghidra/Features/Decompiler/src/main/java/ghidra/app/util/exporter/CppExporter.java#L514
    """
    from ghidra.util.task import ConsoleTaskMonitor
    from ghidra.app.decompiler import DecompiledFunction, DecompileResults

    if monitor is None:
        monitor = ConsoleTaskMonitor()

    result: "DecompileResults" = decompiler.decompileFunction(
        func, timeout, monitor)

    if '' == result.getErrorMessage():
        code = result.decompiledFunction.getC()
        sig = result.decompiledFunction.getSignature()
    else:
        code = result.getErrorMessage()
        sig = None

    return [get_filename(func), code, sig]
